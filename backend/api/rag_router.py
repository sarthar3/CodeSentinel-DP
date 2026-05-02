"""
FastAPI router for RAG endpoints with Server-Sent Events (SSE) streaming
Enhanced with Transformer support (DialoGPT + BERT)
"""
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
import json
import asyncio
from typing import AsyncGenerator, Optional
import os
from dotenv import load_dotenv

from .schemas import RAGQueryRequest, RAGQueryResponse, RAGSource
from ..rag.query import RAGQueryEngine
from ..rag.conversational_engine import ConversationalRAGEngine

load_dotenv()

router = APIRouter()

# Initialize RAG engines (singletons)
_rag_engine = None
_transformer_engine = None
_conversational_engine = None


def get_rag_engine() -> RAGQueryEngine:
    """Get or create standard RAG engine instance"""
    global _rag_engine
    if _rag_engine is None:
        _rag_engine = RAGQueryEngine()
    return _rag_engine


def get_transformer_engine():
    """Get or create transformer RAG engine instance"""
    global _transformer_engine
    if _transformer_engine is None:
        try:
            from ..rag.transformer_engine import TransformerRAGEngine
            _transformer_engine = TransformerRAGEngine()
        except Exception as e:
            print(f"⚠️ Transformer engine unavailable: {e}")
            return None
    return _transformer_engine


def get_conversational_engine():
    """Get or create conversational RAG engine instance"""
    global _conversational_engine
    if _conversational_engine is None:
        try:
            _conversational_engine = ConversationalRAGEngine()
        except Exception as e:
            print(f"⚠️ Conversational engine unavailable: {e}")
            return None
    return _conversational_engine


def get_groq_client():
    """Get Groq client using API key from environment"""
    from groq import Groq
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
    return Groq(api_key=api_key)


@router.post("/query", response_model=RAGQueryResponse)
async def query_rag(
    request: RAGQueryRequest,
    use_conversational: bool = Query(True, description="Use conversational engine (DialoGPT + BERT + Wikipedia)"),
    use_transformer: bool = Query(False, description="Use transformer engine (DialoGPT + BERT)")
):
    """
    Query the RAG system (non-streaming version)
    
    Args:
        request: RAG query request
        use_conversational: Use new conversational engine (default)
        use_transformer: Use transformer engine instead of Groq
        
    Returns:
        RAG query response with answer and sources
    """
    try:
        if use_conversational:
            # Use new conversational engine (preferred)
            conv_engine = get_conversational_engine()
            if conv_engine:
                result = conv_engine.chat(request.query)
                sources = [RAGSource(**source) for source in result["sources"]]
                answer = result["answer"]
                if "model" in result:
                    answer = f"[{result['model']}]\n\n{answer}"
                return RAGQueryResponse(
                    answer=answer,
                    sources=sources,
                    query=request.query
                )
        
        if use_transformer:
            # Try transformer engine
            transformer_engine = get_transformer_engine()
            if transformer_engine:
                result = transformer_engine.query(request.query, request.top_k, use_transformer=True)
            else:
                # Fallback to standard engine
                engine = get_rag_engine()
                result = engine.query(request.query, request.top_k)
        else:
            # Use standard Groq engine
            engine = get_rag_engine()
            result = engine.query(request.query, request.top_k)
        
        # Convert to response schema
        sources = [
            RAGSource(**source) for source in result["sources"]
        ]
        
        # Add model info to answer if available
        answer = result["answer"]
        if "model" in result:
            answer = f"[Model: {result['model']}]\n\n{answer}"
        
        return RAGQueryResponse(
            answer=answer,
            sources=sources,
            query=result["query"]
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/similar")
async def get_similar_documents(query: str, top_k: int = 3):
    """
    Get similar documents without generating an answer
    Used by Stage 4 (Triage) for finding similar incidents
    
    Args:
        query: Query text
        top_k: Number of results to return
        
    Returns:
        List of similar documents with metadata
    """
    try:
        engine = get_rag_engine()
        similar_docs = engine.retrieve_similar(query, top_k)
        
        return {
            "query": query,
            "results": similar_docs
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


async def stream_rag_response(query: str, top_k: int) -> AsyncGenerator[str, None]:
    """
    Stream RAG response using SSE
    
    Args:
        query: User query
        top_k: Number of context documents
        
    Yields:
        SSE events with streaming response
    """
    try:
        engine = get_rag_engine()
        
        # First, retrieve similar documents
        yield json.dumps({
            "type": "status",
            "message": "Retrieving similar documents..."
        }) + "\n\n"
        
        similar_docs = engine.retrieve_similar(query, top_k)
        
        # Filter by relevance threshold
        relevant_docs = [doc for doc in similar_docs if doc['relevance_score'] > engine.RELEVANCE_THRESHOLD]
        print(f"DEBUG: Found {len(similar_docs)} similar docs, {len(relevant_docs)} relevant (Threshold: {engine.RELEVANCE_THRESHOLD})")
        for d in similar_docs:
            print(f"DEBUG: Score {d['relevance_score']} for {d['source']}")
        
        # Send sources (only relevant ones or all found?)
        # Let's send all found to show the user what was explored, 
        # but the LLM will only use the relevant ones.
        yield json.dumps({
            "type": "sources",
            "data": similar_docs
        }) + "\n\n"
        
        if not relevant_docs:
            yield json.dumps({
                "type": "status",
                "message": "No relevant documentation found. Generating general response..."
            }) + "\n\n"
            
            # Fallback to general Groq response
            from groq import Groq
            groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
            
            stream = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant. Provide accurate, concise answers."},
                    {"role": "user", "content": query}
                ],
                temperature=0.7,
                max_tokens=512,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield json.dumps({
                        "type": "token",
                        "data": chunk.choices[0].delta.content
                    }) + "\n\n"
            
            yield json.dumps({"type": "done"}) + "\n\n"
            return
        
        # Generate answer with streaming using relevant docs
        yield json.dumps({
            "type": "status",
            "message": "Generating answer..."
        }) + "\n\n"
        
        # Build context
        context_parts = []
        for doc in relevant_docs:
            context_parts.append(
                f"[SOURCE: {doc['source']}, page {doc['page']}]\n{doc['excerpt']}\n"
            )
        context_str = "\n---\n".join(context_parts)
        
        user_prompt = f"""Context documents:
{context_str}

Question: {query}

Provide a detailed answer using ONLY the context above. You MUST cite sources as [SOURCE: filename, page X] after every claim."""
        
        # Stream from Groq
        from groq import Groq
        groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        stream = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": engine.system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
            max_tokens=1024,
            stream=True
        )
        
        # Stream tokens
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield json.dumps({
                    "type": "token",
                    "data": chunk.choices[0].delta.content
                }) + "\n\n"
                await asyncio.sleep(0)
        
        # Send completion
        yield json.dumps({"type": "done"}) + "\n\n"
    
    except Exception as e:
        yield json.dumps({
            "type": "error",
            "message": str(e)
        }) + "\n\n"


@router.get("/query/stream")
async def query_rag_stream(
    query: str,
    top_k: int = 3,
    use_transformer: bool = Query(False, description="Use transformer engine")
):
    """
    Query the RAG system with SSE streaming
    
    Args:
        query: Query text
        top_k: Number of context documents
        use_transformer: Use transformer engine instead of Groq
        
    Returns:
        SSE stream with answer and sources
    """
    if use_transformer:
        return EventSourceResponse(stream_transformer_response(query, top_k))
    return EventSourceResponse(stream_rag_response(query, top_k))


async def stream_transformer_response(query: str, top_k: int) -> AsyncGenerator[str, None]:
    """
    Stream transformer RAG response using SSE
    
    Args:
        query: User query
        top_k: Number of context documents
        
    Yields:
        SSE events with streaming response
    """
    try:
        transformer_engine = get_transformer_engine()
        
        if not transformer_engine:
            yield json.dumps({
                "type": "error",
                "message": "Transformer engine not available. Install dependencies: pip install torch transformers"
            }) + "\n\n"
            return
        
        # Retrieve similar documents
        yield json.dumps({
            "type": "status",
            "message": "Retrieving similar documents with BERT embeddings..."
        }) + "\n\n"
        
        similar_docs = transformer_engine.retrieve_similar(query, top_k)
        
        # Filter by relevance
        relevant_docs = [doc for doc in similar_docs if doc['relevance_score'] > 0.5]
        
        # Send sources (all found, but mark relevance)
        yield json.dumps({
            "type": "sources",
            "data": similar_docs
        }) + "\n\n"
        
        # Generate with DialoGPT
        yield json.dumps({
            "type": "status",
            "message": "Generating answer with DialoGPT..."
        }) + "\n\n"
        
        result = transformer_engine.query(query, top_k, use_transformer=True)
        
        # Stream answer word by word for effect
        words = result["answer"].split()
        for word in words:
            yield json.dumps({
                "type": "token",
                "data": word + " "
            }) + "\n\n"
            await asyncio.sleep(0.05)  # Simulate streaming
        
        # Send model info
        yield json.dumps({
            "type": "info",
            "data": f"Model: {result.get('model', 'Unknown')}"
        }) + "\n\n"
        
        # Send completion
        yield json.dumps({"type": "done"}) + "\n\n"
    
    except Exception as e:
        yield json.dumps({
            "type": "error",
            "message": str(e)
        }) + "\n\n"


@router.get("/health")
async def health_check():
    """Check if RAG system is initialized"""
    try:
        engine = get_rag_engine()
        doc_count = engine.collection.count()
        
        # Check transformer availability
        transformer_available = get_transformer_engine() is not None
        
        return {
            "status": "healthy",
            "documents": doc_count,
            "transformer_available": transformer_available,
            "models": {
                "groq": "llama-3.3-70b-versatile",
                "transformer": "DialoGPT + BERT (mpnet)" if transformer_available else "Not available"
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@router.post("/enrich/wikipedia")
async def enrich_with_wikipedia(topics: list[str]):
    """
    Enrich knowledge base with Wikipedia articles
    
    Args:
        topics: List of Wikipedia topics to add
        
    Returns:
        Enrichment summary
    """
    try:
        from ..rag.wikipedia_enrichment import WikipediaEnricher
        
        enricher = WikipediaEnricher()
        result = enricher.enrich_knowledge_base(topics)
        
        return {
            "status": "success",
            "added": result["added"],
            "failed": result["failed"],
            "total": result["total"]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Enrichment failed: {str(e)}")


@router.get("/reset-conversation")
async def reset_conversation():
    """Reset conversation history for all engines"""
    try:
        reset_count = 0
        
        # Reset conversational engine
        conv_engine = get_conversational_engine()
        if conv_engine:
            conv_engine.reset_conversation()
            reset_count += 1
        
        # Reset transformer engine
        transformer_engine = get_transformer_engine()
        if transformer_engine:
            transformer_engine.reset_conversation()
            reset_count += 1
        
        if reset_count > 0:
            return {"status": "success", "message": f"Conversation history reset ({reset_count} engines)"}
        return {"status": "error", "message": "No conversation engines available"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Made with Bob

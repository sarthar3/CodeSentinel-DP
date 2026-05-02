"""
RAG Query Engine
Retrieves relevant documents and generates answers with strict citations
"""
import os
from typing import List, Dict, Optional
import chromadb
from sentence_transformers import SentenceTransformer
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


class RAGQueryEngine:
    """Handles RAG queries with citation enforcement"""
    
    RELEVANCE_THRESHOLD = 0.5
    
    def __init__(self, persist_dir: Optional[str] = None):
        """
        Initialize the RAG query engine
        
        Args:
            persist_dir: Directory where ChromaDB data is persisted
        """
        self.persist_dir = persist_dir or os.getenv("CHROMA_PERSIST_DIR", "./data/chroma")
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=self.persist_dir)
        
        # Get collection
        try:
            self.collection = self.client.get_collection(name="legacy_docs")
        except Exception:
            raise ValueError(
                "Collection 'legacy_docs' not found. "
                "Please run ingest.py first to populate the knowledge base."
            )
        
        # Initialize embedding model (all-mpnet-base-v2 for 768-dim embeddings)
        # Matching the collection dimensionality from ingest.py
        self.embedding_model = SentenceTransformer('all-mpnet-base-v2')
        
        # Initialize Groq client
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        self.groq_client = Groq(api_key=api_key)
        
        # Citation-enforcing system prompt
        self.system_prompt = """You are a technical documentation assistant that MUST cite sources.

CRITICAL RULES:
1. You MUST cite sources as [SOURCE: filename, page X] after EVERY claim or fact
2. If the answer is not in the provided context, respond EXACTLY: "ANSWER NOT FOUND IN KNOWLEDGE BASE"
3. Never make up information or hallucinate
4. Use only the provided context documents
5. Be concise and technical

Example response format:
"The database timeout issue was caused by connection pool exhaustion [SOURCE: incident-2019-03.pdf, page 2]. 
The fix involved increasing max_connections to 200 [SOURCE: runbook-db.md, page 5]."
"""
    
    def retrieve_similar(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Retrieve similar documents from ChromaDB
        
        Args:
            query: User query text
            top_k: Number of results to return
            
        Returns:
            List of similar documents with metadata
        """
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])[0]
        
        # Query ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
        
        # Format results
        similar_docs = []
        for i in range(len(results['documents'][0])):
            # Convert distance to relevance score (1 - normalized distance)
            distance = results['distances'][0][i]
            relevance_score = max(0.0, 1.0 - (distance / 2.0))  # Normalize to 0-1
            
            similar_docs.append({
                "source": results['metadatas'][0][i]['source'],
                "page": results['metadatas'][0][i]['page'],
                "excerpt": results['documents'][0][i][:500],  # First 500 chars
                "relevance_score": round(relevance_score, 3)
            })
        
        return similar_docs
    
    def generate_answer(self, query: str, context_docs: List[Dict]) -> str:
        """
        Generate answer using Groq with citation enforcement
        
        Args:
            query: User query
            context_docs: Retrieved context documents
            
        Returns:
            Generated answer with citations
        """
        # Build context string with source information
        context_parts = []
        for doc in context_docs:
            context_parts.append(
                f"[SOURCE: {doc['source']}, page {doc['page']}]\n{doc['excerpt']}\n"
            )
        context_str = "\n---\n".join(context_parts)
        
        # Build user prompt
        user_prompt = f"""Context documents:
{context_str}

Question: {query}

Provide a detailed answer using ONLY the context above. You MUST cite sources as [SOURCE: filename, page X] after every claim."""
        
        # Call Groq API (non-streaming for simplicity in this version)
        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,  # Low temperature for factual responses
                max_tokens=1024
            )
            
            answer = response.choices[0].message.content
            return answer
            
        except Exception as e:
            return f"Error generating answer: {str(e)}"
    
    def query(self, query: str, top_k: int = 3, fallback_to_general: bool = True) -> Dict:
        """
        Complete RAG query pipeline with fallback to general knowledge
        
        Args:
            query: User query
            top_k: Number of context documents to retrieve
            fallback_to_general: If True, answer general questions when no docs found
            
        Returns:
            Dictionary with answer and sources
        """
        # Retrieve similar documents
        similar_docs = self.retrieve_similar(query, top_k)
        
        # Check if we have relevant documents (relevance score > RELEVANCE_THRESHOLD for better filtering)
        relevant_docs = [doc for doc in similar_docs if doc['relevance_score'] > self.RELEVANCE_THRESHOLD]
        
        if not relevant_docs and fallback_to_general:
            # Answer general question without RAG
            answer = self._answer_general_question(query)
            return {
                "answer": answer,
                "sources": [],
                "query": query,
                "type": "general"
            }
        elif not relevant_docs:
            return {
                "answer": "ANSWER NOT FOUND IN KNOWLEDGE BASE",
                "sources": [],
                "query": query,
                "type": "not_found"
            }
        
        # Generate answer with RAG
        answer = self.generate_answer(query, relevant_docs)
        
        return {
            "answer": answer,
            "sources": relevant_docs,
            "query": query,
            "type": "rag"
        }
    
    def _answer_general_question(self, query: str) -> str:
        """
        Answer general questions without RAG context
        
        Args:
            query: User query
            
        Returns:
            Generated answer
        """
        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant. Provide accurate, concise answers to questions."},
                    {"role": "user", "content": query}
                ],
                temperature=0.7,
                max_tokens=512
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}"


def main():
    """CLI entry point for testing queries"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Query the RAG system")
    parser.add_argument("query", help="Query text")
    parser.add_argument("--top-k", type=int, default=3, help="Number of results")
    
    args = parser.parse_args()
    
    engine = RAGQueryEngine()
    result = engine.query(args.query, args.top_k)
    
    print("\n" + "="*80)
    print("ANSWER:")
    print("="*80)
    print(result["answer"])
    print("\n" + "="*80)
    print("SOURCES:")
    print("="*80)
    for source in result["sources"]:
        print(f"- {source['source']}, page {source['page']} (relevance: {source['relevance_score']})")


if __name__ == "__main__":
    main()

# Made with Bob

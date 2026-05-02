"""
Enhanced RAG Engine with Transformers
Uses DialoGPT for generation + BERT for embeddings
"""
import os
import torch
from typing import List, Dict, Optional
from transformers import AutoTokenizer, AutoModelForCausalLM, AutoModel
from sentence_transformers import SentenceTransformer
import chromadb
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


class TransformerRAGEngine:
    """
    Enhanced RAG engine using transformers:
    - BERT (bert-base-uncased) for better embeddings
    - DialoGPT (microsoft/DialoGPT-medium) for conversational generation
    - Groq as fallback for complex queries
    """
    
    def __init__(self, persist_dir: Optional[str] = None, use_gpu: bool = False):
        """
        Initialize transformer-based RAG engine
        
        Args:
            persist_dir: ChromaDB persistence directory
            use_gpu: Use GPU if available (default: False for CPU)
        """
        self.device = "cuda" if use_gpu and torch.cuda.is_available() else "cpu"
        print(f"🚀 Initializing TransformerRAGEngine on {self.device}")
        
        # Initialize ChromaDB
        self.persist_dir = persist_dir or os.getenv("CHROMA_PERSIST_DIR", "./backend/data/chroma")
        self.client = chromadb.PersistentClient(path=self.persist_dir)
        
        try:
            self.collection = self.client.get_collection(name="legacy_docs")
        except Exception:
            raise ValueError("Collection 'legacy_docs' not found. Run ingest.py first.")
        
        # Initialize MPNET embeddings (768-dim to match collection)
        print("📦 Loading BERT embeddings model (all-mpnet-base-v2)...")
        self.embedding_model = SentenceTransformer('all-mpnet-base-v2')
        
        # Initialize DialoGPT for conversational responses
        print("🤖 Loading DialoGPT conversational model...")
        self.dialog_tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
        self.dialog_model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")
        self.dialog_model.to(self.device)
        self.dialog_model.eval()  # Set to evaluation mode
        
        # Initialize Groq as fallback
        groq_key = os.getenv("GROQ_API_KEY")
        self.groq_client = Groq(api_key=groq_key) if groq_key else None
        
        # Conversation history for DialoGPT
        self.chat_history_ids = None
        
        print("✅ TransformerRAGEngine initialized successfully!")
    
    def retrieve_similar(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Retrieve similar documents using better BERT embeddings
        
        Args:
            query: User query
            top_k: Number of results
            
        Returns:
            List of similar documents with metadata
        """
        # Generate query embedding with better BERT model
        query_embedding = self.embedding_model.encode([query])[0]
        
        # Query ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
        
        # Format results with improved relevance scoring
        similar_docs = []
        if results['documents'] and results['documents'][0]:
            for i in range(len(results['documents'][0])):
                distance = results['distances'][0][i] if results['distances'] else 1.0
                # Better relevance calculation for mpnet embeddings
                relevance_score = max(0.0, 1.0 - (distance / 1.5))
                
                metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                similar_docs.append({
                    "source": metadata.get('source', 'unknown'),
                    "page": metadata.get('page', 0),
                    "excerpt": results['documents'][0][i][:500],
                    "relevance_score": round(relevance_score, 3)
                })
        
        return similar_docs
    
    def generate_with_dialogpt(self, query: str, context: str = "") -> str:
        """
        Generate response using DialoGPT transformer
        
        Args:
            query: User query
            context: Optional context from RAG
            
        Returns:
            Generated response
        """
        try:
            # Prepare input with context
            if context:
                input_text = f"Context: {context}\n\nQuestion: {query}\n\nAnswer:"
            else:
                input_text = query
            
            # Tokenize input
            new_input_ids = self.dialog_tokenizer.encode(
                input_text + self.dialog_tokenizer.eos_token,
                return_tensors='pt'
            ).to(self.device)
            
            # Append to chat history if exists
            if self.chat_history_ids is not None:
                bot_input_ids = torch.cat([self.chat_history_ids, new_input_ids], dim=-1)
            else:
                bot_input_ids = new_input_ids
            
            # Generate response
            with torch.no_grad():
                self.chat_history_ids = self.dialog_model.generate(
                    bot_input_ids,
                    max_length=1000,
                    pad_token_id=self.dialog_tokenizer.eos_token_id,
                    temperature=0.7,
                    top_p=0.9,
                    do_sample=True
                )
            
            # Decode response
            response = self.dialog_tokenizer.decode(
                self.chat_history_ids[:, bot_input_ids.shape[-1]:][0],
                skip_special_tokens=True
            )
            
            return response.strip()
            
        except Exception as e:
            print(f"⚠️ DialoGPT generation failed: {e}")
            return ""
    
    def generate_with_groq(self, query: str, context_docs: List[Dict]) -> str:
        """
        Generate response using Groq (fallback)
        
        Args:
            query: User query
            context_docs: Retrieved documents
            
        Returns:
            Generated answer
        """
        if not self.groq_client:
            return "Groq API not available. Please configure GROQ_API_KEY."
        
        # Build context
        context_parts = []
        for doc in context_docs:
            context_parts.append(
                f"[SOURCE: {doc['source']}, page {doc['page']}]\n{doc['excerpt']}\n"
            )
        context_str = "\n---\n".join(context_parts)
        
        # Generate with Groq
        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a helpful technical assistant. Provide accurate answers with source citations."},
                    {"role": "user", "content": f"Context:\n{context_str}\n\nQuestion: {query}\n\nAnswer:"}
                ],
                temperature=0.3,
                max_tokens=512
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error with Groq: {str(e)}"
    
    def query(self, query: str, top_k: int = 3, use_transformer: bool = True) -> Dict:
        """
        Complete RAG query with transformer generation
        
        Args:
            query: User query
            top_k: Number of context documents
            use_transformer: Use DialoGPT (True) or Groq (False)
            
        Returns:
            Dictionary with answer and sources
        """
        # Retrieve similar documents with better embeddings
        similar_docs = self.retrieve_similar(query, top_k)
        
        # Filter by relevance (threshold 0.5)
        relevant_docs = [doc for doc in similar_docs if doc['relevance_score'] > 0.5]
        
        if not relevant_docs:
            # No relevant docs - use general conversation
            if use_transformer:
                answer = self.generate_with_dialogpt(query)
                if answer:
                    return {
                        "answer": answer,
                        "sources": [],
                        "query": query,
                        "type": "transformer_general",
                        "model": "DialoGPT"
                    }
            
            # Fallback to Groq for general questions
            if self.groq_client:
                try:
                    response = self.groq_client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content": "You are a helpful AI assistant."},
                            {"role": "user", "content": query}
                        ],
                        temperature=0.7,
                        max_tokens=512
                    )
                    return {
                        "answer": response.choices[0].message.content,
                        "sources": [],
                        "query": query,
                        "type": "groq_general",
                        "model": "Groq Llama 3.3"
                    }
                except Exception:
                    pass
            
            return {
                "answer": "ANSWER NOT FOUND IN KNOWLEDGE BASE",
                "sources": [],
                "query": query,
                "type": "not_found"
            }
        
        # Generate answer with RAG context
        context = "\n".join([doc['excerpt'] for doc in relevant_docs])
        
        if use_transformer:
            # Try DialoGPT first
            answer = self.generate_with_dialogpt(query, context)
            if answer and len(answer) > 10:  # Valid response
                return {
                    "answer": answer,
                    "sources": relevant_docs,
                    "query": query,
                    "type": "transformer_rag",
                    "model": "DialoGPT + BERT"
                }
        
        # Fallback to Groq
        answer = self.generate_with_groq(query, relevant_docs)
        return {
            "answer": answer,
            "sources": relevant_docs,
            "query": query,
            "type": "groq_rag",
            "model": "Groq Llama 3.3"
        }
    
    def reset_conversation(self):
        """Reset DialoGPT conversation history"""
        self.chat_history_ids = None
        print("🔄 Conversation history reset")


# Made with Bob

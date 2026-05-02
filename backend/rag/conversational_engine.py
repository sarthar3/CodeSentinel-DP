"""
Enhanced Conversational RAG Engine
Combines DialoGPT, BERT embeddings, and Wikipedia knowledge
"""
import os
import torch
import re
from typing import List, Dict, Optional, Tuple
from transformers import AutoTokenizer, AutoModelForCausalLM
from sentence_transformers import SentenceTransformer
import chromadb
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


class ConversationalRAGEngine:
    """
    Advanced conversational AI with RAG capabilities
    - DialoGPT for natural conversations
    - BERT (mpnet) for semantic search
    - Wikipedia knowledge base
    - Context-aware responses
    """
    
    def __init__(self, persist_dir: Optional[str] = None, use_gpu: bool = False):
        """
        Initialize conversational RAG engine
        
        Args:
            persist_dir: ChromaDB persistence directory
            use_gpu: Use GPU if available
        """
        self.device = "cuda" if use_gpu and torch.cuda.is_available() else "cpu"
        print(f"🚀 Initializing Conversational RAG Engine on {self.device}")
        
        # Initialize ChromaDB
        self.persist_dir = persist_dir or os.getenv("CHROMA_PERSIST_DIR", "./backend/data/chroma")
        self.client = chromadb.PersistentClient(path=self.persist_dir)
        
        try:
            self.collection = self.client.get_collection(name="legacy_docs")
            doc_count = self.collection.count()
            print(f"📚 Knowledge base loaded: {doc_count} documents")
        except Exception as e:
            print(f"⚠️  No knowledge base found. Run wikipedia_ingest.py first.")
            self.collection = None
        
        # Initialize BERT embeddings (all-mpnet-base-v2)
        print("📦 Loading BERT embedding model...")
        self.embedding_model = SentenceTransformer('all-mpnet-base-v2')
        
        # Initialize DialoGPT for conversations
        print("🤖 Loading DialoGPT conversational model...")
        self.dialog_tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
        self.dialog_model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")
        self.dialog_model.to(self.device)
        self.dialog_model.eval()
        
        # Conversation history
        self.chat_history_ids = None
        self.conversation_context = []
        
        # Initialize Groq as fallback
        groq_key = os.getenv("GROQ_API_KEY")
        self.groq_client = Groq(api_key=groq_key) if groq_key else None
        
        print("✅ Conversational RAG Engine ready!")
    
    def retrieve_knowledge(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Retrieve relevant knowledge from Wikipedia-based knowledge base
        
        Args:
            query: User query
            top_k: Number of results
            
        Returns:
            List of relevant documents
        """
        if not self.collection:
            return []
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])[0]
        
        # Query ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
        
        # Format results
        knowledge = []
        if results['documents'] and results['documents'][0]:
            for i in range(len(results['documents'][0])):
                distance = results['distances'][0][i] if results['distances'] else 1.0
                relevance_score = max(0.0, 1.0 - (distance / 1.5))
                
                metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                knowledge.append({
                    "source": metadata.get('source', 'Unknown'),
                    "section": metadata.get('section', 'N/A'),
                    "url": metadata.get('url', ''),
                    "excerpt": results['documents'][0][i][:600],
                    "relevance_score": round(relevance_score, 3)
                })
        
        return knowledge
    
    def generate_response(
        self,
        query: str,
        use_knowledge: bool = True,
        max_length: int = 150
    ) -> Dict:
        """
        Generate conversational response with optional knowledge augmentation
        
        Args:
            query: User query
            use_knowledge: Whether to use RAG knowledge
            max_length: Maximum response length
            
        Returns:
            Response dictionary with answer and sources
        """
        # Retrieve knowledge if requested
        knowledge = []
        if use_knowledge and self.collection:
            knowledge = self.retrieve_knowledge(query, top_k=3)
            # Filter by relevance
            knowledge = [k for k in knowledge if k['relevance_score'] > 0.4]
        
        # Build context from knowledge
        context = ""
        if knowledge:
            context_parts = []
            for k in knowledge[:2]:  # Use top 2 sources
                context_parts.append(f"{k['excerpt'][:300]}")
            context = " ".join(context_parts)
        
        # Prepare input for DialoGPT
        if context:
            input_text = f"Context: {context}\n\nUser: {query}\nAssistant:"
        else:
            input_text = f"User: {query}\nAssistant:"
        
        # Generate with DialoGPT
        try:
            new_input_ids = self.dialog_tokenizer.encode(
                input_text + self.dialog_tokenizer.eos_token,
                return_tensors='pt',
                truncation=True,
                max_length=512
            ).to(self.device)
            
            # Append to chat history
            if self.chat_history_ids is not None:
                bot_input_ids = torch.cat([self.chat_history_ids, new_input_ids], dim=-1)
                # Limit history length
                if bot_input_ids.shape[-1] > 800:
                    bot_input_ids = bot_input_ids[:, -800:]
            else:
                bot_input_ids = new_input_ids
            
            # Generate response
            with torch.no_grad():
                self.chat_history_ids = self.dialog_model.generate(
                    bot_input_ids,
                    max_length=bot_input_ids.shape[-1] + max_length,
                    pad_token_id=self.dialog_tokenizer.eos_token_id,
                    temperature=0.8,
                    top_p=0.9,
                    top_k=50,
                    do_sample=True,
                    no_repeat_ngram_size=3
                )
            
            # Decode response
            response = self.dialog_tokenizer.decode(
                self.chat_history_ids[:, bot_input_ids.shape[-1]:][0],
                skip_special_tokens=True
            )
            
            # Clean up response
            response = response.strip()
            if not response or len(response) < 5:
                # Fallback to Groq if DialoGPT fails
                response = self._fallback_to_groq(query, knowledge)
            
            return {
                "answer": response,
                "sources": knowledge,
                "model": "DialoGPT + BERT",
                "has_knowledge": len(knowledge) > 0
            }
            
        except Exception as e:
            print(f"⚠️  DialoGPT error: {e}")
            # Fallback to Groq
            response = self._fallback_to_groq(query, knowledge)
            return {
                "answer": response,
                "sources": knowledge,
                "model": "Groq (fallback)",
                "has_knowledge": len(knowledge) > 0
            }
    
    def _fallback_to_groq(self, query: str, knowledge: List[Dict]) -> str:
        """
        Fallback to Groq when DialoGPT fails
        
        Args:
            query: User query
            knowledge: Retrieved knowledge
            
        Returns:
            Generated response
        """
        if not self.groq_client:
            return "I apologize, but I'm having trouble generating a response right now."
        
        try:
            # Build context
            context = ""
            if knowledge:
                context = "\n".join([k['excerpt'][:300] for k in knowledge[:2]])
            
            messages = [
                {"role": "system", "content": "You are a helpful AI assistant with knowledge from Wikipedia. Provide clear, accurate answers."}
            ]
            
            if context:
                messages.append({"role": "user", "content": f"Context: {context}\n\nQuestion: {query}"})
            else:
                messages.append({"role": "user", "content": query})
            
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.7,
                max_tokens=300
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}"
    
    def chat(self, message: str) -> Dict:
        """
        Main chat interface
        
        Args:
            message: User message
            
        Returns:
            Response dictionary
        """
        # Add to conversation context
        self.conversation_context.append({"role": "user", "content": message})
        
        # Generate response
        response = self.generate_response(message, use_knowledge=True)
        
        # Add to conversation context
        self.conversation_context.append({"role": "assistant", "content": response["answer"]})
        
        # Limit context length
        if len(self.conversation_context) > 10:
            self.conversation_context = self.conversation_context[-10:]
        
        return response
    
    def reset_conversation(self):
        """Reset conversation history"""
        self.chat_history_ids = None
        self.conversation_context = []
        print("🔄 Conversation reset")
    
    def get_conversation_history(self) -> List[Dict]:
        """Get conversation history"""
        return self.conversation_context


# Made with Bob

"""
Clean Wikipedia-Based Knowledge Ingestion
Builds RAG knowledge base from scratch using only Wikipedia
"""
import os
import re
from pathlib import Path
from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import wikipediaapi
import torch
from dotenv import load_dotenv

load_dotenv()


class WikipediaKnowledgeBuilder:
    """
    Builds a clean knowledge base from Wikipedia articles
    Uses transformers for embeddings and RAG
    """
    
    def __init__(self, persist_dir: Optional[str] = None):
        """
        Initialize Wikipedia knowledge builder
        
        Args:
            persist_dir: Directory to persist ChromaDB data
        """
        self.persist_dir = persist_dir or os.getenv("CHROMA_PERSIST_DIR", "./backend/data/chroma")
        
        # Ensure persist directory exists
        Path(self.persist_dir).mkdir(parents=True, exist_ok=True)
        
        print("🌐 Initializing Wikipedia Knowledge Builder...")
        
        # Initialize Wikipedia API
        self.wiki = wikipediaapi.Wikipedia(
            language='en',
            user_agent='CodeSentinel/2.0 (Educational RAG System)'
        )
        
        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(path=self.persist_dir)
        
        # Delete old collection if exists
        try:
            self.client.delete_collection(name="legacy_docs")
            print("🗑️  Deleted old knowledge base")
        except Exception:
            pass
        
        # Create fresh collection
        self.collection = self.client.create_collection(
            name="legacy_docs",
            metadata={"description": "Wikipedia-based knowledge for conversational AI"}
        )
        
        # Initialize better embedding model (all-mpnet-base-v2)
        print("📦 Loading BERT embedding model (all-mpnet-base-v2)...")
        self.embedding_model = SentenceTransformer('all-mpnet-base-v2')
        
        print("✅ Wikipedia Knowledge Builder initialized!")
    
    def fetch_wikipedia_article(self, title: str) -> Optional[Dict]:
        """
        Fetch a Wikipedia article with sections
        
        Args:
            title: Wikipedia article title
            
        Returns:
            Article data with sections
        """
        try:
            page = self.wiki.page(title)
            
            if not page.exists():
                print(f"⚠️  Article not found: {title}")
                return None
            
            # Extract sections
            sections = []
            for section in page.sections:
                if len(section.text) > 100:  # Skip very short sections
                    sections.append({
                        "title": section.title,
                        "text": section.text[:2000]  # Limit section length
                    })
            
            return {
                "title": page.title,
                "summary": page.summary,
                "url": page.fullurl,
                "sections": sections,
                "full_text": page.text[:10000]  # First 10k chars
            }
            
        except Exception as e:
            print(f"❌ Error fetching '{title}': {e}")
            return None
    
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """
        Split text into overlapping chunks for better retrieval
        
        Args:
            text: Text to chunk
            chunk_size: Size of each chunk in words
            overlap: Overlap between chunks in words
            
        Returns:
            List of text chunks
        """
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if len(chunk.strip()) > 50:  # Skip very short chunks
                chunks.append(chunk)
        
        return chunks
    
    def ingest_article(self, title: str) -> int:
        """
        Ingest a single Wikipedia article into knowledge base
        
        Args:
            title: Wikipedia article title
            
        Returns:
            Number of chunks added
        """
        article = self.fetch_wikipedia_article(title)
        
        if not article:
            return 0
        
        chunks_added = 0
        
        # Add summary as a chunk
        summary_embedding = self.embedding_model.encode([article['summary']])[0]
        
        self.collection.add(
            documents=[article['summary']],
            embeddings=[summary_embedding.tolist()],
            metadatas=[{
                "source": f"Wikipedia: {article['title']}",
                "page": 0,
                "url": article['url'],
                "type": "wikipedia_summary",
                "section": "Summary"
            }],
            ids=[f"wiki_{article['title'].replace(' ', '_')}_summary"]
        )
        chunks_added += 1
        
        # Add sections as chunks
        for idx, section in enumerate(article['sections']):
            # Chunk section text
            section_chunks = self.chunk_text(section['text'], chunk_size=400, overlap=50)
            
            for chunk_idx, chunk in enumerate(section_chunks):
                embedding = self.embedding_model.encode([chunk])[0]
                
                chunk_id = f"wiki_{article['title'].replace(' ', '_')}_sec{idx}_chunk{chunk_idx}"
                
                self.collection.add(
                    documents=[chunk],
                    embeddings=[embedding.tolist()],
                    metadatas=[{
                        "source": f"Wikipedia: {article['title']}",
                        "page": idx + 1,
                        "url": article['url'],
                        "type": "wikipedia_section",
                        "section": section['title']
                    }],
                    ids=[chunk_id]
                )
                chunks_added += 1
        
        print(f"✅ Ingested: {article['title']} ({chunks_added} chunks)")
        return chunks_added
    
    def build_knowledge_base(self, topics: List[str]) -> Dict:
        """
        Build complete knowledge base from Wikipedia topics
        
        Args:
            topics: List of Wikipedia article titles
            
        Returns:
            Summary of ingestion
        """
        total_chunks = 0
        successful = 0
        failed = 0
        
        print(f"\n🚀 Building knowledge base from {len(topics)} Wikipedia articles...\n")
        
        for topic in topics:
            chunks = self.ingest_article(topic)
            if chunks > 0:
                total_chunks += chunks
                successful += 1
            else:
                failed += 1
        
        print(f"\n📊 Knowledge Base Built:")
        print(f"   ✅ Successful: {successful} articles")
        print(f"   ❌ Failed: {failed} articles")
        print(f"   📦 Total chunks: {total_chunks}")
        
        return {
            "successful": successful,
            "failed": failed,
            "total_chunks": total_chunks,
            "total_articles": len(topics)
        }


# Comprehensive technical topics for software engineering knowledge base
TECHNICAL_TOPICS = [
    # Programming Languages
    "Python (programming language)",
    "JavaScript",
    "TypeScript",
    "Java (programming language)",
    "C++",
    "Go (programming language)",
    "Rust (programming language)",
    
    # Web Development
    "React (software)",
    "FastAPI",
    "Node.js",
    "REST",
    "GraphQL",
    "WebSocket",
    
    # Backend & Databases
    "Database",
    "SQL",
    "PostgreSQL",
    "MongoDB",
    "Redis",
    "Database normalization",
    
    # DevOps & Cloud
    "Docker (software)",
    "Kubernetes",
    "Continuous integration",
    "Continuous deployment",
    "Amazon Web Services",
    "Microsoft Azure",
    
    # Software Engineering
    "Software engineering",
    "Microservices",
    "Software design pattern",
    "Test-driven development",
    "Agile software development",
    "Code review",
    "Version control",
    "Git",
    
    # AI & Machine Learning
    "Artificial intelligence",
    "Machine learning",
    "Deep learning",
    "Natural language processing",
    "Transformer (machine learning model)",
    "Large language model",
    
    # Data Science
    "Data science",
    "Pandas (software)",
    "NumPy",
    "Scikit-learn",
    
    # Security
    "Computer security",
    "Encryption",
    "Authentication",
    "OAuth",
    
    # Architecture
    "Software architecture",
    "Model–view–controller",
    "Representational state transfer",
    "Service-oriented architecture"
]


def main():
    """Build knowledge base from Wikipedia"""
    builder = WikipediaKnowledgeBuilder()
    result = builder.build_knowledge_base(TECHNICAL_TOPICS)
    
    print(f"\n🎉 Knowledge base ready for conversational AI!")
    print(f"   Location: {builder.persist_dir}")
    print(f"   Articles: {result['successful']}/{result['total_articles']}")
    print(f"   Chunks: {result['total_chunks']}")


if __name__ == "__main__":
    main()

# Made with Bob

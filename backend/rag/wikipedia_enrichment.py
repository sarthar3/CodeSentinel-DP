"""
Wikipedia Integration for RAG Knowledge Base Enrichment
Fetches relevant Wikipedia articles to enhance context
"""
import wikipediaapi
from typing import List, Dict, Optional
import chromadb
from sentence_transformers import SentenceTransformer
import os
from dotenv import load_dotenv

load_dotenv()


class WikipediaEnricher:
    """
    Enriches RAG knowledge base with Wikipedia content
    """
    
    def __init__(self, persist_dir: Optional[str] = None):
        """
        Initialize Wikipedia enricher
        
        Args:
            persist_dir: ChromaDB persistence directory
        """
        # Initialize Wikipedia API
        self.wiki = wikipediaapi.Wikipedia(
            language='en',
            user_agent='CodeSentinel/1.0 (https://github.com/codesentinel)'
        )
        
        # Initialize ChromaDB
        self.persist_dir = persist_dir or os.getenv("CHROMA_PERSIST_DIR", "./backend/data/chroma")
        self.client = chromadb.PersistentClient(path=self.persist_dir)
        
        try:
            self.collection = self.client.get_collection(name="legacy_docs")
        except Exception:
            # Create collection if it doesn't exist
            self.collection = self.client.create_collection(
                name="legacy_docs",
                metadata={"description": "Legacy documentation and Wikipedia enrichment"}
            )
        
        # Initialize embeddings model
        self.embedding_model = SentenceTransformer('all-mpnet-base-v2')
        
        print("✅ WikipediaEnricher initialized")
    
    def search_wikipedia(self, query: str, max_results: int = 3) -> List[Dict]:
        """
        Search Wikipedia for relevant articles
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of article summaries
        """
        results = []
        
        try:
            # Get Wikipedia page
            page = self.wiki.page(query)
            
            if page.exists():
                results.append({
                    "title": page.title,
                    "summary": page.summary[:1000],
                    "url": page.fullurl,
                    "sections": list(page.sections.keys())[:5]
                })
            
            # Try related searches
            search_terms = query.split()
            for term in search_terms[:max_results-1]:
                if len(term) > 3:  # Skip short words
                    page = self.wiki.page(term.capitalize())
                    if page.exists() and page.title not in [r['title'] for r in results]:
                        results.append({
                            "title": page.title,
                            "summary": page.summary[:1000],
                            "url": page.fullurl,
                            "sections": list(page.sections.keys())[:5]
                        })
                        
                        if len(results) >= max_results:
                            break
        
        except Exception as e:
            print(f"⚠️ Wikipedia search error: {e}")
        
        return results
    
    def get_article_content(self, title: str, include_sections: bool = True) -> Optional[Dict]:
        """
        Get full Wikipedia article content
        
        Args:
            title: Article title
            include_sections: Include section content
            
        Returns:
            Article content dictionary
        """
        try:
            page = self.wiki.page(title)
            
            if not page.exists():
                return None
            
            content = {
                "title": page.title,
                "summary": page.summary,
                "url": page.fullurl,
                "text": page.text[:5000],  # Limit to 5000 chars
                "sections": {}
            }
            
            if include_sections:
                for section in list(page.sections)[:5]:  # First 5 sections
                    content["sections"][section.title] = section.text[:1000]
            
            return content
            
        except Exception as e:
            print(f"⚠️ Error fetching article '{title}': {e}")
            return None
    
    def enrich_knowledge_base(self, topics: List[str]) -> Dict:
        """
        Enrich ChromaDB with Wikipedia articles on specified topics
        
        Args:
            topics: List of topics to fetch from Wikipedia
            
        Returns:
            Summary of enrichment
        """
        added_count = 0
        failed_count = 0
        
        for topic in topics:
            try:
                # Get article content
                article = self.get_article_content(topic, include_sections=True)
                
                if not article:
                    failed_count += 1
                    continue
                
                # Add summary to knowledge base
                summary_embedding = self.embedding_model.encode([article['summary']])[0]
                
                self.collection.add(
                    documents=[article['summary']],
                    embeddings=[summary_embedding.tolist()],
                    metadatas=[{
                        "source": f"Wikipedia: {article['title']}",
                        "page": 0,
                        "url": article['url'],
                        "type": "wikipedia"
                    }],
                    ids=[f"wiki_{article['title'].replace(' ', '_')}"]
                )
                
                # Add section content
                for section_title, section_text in article['sections'].items():
                    if len(section_text) > 100:  # Skip very short sections
                        section_embedding = self.embedding_model.encode([section_text])[0]
                        
                        self.collection.add(
                            documents=[section_text],
                            embeddings=[section_embedding.tolist()],
                            metadatas=[{
                                "source": f"Wikipedia: {article['title']} - {section_title}",
                                "page": 0,
                                "url": article['url'],
                                "type": "wikipedia_section"
                            }],
                            ids=[f"wiki_{article['title'].replace(' ', '_')}_{section_title.replace(' ', '_')}"]
                        )
                
                added_count += 1
                print(f"✅ Added Wikipedia article: {article['title']}")
                
            except Exception as e:
                print(f"⚠️ Failed to add topic '{topic}': {e}")
                failed_count += 1
        
        return {
            "added": added_count,
            "failed": failed_count,
            "total": len(topics)
        }
    
    def suggest_enrichment_topics(self, query: str) -> List[str]:
        """
        Suggest Wikipedia topics based on query
        
        Args:
            query: User query
            
        Returns:
            List of suggested topics
        """
        # Extract key terms (simple approach)
        words = query.split()
        topics = []
        
        # Capitalize potential topics
        for word in words:
            if len(word) > 4 and word[0].isupper():
                topics.append(word)
        
        # Add full query as topic
        if len(query.split()) <= 5:
            topics.insert(0, query)
        
        return topics[:3]


# Predefined technical topics for initial enrichment
DEFAULT_TECH_TOPICS = [
    "Software engineering",
    "Microservices",
    "REST API",
    "Database normalization",
    "Machine learning",
    "Continuous integration",
    "Test-driven development",
    "Code review",
    "Git version control",
    "Python programming",
    "JavaScript",
    "Docker containerization",
    "Kubernetes",
    "FastAPI",
    "React framework"
]


def enrich_with_defaults():
    """
    Enrich knowledge base with default technical topics
    """
    enricher = WikipediaEnricher()
    print("🌐 Enriching knowledge base with Wikipedia content...")
    result = enricher.enrich_knowledge_base(DEFAULT_TECH_TOPICS)
    print(f"📊 Enrichment complete: {result['added']} added, {result['failed']} failed")
    return result


if __name__ == "__main__":
    # Run enrichment
    enrich_with_defaults()

# Made with Bob

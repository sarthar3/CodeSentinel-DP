"""
Wikipedia Knowledge Base Enrichment Script
Run this to add Wikipedia articles to your RAG knowledge base
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.rag.wikipedia_enrichment import WikipediaEnricher, DEFAULT_TECH_TOPICS


def main():
    """
    Enrich the knowledge base with Wikipedia articles
    """
    print("=" * 60)
    print("📚 Wikipedia Knowledge Base Enrichment")
    print("=" * 60)
    print()
    
    # Initialize enricher
    enricher = WikipediaEnricher()
    
    # Show default topics
    print("📋 Default Technical Topics:")
    for i, topic in enumerate(DEFAULT_TECH_TOPICS, 1):
        print(f"  {i}. {topic}")
    print()
    
    # Ask user
    choice = input("Enrich with default topics? (y/n): ").strip().lower()
    
    if choice == 'y':
        print("\n🌐 Fetching Wikipedia articles...")
        result = enricher.enrich_knowledge_base(DEFAULT_TECH_TOPICS)
        
        print("\n" + "=" * 60)
        print("✅ Enrichment Complete!")
        print("=" * 60)
        print(f"✓ Added: {result['added']} articles")
        print(f"✗ Failed: {result['failed']} articles")
        print(f"📊 Total: {result['total']} topics processed")
        print()
        print("💡 Your RAG knowledge base now includes Wikipedia content!")
        print("   Try asking: 'What is microservices architecture?'")
        
    else:
        print("\n📝 Custom Topics")
        print("Enter topics one per line (empty line to finish):")
        
        custom_topics = []
        while True:
            topic = input("  Topic: ").strip()
            if not topic:
                break
            custom_topics.append(topic)
        
        if custom_topics:
            print(f"\n🌐 Fetching {len(custom_topics)} Wikipedia articles...")
            result = enricher.enrich_knowledge_base(custom_topics)
            
            print("\n" + "=" * 60)
            print("✅ Enrichment Complete!")
            print("=" * 60)
            print(f"✓ Added: {result['added']} articles")
            print(f"✗ Failed: {result['failed']} articles")
            print(f"📊 Total: {result['total']} topics processed")
        else:
            print("\n❌ No topics provided. Exiting.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

# Made with Bob

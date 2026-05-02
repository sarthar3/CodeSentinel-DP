"""
Rebuild ChromaDB with new 768-dim embeddings (all-mpnet-base-v2)
This fixes the dimension mismatch error
"""
import os
import shutil
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def main():
    print("=" * 60)
    print("Rebuilding ChromaDB with New Embeddings")
    print("=" * 60)
    print()
    
    # Path to ChromaDB
    chroma_path = "./backend/data/chroma"
    
    if os.path.exists(chroma_path):
        print(f"Found existing ChromaDB at: {chroma_path}")
        choice = input("WARNING: Delete and rebuild? (y/n): ").strip().lower()
        
        if choice == 'y':
            print("Deleting old ChromaDB...")
            shutil.rmtree(chroma_path)
            print("SUCCESS: Deleted successfully")
        else:
            print("CANCELLED: Exiting.")
            return
    
    print()
    print("Re-ingesting documents with new embeddings...")
    print("   Model: all-mpnet-base-v2 (768 dimensions)")
    print()
    
    # Run ingest script
    import subprocess
    
    # Ingest demo data
    demo_dir = "./demo_data"
    if os.path.exists(demo_dir):
        print(f"Ingesting from: {demo_dir}")
        result = subprocess.run(
            ["python", "backend/rag/ingest.py", "--dir", demo_dir],
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
    else:
        print(f"WARNING: Demo data directory not found: {demo_dir}")
        print("   Please run: python backend/rag/ingest.py --dir <your_data_dir>")
    
    print()
    print("=" * 60)
    print("SUCCESS: Rebuild Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("   1. Restart the backend server")
    print("   2. Test RAG ChatBot")
    print("   3. (Optional) Run: python enrich_wikipedia.py")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nINTERRUPTED: Cancelled by user")
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()

# Made with Bob

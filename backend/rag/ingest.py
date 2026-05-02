"""
RAG Document Ingestion Pipeline
Loads PDFs, markdown, and text files into ChromaDB with embeddings
"""
import os
import argparse
from pathlib import Path
from typing import List, Dict
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader
import markdown
from dotenv import load_dotenv

load_dotenv()


class DocumentIngester:
    """Handles document ingestion into ChromaDB"""
    
    def __init__(self, persist_dir: str = None):
        """
        Initialize the document ingester
        
        Args:
            persist_dir: Directory to persist ChromaDB data
        """
        self.persist_dir = persist_dir or os.getenv("CHROMA_PERSIST_DIR", "./data/chroma")
        
        # Ensure persist directory exists
        Path(self.persist_dir).mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(path=self.persist_dir)
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="legacy_docs",
            metadata={"description": "Legacy documentation and incident reports"}
        )
        
        # Initialize embedding model (all-mpnet-base-v2 for 768-dim embeddings)
        print("Loading embedding model...")
        self.embedding_model = SentenceTransformer('all-mpnet-base-v2')
        print("Embedding model loaded successfully")
    
    def extract_text_from_pdf(self, pdf_path: str) -> List[Dict[str, any]]:
        """
        Extract text from PDF file with page numbers
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of dictionaries with page text and metadata
        """
        chunks = []
        reader = PdfReader(pdf_path)
        
        for page_num, page in enumerate(reader.pages, start=1):
            text = page.extract_text()
            if text.strip():
                chunks.append({
                    "text": text,
                    "source": os.path.basename(pdf_path),
                    "page": page_num,
                    "type": "pdf"
                })
        
        return chunks
    
    def extract_text_from_markdown(self, md_path: str) -> List[Dict[str, any]]:
        """
        Extract text from Markdown file
        
        Args:
            md_path: Path to markdown file
            
        Returns:
            List of dictionaries with text and metadata
        """
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split by headers for better chunking
        chunks = []
        sections = content.split('\n## ')
        
        for idx, section in enumerate(sections):
            if section.strip():
                chunks.append({
                    "text": section,
                    "source": os.path.basename(md_path),
                    "page": idx + 1,  # Use section number as "page"
                    "type": "markdown"
                })
        
        return chunks
    
    def extract_text_from_txt(self, txt_path: str) -> List[Dict[str, any]]:
        """
        Extract text from plain text file
        
        Args:
            txt_path: Path to text file
            
        Returns:
            List of dictionaries with text and metadata
        """
        with open(txt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split into chunks of ~500 words
        words = content.split()
        chunk_size = 500
        chunks = []
        
        for i in range(0, len(words), chunk_size):
            chunk_text = ' '.join(words[i:i + chunk_size])
            if chunk_text.strip():
                chunks.append({
                    "text": chunk_text,
                    "source": os.path.basename(txt_path),
                    "page": (i // chunk_size) + 1,
                    "type": "text"
                })
        
        return chunks
    
    def ingest_directory(self, directory: str) -> int:
        """
        Ingest all supported documents from a directory
        
        Args:
            directory: Path to directory containing documents
            
        Returns:
            Number of chunks ingested
        """
        directory_path = Path(directory)
        if not directory_path.exists():
            raise ValueError(f"Directory not found: {directory}")
        
        all_chunks = []
        
        # Process all files
        for file_path in directory_path.rglob('*'):
            if file_path.is_file():
                try:
                    if file_path.suffix.lower() == '.pdf':
                        print(f"Processing PDF: {file_path.name}")
                        chunks = self.extract_text_from_pdf(str(file_path))
                        all_chunks.extend(chunks)
                    
                    elif file_path.suffix.lower() in ['.md', '.markdown']:
                        print(f"Processing Markdown: {file_path.name}")
                        chunks = self.extract_text_from_markdown(str(file_path))
                        all_chunks.extend(chunks)
                    
                    elif file_path.suffix.lower() == '.txt':
                        print(f"Processing Text: {file_path.name}")
                        chunks = self.extract_text_from_txt(str(file_path))
                        all_chunks.extend(chunks)
                
                except Exception as e:
                    print(f"Error processing {file_path.name}: {e}")
        
        if not all_chunks:
            print("No documents found to ingest")
            return 0
        
        # Generate embeddings in batches
        print(f"Generating embeddings for {len(all_chunks)} chunks...")
        texts = [chunk["text"] for chunk in all_chunks]
        embeddings = self.embedding_model.encode(texts, show_progress_bar=True)
        
        # Prepare data for ChromaDB
        ids = [f"{chunk['source']}_page{chunk['page']}" for chunk in all_chunks]
        metadatas = [
            {
                "source": chunk["source"],
                "page": chunk["page"],
                "type": chunk["type"]
            }
            for chunk in all_chunks
        ]
        
        # Add to collection
        print("Adding documents to ChromaDB...")
        self.collection.add(
            ids=ids,
            embeddings=embeddings.tolist(),
            documents=texts,
            metadatas=metadatas
        )
        
        # CRITICAL: Persist the data
        print("Persisting data to disk...")
        
        print(f"Successfully ingested {len(all_chunks)} chunks")
        return len(all_chunks)


def main():
    """CLI entry point for document ingestion"""
    parser = argparse.ArgumentParser(description="Ingest documents into RAG system")
    parser.add_argument(
        "--dir",
        required=True,
        help="Directory containing documents to ingest"
    )
    parser.add_argument(
        "--persist-dir",
        default=None,
        help="ChromaDB persistence directory (default: from .env)"
    )
    
    args = parser.parse_args()
    
    ingester = DocumentIngester(persist_dir=args.persist_dir)
    count = ingester.ingest_directory(args.dir)
    
    print(f"\n✓ Ingestion complete: {count} chunks added to knowledge base")


if __name__ == "__main__":
    main()

# Made with Bob

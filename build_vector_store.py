"""Script to build/update the vector store from extracted data."""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.rag.embedding_service import EmbeddingService
from src.rag.vector_store import VectorStore
from src.rag.data_preparation import DataPreparation


def build_vector_store(overwrite: bool = False):
    """
    Build or update the vector store from extracted data.
    
    Args:
        overwrite: If True, delete existing data before adding new data
    """
    print("=" * 60)
    print("Building Vector Store")
    print("=" * 60)
    
    # Initialize components
    print("\n1. Initializing components...")
    embedding_service = EmbeddingService()
    vector_store = VectorStore()
    data_prep = DataPreparation()
    
    # Check if vector store already has data
    collection_info = vector_store.get_collection_info()
    if collection_info['document_count'] > 0:
        if overwrite:
            print(f"\n2. Deleting existing {collection_info['document_count']} documents...")
            vector_store.delete_all()
        else:
            print(f"\n[WARNING] Vector store already contains {collection_info['document_count']} documents.")
            print("Use overwrite=True to replace existing data.")
            return
    
    # Load and prepare data
    print("\n2. Loading and preparing data...")
    try:
        all_chunks = data_prep.load_and_prepare_all_schemes()
    except ValueError as e:
        print(f"[ERROR] {e}")
        return
    
    if not all_chunks:
        print("[ERROR] No chunks prepared. Check if data extraction was successful.")
        return
    
    # Extract texts and metadatas
    texts = [chunk['text'] for chunk in all_chunks]
    metadatas = [chunk['metadata'] for chunk in all_chunks]
    
    # Generate embeddings
    print(f"\n3. Generating embeddings for {len(texts)} chunks...")
    print("This may take a few moments...")
    embeddings = embedding_service.generate_embeddings(texts)
    
    # Add to vector store
    print("\n4. Adding documents to vector store...")
    vector_store.add_documents(
        texts=texts,
        embeddings=embeddings,
        metadatas=metadatas
    )
    
    # Verify
    final_info = vector_store.get_collection_info()
    print("\n" + "=" * 60)
    print("Vector Store Build Complete")
    print("=" * 60)
    print(f"Total documents: {final_info['document_count']}")
    print(f"Collection: {final_info['collection_name']}")
    print(f"Storage location: {final_info['persist_directory']}")
    print("=" * 60)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Build vector store from extracted data")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing vector store data"
    )
    
    args = parser.parse_args()
    build_vector_store(overwrite=args.overwrite)


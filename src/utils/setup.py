"""Setup script to initialize vector store on first run."""
import os
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.rag.vector_store import VectorStore
from src.rag.embedding_service import EmbeddingService
from src.rag.data_preparation import DataPreparation


def setup_vector_store(force_rebuild: bool = False):
    """
    Set up vector store if it doesn't exist.
    
    Args:
        force_rebuild: If True, rebuild even if vector store exists
    """
    vector_store = VectorStore()
    collection_info = vector_store.get_collection_info()
    
    # Check if vector store already has data
    if collection_info['document_count'] > 0 and not force_rebuild:
        print(f"Vector store already exists with {collection_info['document_count']} documents")
        return True
    
    print("Vector store not found or empty. Building...")
    
    try:
        # Load and prepare data
        data_prep = DataPreparation()
        all_chunks = data_prep.load_and_prepare_all_schemes()
        
        if not all_chunks:
            print("ERROR: No data found. Please ensure data/processed/ contains JSON files.")
            return False
        
        # Extract texts and metadatas
        texts = [chunk['text'] for chunk in all_chunks]
        metadatas = [chunk['metadata'] for chunk in all_chunks]
        
        # Generate embeddings
        print(f"Generating embeddings for {len(texts)} chunks...")
        embedding_service = EmbeddingService()
        embeddings = embedding_service.generate_embeddings(texts)
        
        # Clear existing data if rebuilding
        if collection_info['document_count'] > 0:
            vector_store.delete_all()
        
        # Add to vector store
        print("Adding documents to vector store...")
        vector_store.add_documents(
            texts=texts,
            embeddings=embeddings,
            metadatas=metadatas
        )
        
        final_info = vector_store.get_collection_info()
        print(f"✓ Vector store built successfully with {final_info['document_count']} documents")
        return True
        
    except Exception as e:
        print(f"ERROR building vector store: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    setup_vector_store()


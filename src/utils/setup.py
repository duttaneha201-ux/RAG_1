"""Setup script to initialize vector store on first run."""
import os
from pathlib import Path
import sys

# Fix for PyTorch meta tensor issue - set before any imports
os.environ['HF_HUB_DISABLE_EXPERIMENTAL_WARNING'] = '1'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

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
    vector_store = None
    collection_info = None
    
    # Try to initialize vector store
    try:
        vector_store = VectorStore()
        collection_info = vector_store.get_collection_info()
        
        # Check if vector store already has data
        if collection_info['document_count'] > 0 and not force_rebuild:
            print(f"Vector store already exists with {collection_info['document_count']} documents")
            return True
    except Exception as e:
        error_str = str(e).lower()
        if "tenant" in error_str or "default_tenant" in error_str or "could not connect" in error_str:
            print("WARNING: Vector store database appears corrupted. Will rebuild from scratch...")
            # Delete the corrupted database
            import shutil
            db_path = Path("data/chroma_db")
            if db_path.exists():
                try:
                    shutil.rmtree(db_path, ignore_errors=True)
                    print("Corrupted database removed. Creating new database...")
                except Exception as cleanup_error:
                    print(f"Warning: Could not fully clean database directory: {cleanup_error}")
            # Force rebuild by continuing below
            force_rebuild = True
            # Reset vector_store so we recreate it below
            vector_store = None
            collection_info = None
        else:
            # Re-raise if it's a different error
            raise
    
    print("Vector store not found or empty. Building...")
    
    try:
        # Initialize vector store if it wasn't created above
        if vector_store is None:
            vector_store = VectorStore()
            collection_info = vector_store.get_collection_info()
        
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
        try:
            if collection_info['document_count'] > 0:
                vector_store.delete_all()
        except (NameError, KeyError):
            # Collection info not available, continue with adding documents
            pass
        
        # Add to vector store
        print("Adding documents to vector store...")
        vector_store.add_documents(
            texts=texts,
            embeddings=embeddings,
            metadatas=metadatas
        )
        
        final_info = vector_store.get_collection_info()
        # Use ASCII-safe message to avoid encoding issues on Windows
        print(f"[OK] Vector store built successfully with {final_info['document_count']} documents")
        return True
        
    except Exception as e:
        print(f"ERROR building vector store: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    setup_vector_store()


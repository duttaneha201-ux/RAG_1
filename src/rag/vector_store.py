"""Vector store for managing embeddings in ChromaDB."""
import chromadb
from chromadb.config import Settings
from pathlib import Path
from typing import List, Dict, Optional
import uuid


class VectorStore:
    """Manage vector embeddings in ChromaDB."""
    
    def __init__(self, persist_directory: str = "data/chroma_db", collection_name: str = "hdfc_mutual_funds"):
        """
        Initialize the vector store.
        
        Args:
            persist_directory: Directory to persist ChromaDB data
            collection_name: Name of the ChromaDB collection
        """
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        self.collection_name = collection_name
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "HDFC Mutual Fund scheme data"}
        )
    
    def add_documents(
        self,
        texts: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict],
        ids: Optional[List[str]] = None
    ):
        """
        Add documents to the vector store.
        
        Args:
            texts: List of text content
            embeddings: List of embedding vectors
            metadatas: List of metadata dictionaries (must include source_url)
            ids: Optional list of document IDs (auto-generated if not provided)
        """
        if not texts or not embeddings or not metadatas:
            raise ValueError("texts, embeddings, and metadatas must be non-empty lists")
        
        if len(texts) != len(embeddings) or len(texts) != len(metadatas):
            raise ValueError("texts, embeddings, and metadatas must have the same length")
        
        # Generate IDs if not provided
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in texts]
        
        # Validate that all metadatas have source_url
        for i, metadata in enumerate(metadatas):
            if 'source_url' not in metadata:
                raise ValueError(f"Metadata at index {i} is missing 'source_url'")
        
        # Add to collection
        self.collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"Added {len(texts)} documents to vector store")
    
    def search(
        self,
        query_embedding: List[float],
        n_results: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Search for similar documents.
        
        Args:
            query_embedding: Query embedding vector
            n_results: Number of results to return
            filter_metadata: Optional metadata filters (e.g., {"scheme_name": "HDFC Equity Fund"})
            
        Returns:
            Dictionary with 'ids', 'documents', 'metadatas', 'distances'
        """
        query_filters = None
        if filter_metadata:
            query_filters = filter_metadata
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=query_filters
        )
        
        return results
    
    def delete_all(self):
        """Delete all documents from the collection."""
        # Get all IDs
        all_data = self.collection.get()
        if all_data['ids']:
            self.collection.delete(ids=all_data['ids'])
            print(f"Deleted {len(all_data['ids'])} documents from vector store")
        else:
            print("Vector store is already empty")
    
    def get_collection_info(self) -> Dict:
        """
        Get information about the collection.
        
        Returns:
            Dictionary with collection statistics
        """
        count = self.collection.count()
        return {
            "collection_name": self.collection_name,
            "document_count": count,
            "persist_directory": str(self.persist_directory)
        }


"""Retrieval system for querying the vector store."""
from typing import List, Dict, Optional
from src.rag.embedding_service import EmbeddingService
from src.rag.vector_store import VectorStore
from datetime import datetime


class RetrievalSystem:
    """System for retrieving relevant documents from vector store."""
    
    def __init__(self, embedding_service: Optional[EmbeddingService] = None, 
                 vector_store: Optional[VectorStore] = None):
        """
        Initialize the retrieval system.
        
        Args:
            embedding_service: Optional embedding service (creates new if not provided)
            vector_store: Optional vector store (creates new if not provided)
        """
        self.embedding_service = embedding_service or EmbeddingService()
        self.vector_store = vector_store or VectorStore()
    
    def retrieve(self, query: str, n_results: int = 5, 
                 scheme_filter: Optional[str] = None) -> Dict:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: User query/question
            n_results: Number of results to return
            scheme_filter: Optional scheme name to filter results
            
        Returns:
            Dictionary containing:
            - query: Original query
            - results: List of retrieved documents with metadata
            - retrieved_at: Timestamp
        """
        if not query or not isinstance(query, str):
            raise ValueError("Query must be a non-empty string")
        
        # Generate query embedding
        query_embedding = self.embedding_service.generate_embedding(query)
        
        # Apply scheme filter if provided
        filter_metadata = None
        if scheme_filter:
            filter_metadata = {"scheme_name": scheme_filter}
        
        # Search vector store
        search_results = self.vector_store.search(
            query_embedding=query_embedding,
            n_results=n_results,
            filter_metadata=filter_metadata
        )
        
        # Format results
        results = []
        if search_results['documents'] and len(search_results['documents'][0]) > 0:
            for doc, metadata, distance in zip(
                search_results['documents'][0],
                search_results['metadatas'][0],
                search_results['distances'][0]
            ):
                results.append({
                    'document': doc,
                    'metadata': metadata,
                    'similarity_score': 1 - distance,  # Convert distance to similarity
                    'distance': distance
                })
        
        return {
            'query': query,
            'results': results,
            'retrieved_at': datetime.now().isoformat(),
            'total_results': len(results)
        }
    
    def retrieve_with_context(self, query: str, n_results: int = 5,
                             scheme_filter: Optional[str] = None) -> str:
        """
        Retrieve and format results as context string for LLM.
        
        Args:
            query: User query/question
            n_results: Number of results to return
            scheme_filter: Optional scheme name to filter results
            
        Returns:
            Formatted context string with retrieved information
        """
        retrieval_result = self.retrieve(query, n_results, scheme_filter)
        
        if not retrieval_result['results']:
            return "No relevant information found."
        
        context_parts = []
        for i, result in enumerate(retrieval_result['results'], 1):
            metadata = result['metadata']
            doc = result['document']
            
            context_parts.append(
                f"[Source {i}] {metadata.get('scheme_name', 'Unknown Scheme')} "
                f"({metadata.get('category', 'Unknown Category')}):\n"
                f"{doc}\n"
                f"Source URL: {metadata.get('source_url', 'N/A')}\n"
            )
        
        return "\n".join(context_parts)
    
    def get_scheme_info(self, scheme_name: str) -> List[Dict]:
        """
        Get all information about a specific scheme.
        
        Args:
            scheme_name: Name of the scheme
            
        Returns:
            List of all documents for the scheme
        """
        # Use a broad query to get all scheme information
        query = f"{scheme_name} mutual fund information"
        retrieval_result = self.retrieve(query, n_results=10, scheme_filter=scheme_name)
        
        return retrieval_result['results']


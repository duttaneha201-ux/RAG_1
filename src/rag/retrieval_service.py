"""Main retrieval service that combines query processing and retrieval."""
from typing import Dict, Optional
from src.rag.retrieval import RetrievalSystem
from src.rag.query_processor import QueryProcessor
from src.rag.response_formatter import ResponseFormatter


class RetrievalService:
    """Main service for processing queries and retrieving relevant information."""
    
    def __init__(self):
        """Initialize the retrieval service."""
        self.retrieval_system = RetrievalSystem()
        self.query_processor = QueryProcessor()
        self.response_formatter = ResponseFormatter()
    
    def process_and_retrieve(self, query: str, n_results: int = 5) -> Dict:
        """
        Process a user query and retrieve relevant information.
        
        Args:
            query: User query/question
            n_results: Number of results to retrieve
            
        Returns:
            Dictionary containing:
            - processed_query: Processed query information
            - retrieval_result: Raw retrieval results
            - formatted_response: Formatted response for display/LLM
            - is_factual: Whether query is factual
        """
        # Process query
        processed = self.query_processor.process_query(query)
        
        # Check if query is factual
        is_factual = self.query_processor.is_factual_query(query)
        
        # Retrieve relevant documents
        retrieval_result = self.retrieval_system.retrieve(
            query=processed['enhanced_query'],
            n_results=n_results,
            scheme_filter=processed.get('scheme_name')
        )
        
        # Format response
        formatted_response = self.response_formatter.format_retrieval_results(
            retrieval_result,
            max_results=3
        )
        
        return {
            'processed_query': processed,
            'retrieval_result': retrieval_result,
            'formatted_response': formatted_response,
            'is_factual': is_factual,
            'query': query
        }
    
    def get_context_for_llm(self, query: str, n_results: int = 5) -> str:
        """
        Get formatted context string for LLM from a query.
        
        Args:
            query: User query/question
            n_results: Number of results to retrieve
            
        Returns:
            Formatted context string
        """
        result = self.process_and_retrieve(query, n_results)
        return self.response_formatter.format_for_llm(
            result['retrieval_result'],
            max_results=3
        )
    
    def validate_query(self, query: str) -> Dict:
        """
        Validate if a query can be answered by the system.
        
        Args:
            query: User query
            
        Returns:
            Dictionary with validation result
        """
        is_factual = self.query_processor.is_factual_query(query)
        
        if not is_factual:
            return {
                'valid': False,
                'reason': 'Query seeks opinion or advice, which is not supported.',
                'message': 'I can only answer factual questions about HDFC mutual fund schemes (expense ratio, minimum SIP, exit load, NAV, tax implications). I cannot provide investment advice or answer portfolio-related questions.'
            }
        
        return {
            'valid': True,
            'reason': 'Query is factual and can be answered.'
        }


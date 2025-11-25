"""Answer generator combining retrieval and LLM."""
from typing import Dict, Optional
import sys
from src.rag.retrieval_service import RetrievalService
from src.rag.llm_service import LLMService
from src.scraper.data_storage import DataStorage
from datetime import datetime

def safe_str_error(error: Exception) -> str:
    """Convert exception to string safely, handling Unicode encoding issues on Windows."""
    try:
        error_str = str(error)
        # Replace any Unicode characters that might cause encoding issues
        return error_str.encode('ascii', 'replace').decode('ascii')
    except (UnicodeEncodeError, UnicodeDecodeError):
        # Fallback: use repr if string conversion fails
        try:
            return repr(error)
        except:
            return "An error occurred (unable to encode error message)"


class AnswerGenerator:
    """Generate answers by combining retrieval and LLM."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the answer generator.
        
        Args:
            api_key: Google AI API key (optional, can use env var)
        """
        try:
            self.retrieval_service = RetrievalService()
            self.llm_service = LLMService(api_key=api_key)
            self.data_storage = DataStorage()
        except Exception as e:
            error_str = safe_str_error(e)
            error_msg = f"Failed to initialize AnswerGenerator: {error_str}"
            # Use safe print to avoid encoding issues
            try:
                print(f"[ERROR] {error_msg}")
            except UnicodeEncodeError:
                print(f"[ERROR] Failed to initialize AnswerGenerator: {error_str}")
            raise ValueError(error_msg) from e
    
    def generate_answer(self, question: str, n_results: int = 3) -> Dict:
        """
        Generate a complete answer for a user question.
        
        Args:
            question: User question
            n_results: Number of retrieval results to use
            
        Returns:
            Dictionary containing:
            - answer: Generated answer
            - source_url: Source URL(s)
            - is_factual: Whether query was factual
            - validation: Validation result
            - retrieval_info: Retrieval information
        """
        # Validate query
        validation = self.retrieval_service.validate_query(question)
        if not validation['valid']:
            return {
                'answer': validation.get('message', self.llm_service.get_refusal_message()),
                'source_url': None,
                'is_factual': False,
                'validation': validation,
                'retrieval_info': None,
                'model': self.llm_service.model_name
            }
        
        # Retrieve relevant information
        retrieval_result = self.retrieval_service.process_and_retrieve(
            question, 
            n_results=n_results
        )
        
        if not retrieval_result['retrieval_result']['results']:
            return {
                'answer': "I couldn't find relevant information to answer your question. Please try rephrasing or asking about expense ratio, minimum SIP, exit load, NAV, or tax implications for HDFC mutual fund schemes.",
                'source_url': None,
                'is_factual': True,
                'validation': validation,
                'retrieval_info': retrieval_result,
                'model': self.llm_service.model_name
            }
        
        # Get formatted context for LLM
        formatted_response = retrieval_result['formatted_response']
        context = formatted_response['context']
        
        # Get extraction date from latest data
        try:
            schemes = self.data_storage.load_latest_data()
            if schemes:
                # Get the most recent extraction date
                extracted_dates = [s.get('extracted_at', '') for s in schemes if s.get('extracted_at')]
                extracted_at = max(extracted_dates) if extracted_dates else None
            else:
                extracted_at = None
        except:
            extracted_at = None
        
        # Generate answer using LLM
        llm_result = self.llm_service.generate_answer(
            question=question,
            context=context,
            extracted_at=extracted_at
        )
        
        # Extract source URLs
        source_urls = formatted_response.get('sources', [])
        primary_source = source_urls[0] if source_urls else None
        
        return {
            'answer': llm_result['answer'],
            'source_url': primary_source,
            'source_urls': source_urls,
            'is_factual': True,
            'validation': validation,
            'retrieval_info': {
                'total_results': retrieval_result['retrieval_result']['total_results'],
                'schemes': formatted_response['metadata'].get('schemes', [])
            },
            'retrieval_result': retrieval_result,  # Include raw retrieval data for fallback
            'formatted_context': context,  # Include formatted context for fallback
            'model': llm_result['model'],
            'timestamp': llm_result['timestamp']
        }
    
    def format_answer_with_source(self, answer: str, source_url: Optional[str]) -> str:
        """
        Format answer with source URL if not already included.
        
        Args:
            answer: Generated answer
            source_url: Source URL
            
        Returns:
            Formatted answer with source
        """
        if not source_url:
            return answer
        
        # Check if source URL is already in answer
        if source_url in answer:
            return answer
        
        # Add source URL
        return f"{answer}\n\nSource: {source_url}"


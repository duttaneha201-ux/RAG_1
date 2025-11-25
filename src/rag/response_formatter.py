"""Response formatter for structuring retrieved information."""
from typing import Dict, List, Optional
from datetime import datetime
from src.utils.token_counter import estimate_tokens, truncate_smart


class ResponseFormatter:
    """Format retrieved results into structured responses."""
    
    def __init__(self):
        """Initialize the response formatter."""
        pass
    
    def format_retrieval_results(self, retrieval_result: Dict, 
                                max_results: int = 3,
                                max_tokens_per_doc: int = 500,
                                max_total_context_tokens: int = 1500) -> Dict:
        """
        Format retrieval results for display or LLM context.
        
        Args:
            retrieval_result: Result from RetrievalSystem.retrieve()
            max_results: Maximum number of results to include
            max_tokens_per_doc: Maximum tokens per document chunk (default: 500)
            max_total_context_tokens: Maximum total tokens for all context (default: 1500)
            
        Returns:
            Formatted dictionary with:
            - context: Formatted context string
            - sources: List of source URLs
            - metadata: Additional metadata
        """
        results = retrieval_result.get('results', [])
        if not results:
            return {
                'context': "No relevant information found.",
                'sources': [],
                'metadata': {}
            }
        
        # Limit results
        limited_results = results[:max_results]
        
        # Extract unique sources
        sources = []
        seen_urls = set()
        
        context_parts = []
        total_tokens = 0
        
        for i, result in enumerate(limited_results, 1):
            metadata = result['metadata']
            doc = result['document']
            scheme_name = metadata.get('scheme_name', 'Unknown')
            field_label = metadata.get('field_label', 'Information')
            source_url = metadata.get('source_url', '')
            
            # Add source URL if not seen
            if source_url and source_url not in seen_urls:
                sources.append(source_url)
                seen_urls.add(source_url)
            
            # Truncate document if it's too long
            doc_tokens = estimate_tokens(doc)
            if doc_tokens > max_tokens_per_doc:
                # Truncate to max_tokens_per_doc, keeping the beginning
                doc, _ = truncate_smart(doc, max_tokens_per_doc, preserve_end=False)
            
            # Create formatted text
            formatted_text = f"{scheme_name} - {field_label}: {doc}"
            formatted_tokens = estimate_tokens(formatted_text)
            
            # Check if adding this would exceed total limit
            if total_tokens + formatted_tokens > max_total_context_tokens:
                # Truncate this part to fit remaining budget
                remaining_tokens = max_total_context_tokens - total_tokens
                if remaining_tokens > 50:  # Only add if we have meaningful space left
                    doc, _ = truncate_smart(doc, remaining_tokens - estimate_tokens(f"{scheme_name} - {field_label}: "), preserve_end=False)
                    formatted_text = f"{scheme_name} - {field_label}: {doc}"
                    formatted_tokens = estimate_tokens(formatted_text)
                    context_parts.append(formatted_text)
                    total_tokens += formatted_tokens
                break  # Stop adding more results
            
            context_parts.append(formatted_text)
            total_tokens += formatted_tokens
        
        context = "\n\n".join(context_parts)
        
        return {
            'context': context,
            'sources': sources,
            'metadata': {
                'total_results': len(results),
                'used_results': len(limited_results),
                'schemes': list(set(r['metadata'].get('scheme_name', '') for r in limited_results)),
                'context_tokens': estimate_tokens(context)
            }
        }
    
    def format_for_llm(self, retrieval_result: Dict, 
                       max_results: int = 3,
                       max_tokens_per_doc: int = 500,
                       max_total_context_tokens: int = 1500) -> str:
        """
        Format retrieval results as context string for LLM.
        
        Args:
            retrieval_result: Result from RetrievalSystem.retrieve()
            max_results: Maximum number of results to include
            max_tokens_per_doc: Maximum tokens per document chunk
            max_total_context_tokens: Maximum total tokens for context
            
        Returns:
            Formatted context string
        """
        formatted = self.format_retrieval_results(
            retrieval_result, 
            max_results,
            max_tokens_per_doc=max_tokens_per_doc,
            max_total_context_tokens=max_total_context_tokens
        )
        
        context = formatted['context']
        sources = formatted['sources']
        
        # Add source information (with token budget consideration)
        if sources:
            source_text = "\n\nSources:\n" + "\n".join(f"- {url}" for url in sources)
            source_tokens = estimate_tokens(source_text)
            
            # Reserve tokens for sources (limit to 100 tokens for URLs)
            max_source_tokens = 100
            if source_tokens > max_source_tokens:
                # Limit number of sources shown if URLs are very long
                limited_sources = sources[:3]  # Show max 3 sources
                source_text = "\n\nSources:\n" + "\n".join(f"- {url}" for url in limited_sources)
            
            context += source_text
        
        return context
    
    def extract_answer_from_result(self, result: Dict) -> Optional[str]:
        """
        Extract the actual answer/value from a retrieval result.
        
        Args:
            result: Single result dictionary from retrieval
            
        Returns:
            Extracted answer string or None
        """
        metadata = result.get('metadata', {})
        document = result.get('document', '')
        
        # Try to extract the value from the document
        field_value = metadata.get('field_value')
        if field_value:
            return field_value
        
        # Extract from document text
        # Look for patterns like "Expense Ratio: 0.67%" or "Rs 100"
        import re
        
        # Try to extract after colon
        match = re.search(r':\s*(.+?)(?:\n|$)', document)
        if match:
            return match.group(1).strip()
        
        return document
    
    def get_source_url(self, result: Dict) -> Optional[str]:
        """Get source URL from a result."""
        return result.get('metadata', {}).get('source_url')
    
    def get_scheme_name(self, result: Dict) -> Optional[str]:
        """Get scheme name from a result."""
        return result.get('metadata', {}).get('scheme_name')


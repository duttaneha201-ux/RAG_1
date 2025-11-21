"""Query processor to analyze and enhance user queries."""
import re
from typing import Dict, Optional, List


class QueryProcessor:
    """Process and enhance user queries for better retrieval."""
    
    # Common scheme name patterns
    SCHEME_PATTERNS = {
        r'hdfc\s+equity': 'HDFC Equity Fund',
        r'hdfc\s+large\s+cap': 'HDFC Large Cap Fund',
        r'hdfc\s+mid\s+cap': 'HDFC Mid Cap Fund',
        r'hdfc\s+small\s+cap': 'HDFC Small Cap Fund',
        r'hdfc\s+multi\s+cap': 'HDFC Multi Cap Fund',
        r'hdfc\s+elss': 'HDFC ELSS Tax Saver Fund',
        r'hdfc\s+tax\s+saver': 'HDFC ELSS Tax Saver Fund',
    }
    
    # Field keywords
    FIELD_KEYWORDS = {
        'expense_ratio': ['expense ratio', 'expense', 'charges', 'fee'],
        'minimum_sip': ['minimum sip', 'min sip', 'sip amount', 'minimum investment', 'sip'],
        'exit_load': ['exit load', 'exit charge', 'redemption charge', 'withdrawal fee'],
        'nav': ['nav', 'net asset value', 'current nav', 'price', 'value'],
        'tax_implication': ['tax', 'taxation', 'tax implication', 'capital gains', 'tax on redemption']
    }
    
    def __init__(self):
        """Initialize the query processor."""
        pass
    
    def process_query(self, query: str) -> Dict:
        """
        Process a user query to extract intent and enhance it.
        
        Args:
            query: User query string
            
        Returns:
            Dictionary containing:
            - original_query: Original user query
            - enhanced_query: Enhanced query for better retrieval
            - scheme_name: Detected scheme name (if any)
            - field_type: Detected field type (if any)
            - intent: Query intent
        """
        original_query = query.strip()
        query_lower = original_query.lower()
        
        # Detect scheme name
        scheme_name = self._detect_scheme(query_lower)
        
        # Detect field type
        field_type = self._detect_field(query_lower)
        
        # Enhance query
        enhanced_query = self._enhance_query(original_query, scheme_name, field_type)
        
        # Determine intent
        intent = self._determine_intent(query_lower, field_type)
        
        return {
            'original_query': original_query,
            'enhanced_query': enhanced_query,
            'scheme_name': scheme_name,
            'field_type': field_type,
            'intent': intent
        }
    
    def _detect_scheme(self, query: str) -> Optional[str]:
        """Detect scheme name from query."""
        for pattern, scheme_name in self.SCHEME_PATTERNS.items():
            if re.search(pattern, query, re.IGNORECASE):
                return scheme_name
        return None
    
    def _detect_field(self, query: str) -> Optional[str]:
        """Detect field type from query."""
        for field, keywords in self.FIELD_KEYWORDS.items():
            for keyword in keywords:
                if keyword in query:
                    return field
        return None
    
    def _enhance_query(self, query: str, scheme_name: Optional[str], 
                      field_type: Optional[str]) -> str:
        """
        Enhance query with additional context for better retrieval.
        
        Args:
            query: Original query
            scheme_name: Detected scheme name
            field_type: Detected field type
            
        Returns:
            Enhanced query string
        """
        enhanced_parts = [query]
        
        # Add scheme context if detected
        if scheme_name:
            enhanced_parts.append(f"about {scheme_name}")
        
        # Add field context if detected
        if field_type:
            field_label = self._get_field_label(field_type)
            if field_label:
                enhanced_parts.append(f"regarding {field_label.lower()}")
        
        return " ".join(enhanced_parts)
    
    def _get_field_label(self, field_type: str) -> Optional[str]:
        """Get human-readable label for field type."""
        labels = {
            'expense_ratio': 'Expense Ratio',
            'minimum_sip': 'Minimum SIP',
            'exit_load': 'Exit Load',
            'nav': 'NAV',
            'tax_implication': 'Tax Implication'
        }
        return labels.get(field_type)
    
    def _determine_intent(self, query: str, field_type: Optional[str]) -> str:
        """Determine the intent of the query."""
        if field_type:
            return f"query_{field_type}"
        
        if any(word in query for word in ['what', 'tell me', 'explain', 'information']):
            return 'general_inquiry'
        
        if any(word in query for word in ['compare', 'difference', 'vs', 'versus']):
            return 'comparison'
        
        return 'general_inquiry'
    
    def is_factual_query(self, query: str) -> bool:
        """
        Check if query is asking for factual information.
        
        Args:
            query: User query
            
        Returns:
            True if query is factual, False if opinionated/advice-seeking
        """
        query_lower = query.lower()
        
        # Opinion/advice keywords to reject
        opinion_keywords = [
            'should i', 'is it good', 'is it worth', 'recommend', 'advice',
            'opinion', 'what do you think', 'portfolio', 'which is better',
            'best', 'worst', 'top', 'bottom'
        ]
        
        for keyword in opinion_keywords:
            if keyword in query_lower:
                return False
        
        # Factual keywords to accept
        factual_keywords = [
            'what is', 'what are', 'tell me', 'expense', 'sip', 'nav',
            'exit load', 'tax', 'minimum', 'maximum', 'current', 'latest'
        ]
        
        for keyword in factual_keywords:
            if keyword in query_lower:
                return True
        
        # Default to factual if no opinion keywords found
        return True


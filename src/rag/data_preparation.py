"""Prepare extracted data for vector store by converting to searchable chunks."""
from typing import List, Dict
from src.scraper.data_storage import DataStorage
from src.utils.token_counter import estimate_tokens, truncate_smart


class DataPreparation:
    """Prepare mutual fund data for vector storage."""
    
    def __init__(self, max_chunk_tokens: int = 500):
        """
        Initialize the data preparation service.
        
        Args:
            max_chunk_tokens: Maximum tokens per chunk (default: 500)
        """
        self.max_chunk_tokens = max_chunk_tokens
    
    def prepare_chunks_from_scheme(self, scheme_data: Dict) -> List[Dict]:
        """
        Convert a scheme's data into searchable text chunks.
        
        Args:
            scheme_data: Dictionary containing scheme information
            
        Returns:
            List of dictionaries, each containing:
            - text: Searchable text chunk
            - metadata: Metadata including source_url, scheme_name, field_name
        """
        chunks = []
        scheme_name = scheme_data.get('scheme_name', 'Unknown')
        source_url = scheme_data.get('source_url', '')
        category = scheme_data.get('category', '')
        
        # Base metadata for all chunks from this scheme
        base_metadata = {
            'scheme_name': scheme_name,
            'category': category,
            'source_url': source_url,
            'extracted_at': scheme_data.get('extracted_at', '')
        }
        
        # Create chunks for each field
        fields = {
            'expense_ratio': 'Expense Ratio',
            'minimum_sip': 'Minimum SIP',
            'exit_load': 'Exit Load',
            'nav': 'NAV',
            'tax_implication': 'Tax Implication'
        }
        
        for field_key, field_label in fields.items():
            value = scheme_data.get(field_key)
            if value and value != 'None' and value is not None:
                # Convert value to string
                value_str = str(value)
                
                # Truncate value if it's too long (especially for tax_implication which can be lengthy)
                value_tokens = estimate_tokens(value_str)
                if value_tokens > self.max_chunk_tokens:
                    # Truncate the value to fit within token limit
                    value_str, _ = truncate_smart(value_str, self.max_chunk_tokens, preserve_end=False)
                
                # Create a searchable text chunk
                text = self._create_chunk_text(scheme_name, field_label, value_str, category)
                
                # Final check: truncate the entire chunk if still too long
                text_tokens = estimate_tokens(text)
                if text_tokens > self.max_chunk_tokens:
                    text, _ = truncate_smart(text, self.max_chunk_tokens, preserve_end=False)
                
                metadata = {
                    **base_metadata,
                    'field_name': field_key,
                    'field_label': field_label,
                    'field_value': value_str
                }
                
                chunks.append({
                    'text': text,
                    'metadata': metadata
                })
        
        # Also create a comprehensive chunk with all information
        comprehensive_text = self._create_comprehensive_chunk(scheme_data)
        if comprehensive_text:
            # Truncate comprehensive chunk if too long
            comp_tokens = estimate_tokens(comprehensive_text)
            if comp_tokens > self.max_chunk_tokens:
                comprehensive_text, _ = truncate_smart(comprehensive_text, self.max_chunk_tokens, preserve_end=False)
            
            chunks.append({
                'text': comprehensive_text,
                'metadata': {
                    **base_metadata,
                    'field_name': 'comprehensive',
                    'field_label': 'All Information'
                }
            })
        
        return chunks
    
    def _create_chunk_text(self, scheme_name: str, field_label: str, value: str, category: str) -> str:
        """
        Create a searchable text chunk for a specific field.
        
        Args:
            scheme_name: Name of the scheme
            field_label: Label of the field (e.g., "Expense Ratio")
            value: Value of the field
            category: Category of the scheme
            
        Returns:
            Formatted text chunk
        """
        return f"{scheme_name} ({category}) {field_label}: {value}"
    
    def _create_comprehensive_chunk(self, scheme_data: Dict) -> str:
        """
        Create a comprehensive text chunk with all scheme information.
        
        Args:
            scheme_data: Dictionary containing all scheme data
            
        Returns:
            Comprehensive text description
        """
        scheme_name = scheme_data.get('scheme_name', 'Unknown')
        category = scheme_data.get('category', '')
        
        parts = [f"{scheme_name} is a {category} mutual fund scheme."]
        
        if scheme_data.get('expense_ratio'):
            parts.append(f"Expense ratio: {scheme_data['expense_ratio']}")
        
        if scheme_data.get('minimum_sip'):
            parts.append(f"Minimum SIP: {scheme_data['minimum_sip']}")
        
        if scheme_data.get('nav'):
            parts.append(f"Current NAV: {scheme_data['nav']}")
        
        if scheme_data.get('exit_load'):
            parts.append(f"Exit load: {scheme_data['exit_load']}")
        
        if scheme_data.get('tax_implication'):
            parts.append(f"Tax implication: {scheme_data['tax_implication']}")
        
        return " ".join(parts)
    
    def load_and_prepare_all_schemes(self, data_dir: str = "data") -> List[Dict]:
        """
        Load all schemes from storage and prepare them as chunks.
        
        Args:
            data_dir: Directory containing processed data
            
        Returns:
            List of all chunks with text and metadata
        """
        storage = DataStorage(data_dir=data_dir)
        schemes = storage.load_latest_data()
        
        if not schemes:
            raise ValueError("No scheme data found. Please run extract_data.py first.")
        
        all_chunks = []
        for scheme in schemes:
            chunks = self.prepare_chunks_from_scheme(scheme)
            all_chunks.extend(chunks)
        
        print(f"Prepared {len(all_chunks)} chunks from {len(schemes)} schemes")
        return all_chunks


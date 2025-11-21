"""Data storage module for saving extracted mutual fund data."""
import json
import os
from pathlib import Path
from typing import Dict, List
from datetime import datetime


class DataStorage:
    """Handle storage of extracted mutual fund data."""
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize data storage.
        
        Args:
            data_dir: Base directory for storing data
        """
        self.data_dir = Path(data_dir)
        self.raw_dir = self.data_dir / "raw"
        self.processed_dir = self.data_dir / "processed"
        
        # Create directories if they don't exist
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
    
    def save_raw_html(self, url: str, html: str) -> str:
        """
        Save raw HTML content.
        
        Args:
            url: Source URL
            html: HTML content
            
        Returns:
            Path to saved file
        """
        # Create filename from URL
        url_slug = url.split('/')[-1] or url.split('/')[-2]
        filename = f"{url_slug}_{datetime.now().strftime('%Y%m%d')}.html"
        filepath = self.raw_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return str(filepath)
    
    def save_extracted_data(self, data: Dict) -> str:
        """
        Save extracted structured data.
        
        Args:
            data: Extracted data dictionary
            
        Returns:
            Path to saved file
        """
        # Create filename from scheme name and date
        scheme_slug = data['scheme_name'].lower().replace(' ', '_')
        filename = f"{scheme_slug}_{datetime.now().strftime('%Y%m%d')}.json"
        filepath = self.processed_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return str(filepath)
    
    def save_all_data(self, all_data: List[Dict]) -> str:
        """
        Save all extracted data in a single consolidated file.
        
        Args:
            all_data: List of extracted data dictionaries
            
        Returns:
            Path to saved file
        """
        filename = f"all_schemes_{datetime.now().strftime('%Y%m%d')}.json"
        filepath = self.processed_dir / filename
        
        consolidated = {
            'extracted_at': datetime.now().isoformat(),
            'total_schemes': len(all_data),
            'schemes': all_data
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(consolidated, f, indent=2, ensure_ascii=False)
        
        return str(filepath)
    
    def load_latest_data(self) -> List[Dict]:
        """
        Load the most recent consolidated data file.
        
        Returns:
            List of scheme data dictionaries
        """
        # Find all consolidated files
        pattern = "all_schemes_*.json"
        files = list(self.processed_dir.glob(pattern))
        
        if not files:
            return []
        
        # Get the most recent file
        latest_file = max(files, key=lambda p: p.stat().st_mtime)
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return data.get('schemes', [])


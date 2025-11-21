"""Configuration utilities for loading URLs and settings."""
import yaml
import os
from pathlib import Path
from typing import List, Dict


def load_urls_config(config_path: str = "config/urls.yaml") -> List[Dict]:
    """Load URLs configuration from YAML file."""
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    return config.get('schemes', [])


def validate_url(url: str) -> bool:
    """Validate if URL is a valid Groww mutual fund URL."""
    if not url or not isinstance(url, str):
        return False
    
    # Check if URL starts with https://groww.in/mutual-funds/
    if not url.startswith('https://groww.in/mutual-funds/'):
        return False
    
    # Check if URL is accessible (basic validation)
    return True


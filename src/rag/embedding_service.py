"""Embedding service for generating vector embeddings from text."""
from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np
import os
import torch


class EmbeddingService:
    """Service for generating text embeddings."""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize the embedding service.
        
        Args:
            model_name: Name of the sentence transformer model to use
        """
        print(f"Loading embedding model: {model_name}")
        
        # Fix for PyTorch meta tensor issue
        # Set environment variables to avoid meta tensor problems
        os.environ['HF_HUB_DISABLE_EXPERIMENTAL_WARNING'] = '1'
        
        # Disable meta device to avoid the error
        try:
            # Try loading with device_map='cpu' to avoid GPU/meta issues
            self.model = SentenceTransformer(
                model_name,
                device='cpu'  # Force CPU to avoid device transfer issues
            )
        except Exception as e:
            # If that fails, try with trust_remote_code
            try:
                self.model = SentenceTransformer(
                    model_name,
                    device='cpu',
                    trust_remote_code=True
                )
            except Exception as e2:
                # Last resort: try without device specification
                print(f"Warning: Could not load with device='cpu', trying default: {e2}")
                self.model = SentenceTransformer(model_name)
        
        # Ensure model is on CPU and in eval mode
        if hasattr(self.model, 'to'):
            try:
                self.model.eval()
            except:
                pass
        
        self.model_name = model_name
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text to embed
            
        Returns:
            List of float values representing the embedding vector
        """
        if not text or not isinstance(text, str):
            raise ValueError("Text must be a non-empty string")
        
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (batch processing).
        
        Args:
            texts: List of input texts to embed
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        # Filter out empty texts
        valid_texts = [text for text in texts if text and isinstance(text, str)]
        if not valid_texts:
            return []
        
        embeddings = self.model.encode(valid_texts, convert_to_numpy=True, show_progress_bar=True)
        return embeddings.tolist()
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings produced by this model.
        
        Returns:
            Dimension of the embedding vectors
        """
        # Test with a dummy text
        test_embedding = self.generate_embedding("test")
        return len(test_embedding)


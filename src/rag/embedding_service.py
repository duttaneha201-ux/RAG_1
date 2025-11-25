"""Embedding service for generating vector embeddings from text."""
import os

# Fix for PyTorch meta tensor issue - set BEFORE any torch imports
os.environ['HF_HUB_DISABLE_EXPERIMENTAL_WARNING'] = '1'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'
os.environ['HF_HUB_DISABLE_ACCELERATE'] = '1'

# Import torch AFTER setting env vars
import torch

# Patch torch.nn.Module.to() to handle meta tensors BEFORE importing SentenceTransformer
_original_module_to = torch.nn.Module.to

def _patched_module_to(self, *args, **kwargs):
    """Patched to() method that handles meta tensors using to_empty()."""
    # Check if any parameters are meta tensors BEFORE calling .to()
    has_meta = False
    try:
        # Check recursively through all parameters and buffers
        for param in self.parameters(recurse=True):
            if hasattr(param, 'is_meta') and param.is_meta:
                has_meta = True
                break
        # Also check buffers
        if not has_meta:
            for buffer in self.buffers(recurse=True):
                if hasattr(buffer, 'is_meta') and buffer.is_meta:
                    has_meta = True
                    break
    except:
        pass
    
    # If meta tensors detected, use to_empty()
    if has_meta:
        device = args[0] if args else kwargs.get('device', 'cpu')
        dtype = kwargs.get('dtype', None)
        
        if hasattr(self, 'to_empty'):
            try:
                # Use to_empty to properly handle meta tensors
                result = self.to_empty(device=device)
                if dtype is not None:
                    result = result.to(dtype=dtype)
                return result
            except Exception:
                # If to_empty fails, continue to try normal .to()
                pass
    
    # Try normal .to() call
    try:
        return _original_module_to(self, *args, **kwargs)
    except RuntimeError as e:
        error_str = str(e).lower()
        if "meta" in error_str and ("to_empty" in error_str or "no data" in error_str or "cannot copy" in error_str):
            device = args[0] if args else kwargs.get('device', 'cpu')
            dtype = kwargs.get('dtype', None)
            
            # Try using to_empty() as last resort
            if hasattr(self, 'to_empty'):
                try:
                    result = self.to_empty(device=device)
                    if dtype is not None:
                        result = result.to(dtype=dtype)
                    return result
                except:
                    pass
            
            # If all else fails, raise with helpful message
            raise RuntimeError(
                f"Meta tensor error: Cannot copy out of meta tensor. "
                f"Please clear HuggingFace cache: {os.path.expanduser('~/.cache/huggingface/')}"
            ) from e
        raise

# Apply the patch
torch.nn.Module.to = _patched_module_to

# NOW import SentenceTransformer after the patch
from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np


class EmbeddingService:
    """Service for generating text embeddings."""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize the embedding service.
        
        Args:
            model_name: Name of the sentence transformer model to use
        """
        print(f"Loading embedding model: {model_name}")
        
        # Additional PyTorch meta tensor fixes
        # Disable meta device globally
        os.environ['HF_HUB_DISABLE_EXPERIMENTAL_WARNING'] = '1'
        os.environ['TOKENIZERS_PARALLELISM'] = 'false'
        os.environ['HF_HUB_DISABLE_ACCELERATE'] = '1'
        
        # Fix meta tensor issue by ensuring proper loading
        # Prevent transformers from using meta device
        try:
            # Try loading with explicit parameters to avoid meta device
            # Set device_map to None to prevent meta device usage
            from transformers import AutoModel, AutoTokenizer
            import gc
            gc.collect()
            
            # Load model directly without meta device
            tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                use_fast=True
            )
            
            # Load model without meta device - this is the key fix
            auto_model = AutoModel.from_pretrained(
                model_name,
                torch_dtype=torch.float32,
                low_cpu_mem_usage=False,  # Important: False prevents meta device
                device_map=None,  # Critical: None prevents meta device
                _fast_init=False  # Avoid fast init which can use meta
            )
            
            # Model should already be on CPU, but ensure it
            if next(auto_model.parameters()).device.type != 'cpu':
                auto_model = auto_model.cpu()
            
            # Build SentenceTransformer from components
            from sentence_transformers.models import Transformer, Pooling
            word_embedding_model = Transformer(model_name, max_seq_length=256)
            word_embedding_model.auto_model = auto_model
            word_embedding_model.tokenizer = tokenizer
            
            pooling_model = Pooling(word_embedding_model.get_word_embedding_dimension())
            self.model = SentenceTransformer(modules=[word_embedding_model, pooling_model])
            
            # Ensure model is on CPU (should already be)
            try:
                # This should work because model is already loaded without meta tensors
                self.model = self.model.to('cpu')
            except Exception as move_error:
                # If move fails, model is likely already on CPU
                if 'meta' in str(move_error).lower():
                    print("[WARNING] Meta tensor detected during move, but model should be usable")
                pass
            
            print("[OK] Model loaded successfully without meta device")
            
        except Exception as e1:
            error_str1 = str(e1).lower()
            print(f"[WARNING] Direct loading failed: {str(e1)[:150]}")
            
            # If direct loading fails, try standard SentenceTransformer load
            # (our patch should handle meta tensor issues)
            try:
                print("[INFO] Trying standard SentenceTransformer loading...")
                self.model = SentenceTransformer(
                    model_name,
                    device='cpu'
                )
                print("[OK] Model loaded with standard method")
            except Exception as e2:
                error_str2 = str(e2).lower()
                
                # Check if it's a meta tensor error
                if "meta" in error_str2 or "to_empty" in error_str2 or "no data" in error_str2 or "cannot copy" in error_str2:
                    # Provide helpful error with fix instructions
                    import shutil
                    cache_dir = os.path.expanduser('~/.cache/huggingface')
                    
                    error_msg = (
                        f"Failed to load embedding model '{model_name}' due to PyTorch meta tensor issue.\n\n"
                        f"**Errors:**\n"
                        f"1. Direct load: {str(e1)[:150]}\n"
                        f"2. Standard load: {str(e2)[:150]}\n\n"
                        f"**Solution - Clear HuggingFace cache:**\n"
                        f"1. Close this application\n"
                        f"2. Delete this folder: {cache_dir}\n"
                        f"3. Or run: python -c \"import shutil; shutil.rmtree(r'{cache_dir}', ignore_errors=True)\"\n"
                        f"4. Restart the application\n\n"
                        f"The cache may contain corrupted model files with meta tensors."
                    )
                    raise ValueError(error_msg) from e2
                else:
                    # Re-raise if it's a different error
                    raise ValueError(f"Failed to load embedding model: {str(e2)}") from e2
        
        # Ensure model is in eval mode
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


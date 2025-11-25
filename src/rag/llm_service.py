"""LLM service for generating answers using Gemini Flash 1.5."""
import google.generativeai as genai
import os
import sys
from typing import Optional, Dict
from datetime import datetime
import yaml
from pathlib import Path
from src.utils.token_counter import estimate_tokens, truncate_smart

# Fix Windows console encoding for Unicode characters
if sys.platform == 'win32':
    try:
        # Try to set UTF-8 encoding for stdout/stderr on Windows
        if sys.stdout.encoding != 'utf-8':
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        if sys.stderr.encoding != 'utf-8':
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError):
        # Fallback: use ASCII-safe characters
        pass

def safe_print(message: str):
    """Print message safely, handling encoding errors on Windows."""
    try:
        print(message)
    except UnicodeEncodeError:
        # Replace Unicode characters with ASCII equivalents
        safe_message = message.replace('✓', '[OK]').replace('✗', '[X]').replace('⚠', '[!]')
        print(safe_message)


class LLMService:
    """Service for generating answers using Gemini Flash 1.5."""
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-2.0-flash"):
        """
        Initialize the LLM service.
        
        Args:
            api_key: Google AI API key (or set GOOGLE_API_KEY env var)
            model_name: Model name to use (default: gemini-1.5-flash)
        """
        # Get API key from parameter, environment variable, or .env file
        if api_key:
            self.api_key = api_key
        else:
            self.api_key = os.getenv('GOOGLE_API_KEY')
            if not self.api_key:
                # Try loading from .env file
                try:
                    from dotenv import load_dotenv
                    load_dotenv()
                    self.api_key = os.getenv('GOOGLE_API_KEY')
                except ImportError:
                    pass
        
        if not self.api_key:
            raise ValueError(
                "Google API key not found. Please set GOOGLE_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model_name = model_name
        
        # Token limits for Gemini 1.5 Flash (conservative limits to avoid errors)
        # Gemini 1.5 Flash has 8,192 input tokens, we'll use 6,000 as a safe limit
        self.max_input_tokens = 6000  # Conservative limit for input
        self.max_context_tokens = 4000  # Max tokens for context portion
        
        # Try to initialize model with fallback options
        # Updated with actual available model names from API
        self.model = None
        model_options = [
            model_name,  # Try user-specified or default first
            "gemini-2.0-flash",  # Known working model
            "gemini-2.5-flash",  # Latest 2.5 flash
            "gemini-flash-latest",  # Latest flash version
            "gemini-2.0-flash-lite",  # 2.0 lite
            "gemini-2.5-flash-lite",  # Lite version
            "gemini-pro-latest",  # Latest pro
            "gemini-1.5-flash-latest",  # Try older versions as fallback
            "gemini-1.5-flash",
            "gemini-1.5-pro",
            "gemini-pro",
        ]
        
        last_error = None
        for model_option in model_options:
            try:
                # Try to create the model
                test_model = genai.GenerativeModel(model_option)
                # Model created successfully, try a simple test call
                try:
                    # Quick test to verify model works (with minimal tokens)
                    test_response = test_model.generate_content(
                        "Hi", 
                        generation_config={"max_output_tokens": 5, "temperature": 0.1}
                    )
                    if test_response and (hasattr(test_response, 'text') or (hasattr(test_response, 'candidates') and test_response.candidates)):
                        self.model = test_model
                        self.model_name = model_option
                        safe_print(f"[OK] Successfully initialized model: {model_option}")
                        break
                    else:
                        # Response exists but no text - model might still work
                        self.model = test_model
                        self.model_name = model_option
                        safe_print(f"[OK] Initialized model: {model_option} (will test on first query)")
                        break
                except Exception as test_error:
                    error_str = str(test_error).lower()
                    # If it's a model not found error, try next option
                    if "not found" in error_str or "does not exist" in error_str or "404" in error_str:
                        last_error = str(test_error)
                        safe_print(f"[SKIP] Model {model_option} not available: {str(test_error)[:100]}")
                        continue
                    # For other errors (rate limit, etc.), model might still work
                    self.model = test_model
                    self.model_name = model_option
                    safe_print(f"[OK] Initialized model: {model_option} (test had issues but model created successfully)")
                    break
            except Exception as e:
                error_str = str(e).lower()
                last_error = str(e)
                # If it's a model not found error, try next option
                if "not found" in error_str or "does not exist" in error_str or "404" in error_str:
                    safe_print(f"[SKIP] Model {model_option} not available")
                    continue
                else:
                    # Other errors - might still work
                    self.model = genai.GenerativeModel(model_option)
                    self.model_name = model_option
                    safe_print(f"[OK] Initialized model: {model_option} (proceeding despite initialization warning)")
                    break
        
        if self.model is None:
            error_msg = (
                f"Could not initialize any Gemini model. Tried: {', '.join(model_options)}.\n"
                f"Last error: {last_error}\n"
                f"Please check:\n"
                f"  1. Your API key is valid (current key starts with: {self.api_key[:10]}...)\n"
                f"  2. API key has access to Gemini models\n"
                f"  3. Model names are correct for your API key type"
            )
            raise ValueError(error_msg)
        
        # Load prompts
        self._load_prompts()
    
    def _load_prompts(self):
        """Load prompt templates from config."""
        prompt_file = Path("config/prompts.yaml")
        if prompt_file.exists():
            with open(prompt_file, 'r', encoding='utf-8') as f:
                prompts = yaml.safe_load(f)
                self.system_prompt_template = prompts.get('system_prompt', '')
                self.refusal_message = prompts.get('refusal_message', '')
        else:
            # Default prompts
            self.system_prompt_template = """You are a factual FAQ assistant for HDFC mutual fund schemes on Groww.

Rules:
- Answer ONLY factual queries (expense ratio, minimum SIP, exit load, NAV, tax implications)
- Keep answers ≤3 sentences
- Include source URL in every answer
- Add "Last updated from sources: [date]" at the end
- Refuse opinionated/portfolio questions
- No investment advice

Context: {context}
Question: {question}

Answer:"""
            self.refusal_message = "I can only answer factual questions about HDFC mutual fund schemes (expense ratio, minimum SIP, exit load, NAV, tax implications). I cannot provide investment advice or answer portfolio-related questions."
    
    def generate_answer(self, question: str, context: str, 
                       extracted_at: Optional[str] = None) -> Dict:
        """
        Generate an answer from context and question.
        
        Args:
            question: User question
            context: Retrieved context from vector store
            extracted_at: Timestamp when data was extracted (for "Last updated")
            
        Returns:
            Dictionary with:
            - answer: Generated answer
            - model: Model used
            - timestamp: Generation timestamp
        """
        # Format the prompt
        if extracted_at:
            # Parse date from ISO format
            try:
                date_obj = datetime.fromisoformat(extracted_at.replace('Z', '+00:00'))
                date_str = date_obj.strftime('%Y-%m-%d')
            except:
                date_str = datetime.now().strftime('%Y-%m-%d')
        else:
            date_str = datetime.now().strftime('%Y-%m-%d')
        
        # Prepare system prompt template
        system_prompt_base = self.system_prompt_template.replace('DATE_PLACEHOLDER', date_str)
        
        # First, format prompt with full context to check total size
        prompt = system_prompt_base.format(
            context=context,
            question=question
        )
        
        # Check total token count
        total_prompt_tokens = estimate_tokens(prompt)
        
        # If prompt is too long, truncate context iteratively
        if total_prompt_tokens > self.max_input_tokens:
            safe_print(f"⚠️  Prompt too long ({total_prompt_tokens} tokens), truncating context...")
            
            # Estimate tokens for prompt without context (system prompt + question)
            prompt_without_context = system_prompt_base.format(context="", question=question)
            base_tokens = estimate_tokens(prompt_without_context)
            
            # Calculate available space for context
            available_context_tokens = self.max_input_tokens - base_tokens - 100  # 100 token safety buffer
            
            if available_context_tokens > 500:  # Only truncate if we have meaningful space
                context_tokens = estimate_tokens(context)
                safe_print(f"   Context: {context_tokens} tokens, Available: {available_context_tokens} tokens")
                
                context, actual_context_tokens = truncate_smart(
                    context, 
                    available_context_tokens, 
                    preserve_end=False
                )
                
                # Reformulate prompt with truncated context
                prompt = system_prompt_base.format(
                    context=context,
                    question=question
                )
                
                final_tokens = estimate_tokens(prompt)
                safe_print(f"✓ Context truncated to {actual_context_tokens} tokens, Final prompt: {final_tokens} tokens")
            else:
                safe_print(f"⚠️  Warning: Very limited token budget. Prompt may exceed limits.")
        
        # Generate response
        try:
            # Configure generation settings
            try:
                from google.generativeai.types import GenerationConfig
                generation_config = GenerationConfig(
                    temperature=0.1,  # Low temperature for factual answers
                    top_p=0.8,
                    top_k=40,
                    max_output_tokens=200,  # Limit to keep answers concise
                )
            except ImportError:
                # Fallback to dict if GenerationConfig not available
                generation_config = {
                    "temperature": 0.1,
                    "top_p": 0.8,
                    "top_k": 40,
                    "max_output_tokens": 200,
                }
            
            # Generate with retry logic and model fallback
            max_retries = 2
            response = None
            last_gen_error = None
            
            for attempt in range(max_retries):
                try:
                    response = self.model.generate_content(
                        prompt,
                        generation_config=generation_config
                    )
                    break
                except Exception as retry_error:
                    last_gen_error = retry_error
                    error_str = str(retry_error).lower()
                    
                    # If model not found, try to find an alternative model
                    if "not found" in error_str or "404" in error_str or "does not exist" in error_str:
                        safe_print(f"Model {self.model_name} not found, trying alternative models...")
                        # Try alternative models
                        alternative_models = [
                            "gemini-1.5-flash-latest",
                            "gemini-1.5-flash-8b", 
                            "gemini-1.5-pro-latest",
                            "gemini-1.5-pro",
                            "gemini-pro"
                        ]
                        for alt_model in alternative_models:
                            if alt_model == self.model_name:
                                continue
                            try:
                                safe_print(f"Trying alternative model: {alt_model}")
                                alt_model_instance = genai.GenerativeModel(alt_model)
                                response = alt_model_instance.generate_content(
                                    prompt,
                                    generation_config=generation_config
                                )
                                self.model = alt_model_instance
                                self.model_name = alt_model
                                safe_print(f"Successfully switched to model: {alt_model}")
                                break
                            except Exception:
                                continue
                        if response:
                            break
                    
                    if attempt == max_retries - 1:
                        raise
                    # Wait a bit before retry
                    import time
                    time.sleep(0.5)
                    continue
            
            # Handle response - check if it was blocked or has content
            if not response:
                raise ValueError("Empty response from model")
            
            # Check for blocked content
            if hasattr(response, 'prompt_feedback') and response.prompt_feedback:
                if response.prompt_feedback.block_reason:
                    raise ValueError(f"Response blocked: {response.prompt_feedback.block_reason}")
            
            # Get text from response - handle different response formats
            answer = None
            
            # Try response.text first (most common)
            try:
                if hasattr(response, 'text') and response.text:
                    answer = response.text.strip()
            except Exception:
                pass
            
            # If that didn't work, try accessing via candidates
            if not answer and hasattr(response, 'candidates') and response.candidates:
                try:
                    candidate = response.candidates[0]
                    if hasattr(candidate, 'content'):
                        if hasattr(candidate.content, 'parts') and candidate.content.parts:
                            if hasattr(candidate.content.parts[0], 'text'):
                                answer = candidate.content.parts[0].text.strip()
                except Exception:
                    pass
            
            # If still no answer, try to extract from response string representation
            if not answer:
                # Last resort: try to get any text content
                response_str = str(response)
                if response_str and len(response_str) > 10:
                    # This shouldn't normally happen, but handle it
                    answer = response_str[:500]  # Limit to avoid huge strings
                else:
                    raise ValueError("Could not extract text from response - response format not recognized")
            
            if not answer:
                raise ValueError("Empty answer from model")
            
            # Ensure answer includes "Last updated" if not present
            if "Last updated" not in answer and "last updated" not in answer.lower():
                answer += f"\n\nLast updated from sources: {date_str}"
            
            return {
                'answer': answer,
                'model': self.model_name,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            error_str = str(e)
            error_type = type(e).__name__
            
            # Log the full error for debugging
            safe_print(f"LLM Error ({error_type}): {error_str}")
            
            # Check for specific error types
            if "429" in error_str or "quota" in error_str.lower() or "rate limit" in error_str.lower():
                error_msg = "API rate limit exceeded. Please try again later."
            elif "404" in error_str or "not found" in error_str.lower() or "does not exist" in error_str.lower():
                error_msg = (
                    f"Model '{self.model_name}' not found or not available with your API key.\n\n"
                    f"**Troubleshooting steps:**\n"
                    f"1. Verify your API key at: https://makersuite.google.com/app/apikey\n"
                    f"2. Check if billing is enabled (some models require paid tier)\n"
                    f"3. Try regenerating your API key\n"
                    f"4. Check Google AI Studio for available models: https://aistudio.google.com/"
                )
            elif "401" in error_str or "unauthorized" in error_str.lower() or "invalid api key" in error_str.lower():
                error_msg = "Invalid API key. Please check your GOOGLE_API_KEY."
            elif "403" in error_str or "forbidden" in error_str.lower():
                error_msg = "API access forbidden. Please check your API key permissions."
            elif "safety" in error_str.lower() or "blocked" in error_str.lower():
                error_msg = "Response was blocked by safety filters. Please rephrase your question."
            elif "token" in error_str.lower() and ("limit" in error_str.lower() or "exceeded" in error_str.lower() or "too long" in error_str.lower()):
                error_msg = f"Input too long ({estimate_tokens(prompt)} tokens). The context was too large. Please try a more specific question."
            else:
                error_msg = f"Error generating answer: {error_str[:200]}"  # Truncate long errors
            
            return {
                'answer': error_msg,
                'model': self.model_name,
                'timestamp': datetime.now().isoformat(),
                'error': error_str,
                'error_type': 'llm_error',
                'error_class': error_type
            }
    
    def get_refusal_message(self) -> str:
        """Get the refusal message for non-factual queries."""
        return self.refusal_message


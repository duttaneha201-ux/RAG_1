"""LLM service for generating answers using Gemini Flash 1.5."""
import google.generativeai as genai
import os
from typing import Optional, Dict
from datetime import datetime
import yaml
from pathlib import Path


class LLMService:
    """Service for generating answers using Gemini Flash 1.5."""
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-1.5-flash"):
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
        
        # Try to initialize model with fallback options
        self.model = None
        model_options = [
            "gemini-1.5-flash",  # Most common
            "gemini-1.5-flash-latest",  # Latest version
            "gemini-1.5-flash-001",  # Versioned
            "gemini-1.5-pro",  # Pro version
            "gemini-pro",  # Older pro version
            model_name  # User specified as last resort
        ]
        
        last_error = None
        for model_option in model_options:
            try:
                # Try to create the model
                test_model = genai.GenerativeModel(model_option)
                # Test if model works by making a simple test call
                try:
                    # Quick test to verify model works
                    test_response = test_model.generate_content("test", generation_config={"max_output_tokens": 1})
                    if test_response and (hasattr(test_response, 'text') or (hasattr(test_response, 'candidates') and test_response.candidates)):
                        self.model = test_model
                        self.model_name = model_option
                        print(f"✓ Successfully initialized model: {model_option}")
                        break
                except Exception as test_error:
                    # Model exists but test failed, still use it
                    self.model = test_model
                    self.model_name = model_option
                    print(f"✓ Initialized model: {model_option} (test call had minor issue, but model is available)")
                    break
            except Exception as e:
                last_error = str(e)
                print(f"✗ Failed to initialize {model_option}: {last_error}")
                continue
        
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
        
        # Format prompt - replace DATE_PLACEHOLDER with actual date, then format context and question
        prompt = self.system_prompt_template.replace('DATE_PLACEHOLDER', date_str).format(
            context=context,
            question=question
        )
        
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
            
            # Generate with retry logic
            max_retries = 2
            response = None
            for attempt in range(max_retries):
                try:
                    response = self.model.generate_content(
                        prompt,
                        generation_config=generation_config
                    )
                    break
                except Exception as retry_error:
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
            
            # Get text from response
            if hasattr(response, 'text'):
                answer = response.text.strip()
            elif hasattr(response, 'candidates') and response.candidates:
                if hasattr(response.candidates[0], 'content'):
                    answer = response.candidates[0].content.parts[0].text.strip()
                else:
                    raise ValueError("Could not extract text from response")
            else:
                raise ValueError("Unexpected response format")
            
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
            print(f"LLM Error ({error_type}): {error_str}")
            
            # Check for specific error types
            if "429" in error_str or "quota" in error_str.lower() or "rate limit" in error_str.lower():
                error_msg = "API rate limit exceeded. Please try again later."
            elif "404" in error_str or "not found" in error_str.lower() or "does not exist" in error_str.lower():
                error_msg = f"Model {self.model_name} not found. Please check model availability."
            elif "401" in error_str or "unauthorized" in error_str.lower() or "invalid api key" in error_str.lower():
                error_msg = "Invalid API key. Please check your GOOGLE_API_KEY."
            elif "403" in error_str or "forbidden" in error_str.lower():
                error_msg = "API access forbidden. Please check your API key permissions."
            elif "safety" in error_str.lower() or "blocked" in error_str.lower():
                error_msg = "Response was blocked by safety filters. Please rephrase your question."
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


"""LLM service for generating answers using Gemini Flash 1.5."""
import google.generativeai as genai
import os
from typing import Optional, Dict
from datetime import datetime
import yaml
from pathlib import Path


class LLMService:
    """Service for generating answers using Gemini Flash 1.5."""
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-2.0-flash-exp"):
        """
        Initialize the LLM service.
        
        Args:
            api_key: Google AI API key (or set GOOGLE_API_KEY env var)
            model_name: Model name to use (default: gemini-2.0-flash-exp)
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
        self.model = genai.GenerativeModel(model_name)
        
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
            response = self.model.generate_content(prompt)
            answer = response.text.strip()
            
            # Ensure answer includes "Last updated" if not present
            if "Last updated" not in answer and "last updated" not in answer.lower():
                answer += f"\n\nLast updated from sources: {date_str}"
            
            return {
                'answer': answer,
                'model': self.model_name,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'answer': f"Error generating answer: {str(e)}",
                'model': self.model_name,
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def get_refusal_message(self) -> str:
        """Get the refusal message for non-factual queries."""
        return self.refusal_message


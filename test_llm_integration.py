"""Test script for LLM integration with Gemini Flash 1.5."""
import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

# Load .env file first
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from src.rag.answer_generator import AnswerGenerator


def test_llm_integration():
    """Test the complete RAG pipeline with LLM."""
    print("=" * 60)
    print("Testing LLM Integration (Gemini Flash 1.5)")
    print("=" * 60)
    
    # Check for API key (after loading .env)
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key or api_key == 'your_api_key_here':
        print("\n[ERROR] GOOGLE_API_KEY not found or still has placeholder value!")
        print("Please:")
        print("  1. Open the .env file")
        print("  2. Replace 'your_api_key_here' with your actual API key")
        print("  3. Get your API key from: https://makersuite.google.com/app/apikey")
        return
    
    try:
        generator = AnswerGenerator(api_key=api_key)
    except Exception as e:
        print(f"\n[ERROR] Failed to initialize AnswerGenerator: {e}")
        return
    
    test_queries = [
        "What is the expense ratio of HDFC Equity Fund?",
        "What is the minimum SIP for HDFC Large Cap Fund?",
        "What is the NAV of HDFC Mid Cap Fund?",
        "What is the exit load for HDFC Small Cap Fund?",
        "What are the tax implications for HDFC ELSS Fund?",
        "Should I invest in HDFC Equity Fund?",  # Should be rejected
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print('='*60)
        
        try:
            result = generator.generate_answer(query, n_results=3)
            
            print(f"\nAnswer:")
            print(f"  {result['answer']}")
            print(f"\nSource URL: {result.get('source_url', 'N/A')}")
            print(f"Is Factual: {result['is_factual']}")
            print(f"Model: {result.get('model', 'N/A')}")
            
            if result.get('retrieval_info'):
                print(f"\nRetrieval Info:")
                print(f"  Total Results: {result['retrieval_info'].get('total_results', 0)}")
                print(f"  Schemes: {', '.join(result['retrieval_info'].get('schemes', []))}")
        
        except Exception as e:
            print(f"\n[ERROR] Failed to generate answer: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("LLM Integration Test Complete")
    print("=" * 60)


if __name__ == "__main__":
    test_llm_integration()


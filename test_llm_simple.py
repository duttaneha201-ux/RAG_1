"""Simple test to verify LLM service works."""
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Load .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from src.rag.llm_service import LLMService

def test_llm():
    """Test LLM service directly."""
    print("Testing LLM Service...")
    print("=" * 60)
    
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("ERROR: GOOGLE_API_KEY not found in environment")
        return False
    
    print(f"API Key found: {api_key[:10]}...")
    
    try:
        print("\n1. Initializing LLM Service...")
        llm = LLMService(api_key=api_key)
        print(f"   ✓ Model initialized: {llm.model_name}")
        
        print("\n2. Testing simple generation...")
        test_context = "HDFC Equity Fund has an expense ratio of 1.5% and minimum SIP of ₹100."
        test_question = "What is the expense ratio of HDFC Equity Fund?"
        
        result = llm.generate_answer(
            question=test_question,
            context=test_context,
            extracted_at=None
        )
        
        print(f"   ✓ Answer generated")
        print(f"   Model used: {result.get('model', 'N/A')}")
        print(f"   Answer: {result.get('answer', 'N/A')[:200]}")
        
        if result.get('error'):
            print(f"\n   ⚠ Error occurred: {result.get('error')}")
            return False
        
        print("\n" + "=" * 60)
        print("✓ LLM Service is working correctly!")
        return True
        
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_llm()
    sys.exit(0 if success else 1)


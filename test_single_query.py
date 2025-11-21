"""Test script for a single query to avoid rate limits."""
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


def test_single_query(query: str = None):
    """Test the RAG pipeline with a single query."""
    print("=" * 60)
    print("HDFC Mutual Fund FAQ Assistant - Single Query Test")
    print("=" * 60)
    
    # Check for API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key or api_key == 'your_api_key_here':
        print("\n[ERROR] GOOGLE_API_KEY not found or still has placeholder value!")
        print("Please update your .env file with your actual API key.")
        return
    
    # Get query from user if not provided
    if not query:
        print("\nEnter your question (or press Enter for example query):")
        user_input = input("> ").strip()
        if user_input:
            query = user_input
        else:
            query = "What is the expense ratio of HDFC Equity Fund?"
            print(f"\nUsing example query: {query}")
    else:
        print(f"\nQuery: {query}")
    
    print("\n" + "=" * 60)
    print("Processing...")
    print("=" * 60)
    
    try:
        generator = AnswerGenerator(api_key=api_key)
    except Exception as e:
        print(f"\n[ERROR] Failed to initialize AnswerGenerator: {e}")
        return
    
    try:
        result = generator.generate_answer(query, n_results=3)
        
        print("\n" + "=" * 60)
        print("ANSWER")
        print("=" * 60)
        
        # Check if answer has error (rate limit)
        if 'error' in result.get('answer', '').lower() or '429' in result.get('answer', ''):
            print("\n[Rate Limit Notice]")
            print("The LLM is currently rate-limited, but retrieval is working!")
            print("\n" + "=" * 60)
            print("RETRIEVED INFORMATION (without LLM formatting)")
            print("=" * 60)
            
            # Show formatted context if available
            if result.get('formatted_context'):
                print("\nRetrieved Answer:")
                print("-" * 60)
                print(result['formatted_context'])
            
            # Show raw retrieval results
            retrieval_result = result.get('retrieval_result', {})
            if retrieval_result and retrieval_result.get('retrieval_result', {}).get('results'):
                print("\n" + "=" * 60)
                print("DETAILED RETRIEVAL RESULTS")
                print("=" * 60)
                for i, res in enumerate(retrieval_result['retrieval_result']['results'][:3], 1):
                    print(f"\n[Result {i}]")
                    print(f"Scheme: {res['metadata'].get('scheme_name', 'N/A')}")
                    print(f"Field: {res['metadata'].get('field_label', 'N/A')}")
                    print(f"Similarity: {res.get('similarity_score', 0):.4f}")
                    print(f"Content: {res['document']}")
                    print(f"Source: {res['metadata'].get('source_url', 'N/A')}")
            
            print("\n" + "=" * 60)
            print("NOTE")
            print("=" * 60)
            print("This is the raw retrieved information. When LLM is available,")
            print("it will format this into a concise 3-sentence answer.")
            print("\nPlease wait 30-60 seconds and try again, or check your API quota.")
        else:
            print(f"\n{result['answer']}")
        
        print("\n" + "=" * 60)
        print("DETAILS")
        print("=" * 60)
        print(f"Source URL: {result.get('source_url', 'N/A')}")
        print(f"Is Factual: {result['is_factual']}")
        print(f"Model: {result.get('model', 'N/A')}")
        
        if result.get('retrieval_info'):
            print(f"\nRetrieval Info:")
            print(f"  Total Results: {result['retrieval_info'].get('total_results', 0)}")
            schemes = result['retrieval_info'].get('schemes', [])
            if schemes:
                print(f"  Schemes Found: {', '.join(schemes)}")
        
        if result.get('source_urls'):
            print(f"\nAll Source URLs:")
            for url in result['source_urls']:
                print(f"  - {url}")
        
        print("\n" + "=" * 60)
        print("Test Complete")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n[ERROR] Failed to generate answer: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test single query with RAG system")
    parser.add_argument(
        "--query", "-q",
        type=str,
        help="Query to test (optional, will prompt if not provided)"
    )
    
    args = parser.parse_args()
    test_single_query(args.query)


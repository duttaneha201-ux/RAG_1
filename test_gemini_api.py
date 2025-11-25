"""Test script to diagnose Gemini API access and list available models."""
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Load .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import google.generativeai as genai

def test_gemini_api():
    """Test Gemini API access and list available models."""
    print("=" * 60)
    print("Gemini API Diagnostic Test")
    print("=" * 60)
    
    # Check API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key or api_key == 'your_api_key_here':
        print("\n[ERROR] GOOGLE_API_KEY not found or still has placeholder value!")
        print("Please update your .env file with your actual API key.")
        return False
    
    print(f"\n[OK] API Key found: {api_key[:10]}...{api_key[-4:]}")
    print(f"  API Key length: {len(api_key)} characters")
    
    # Configure Gemini
    try:
        genai.configure(api_key=api_key)
        print("\n[OK] Gemini API configured successfully")
    except Exception as e:
        print(f"\n[ERROR] Failed to configure Gemini API: {e}")
        return False
    
    # List available models via API
    print("\n" + "=" * 60)
    print("Listing Available Models from API")
    print("=" * 60)
    
    working_models = []
    available_model_names = []
    
    try:
        print("\nFetching available models...")
        models_list = list(genai.list_models())
        
        if models_list:
            print(f"\n[OK] Found {len(models_list)} available model(s):\n")
            for model in models_list:
                # Extract model name from full path
                model_name = model.name
                if '/' in model_name:
                    model_name = model_name.split('/')[-1]
                # Check if model supports generateContent
                supports_generate = True
                if hasattr(model, 'supported_generation_methods'):
                    supports_generate = 'generateContent' in model.supported_generation_methods
                
                status = "[SUPPORTED]" if supports_generate else "[NOT FOR GENERATION]"
                print(f"  - {model_name} {status}")
                if supports_generate:
                    available_model_names.append(model_name)
            
            print("\n" + "=" * 60)
            print("Testing Models that Support generateContent")
            print("=" * 60)
            
            # Test the models we found - prioritize common ones
            # Prioritize flash models (faster and usually have higher quota)
            priority_models = [m for m in available_model_names if 'flash' in m.lower() and 'lite' not in m.lower()]
            other_models = [m for m in available_model_names if m not in priority_models]
            test_order = priority_models[:3] + other_models[:2]  # Test 5 models
            
            for model_name in test_order:
                try:
                    print(f"\nTesting: {model_name}...", end=" ")
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content(
                        "Say hi", 
                        generation_config={"max_output_tokens": 5, "temperature": 0.1}
                    )
                    # Handle response properly
                    answer_text = None
                    try:
                        answer_text = response.text
                    except:
                        if hasattr(response, 'candidates') and response.candidates:
                            try:
                                answer_text = response.candidates[0].content.parts[0].text
                            except:
                                pass
                    
                    if answer_text and answer_text.strip():
                        print("[OK] WORKS!")
                        working_models.append(model_name)
                        break  # Found a working model, stop testing
                    else:
                        print("[X] No text in response")
                except Exception as e:
                    error_str = str(e).lower()
                    if "not found" in error_str or "404" in error_str:
                        print("[X] Not found")
                    elif "429" in error_str or "quota" in error_str:
                        print("[X] Quota exceeded (try again later)")
                    elif "403" in error_str or "forbidden" in error_str:
                        print("[X] Access forbidden")
                    else:
                        print(f"[X] Error: {str(e)[:70]}")
        
    except Exception as e:
        print(f"\n[WARNING] Could not list models: {str(e)[:150]}")
        print("\nTrying standard model names instead...")
        available_model_names = [
            "gemini-1.5-flash-latest",
            "gemini-1.5-flash",
            "gemini-1.5-pro-latest",
            "gemini-1.5-pro",
            "gemini-pro",
        ]
        
        for model_name in available_model_names:
            try:
                print(f"\nTesting: {model_name}...", end=" ")
                model = genai.GenerativeModel(model_name)
                response = model.generate_content("Hi", generation_config={"max_output_tokens": 5})
                if response and (hasattr(response, 'text') or (hasattr(response, 'candidates') and response.candidates)):
                    print("[OK] WORKS!")
                    working_models.append(model_name)
                else:
                    print("[X] No response")
            except Exception as e:
                error_str = str(e).lower()
                if "not found" in error_str or "404" in error_str:
                    print("[X] Not found")
                else:
                    print(f"[X] Error: {str(e)[:70]}")
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    if working_models:
        print(f"\n[OK] {len(working_models)} working model(s) found:")
        for model in working_models:
            print(f"  - {model}")
        print(f"\n[RECOMMENDATION] Use '{working_models[0]}' in your configuration")
        print("\nYou can update src/rag/llm_service.py to use this model.")
        return True
    else:
        print("\n[X] No working models found!")
        print("\nPossible issues:")
        print("1. API key may not have access to Gemini models")
        print("2. Billing may need to be enabled (some models require paid tier)")
        print("3. API key may be invalid, expired, or needs regeneration")
        print("\nNext steps:")
        print("1. Visit: https://makersuite.google.com/app/apikey")
        print("2. Check your API key status and regenerate if needed")
        print("3. Visit: https://aistudio.google.com/ to test your API key")
        print("4. Verify billing is enabled if required")
        return False

if __name__ == "__main__":
    success = test_gemini_api()
    sys.exit(0 if success else 1)

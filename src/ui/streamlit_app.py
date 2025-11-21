"""Streamlit UI for HDFC Mutual Fund FAQ Assistant."""
import streamlit as st
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Load .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from src.rag.answer_generator import AnswerGenerator
from datetime import datetime


# Page configuration
st.set_page_config(
    page_title="HDFC Mutual Fund FAQ Assistant",
    page_icon="💬",
    layout="wide"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "generator" not in st.session_state:
    st.session_state.generator = None


def initialize_generator():
    """Initialize the answer generator."""
    if st.session_state.generator is None:
        try:
            api_key = os.getenv('GOOGLE_API_KEY')
            if not api_key or api_key == 'your_api_key_here':
                st.error("⚠️ API key not configured. Please set GOOGLE_API_KEY in your .env file.")
                return None
            st.session_state.generator = AnswerGenerator(api_key=api_key)
            return st.session_state.generator
        except Exception as e:
            st.error(f"Failed to initialize: {str(e)}")
            return None
    return st.session_state.generator


def format_answer_with_fallback(result):
    """Format answer, showing retrieved info if LLM failed."""
    if 'error' in result.get('answer', '').lower() or '429' in result.get('answer', ''):
        # LLM rate-limited, show retrieved info
        answer_parts = []
        answer_parts.append("⚠️ **LLM temporarily unavailable, showing retrieved information:**\n\n")
        
        # Show formatted context
        if result.get('formatted_context'):
            answer_parts.append(result['formatted_context'])
        
        # Add source URLs
        if result.get('source_urls'):
            answer_parts.append("\n\n**Sources:**")
            for url in result['source_urls']:
                answer_parts.append(f"\n- {url}")
        
        return "\n".join(answer_parts)
    else:
        # Normal LLM answer
        answer = result['answer']
        # Ensure source URL is included
        if result.get('source_url') and result['source_url'] not in answer:
            answer += f"\n\n**Source:** {result['source_url']}"
        return answer


def main():
    """Main Streamlit app."""
    # Header
    st.title("💬 HDFC Mutual Fund FAQ Assistant")
    st.markdown("**Facts-only. No investment advice.**")
    
    # Welcome section
    st.markdown("---")
    st.markdown("### Welcome!")
    st.markdown("Ask factual questions about HDFC mutual fund schemes on Groww.")
    
    # Example questions
    st.markdown("#### Example Questions:")
    example_questions = [
        "What is the expense ratio of HDFC Equity Fund?",
        "What is the minimum SIP amount for HDFC Large Cap Fund?",
        "What are the tax implications for HDFC ELSS Fund?"
    ]
    
    # Display example questions as buttons
    cols = st.columns(3)
    for i, question in enumerate(example_questions):
        with cols[i]:
            if st.button(f"💡 {question[:40]}...", key=f"example_{i}", use_container_width=True):
                # Add to chat
                st.session_state.messages.append({
                    "role": "user",
                    "content": question
                })
                st.rerun()
    
    st.markdown("---")
    
    # Initialize generator
    generator = initialize_generator()
    if generator is None:
        st.stop()
    
    # Chat interface
    st.markdown("### Chat")
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Show source URL if available
            if message.get("source_url"):
                st.markdown(f"🔗 [Source]({message['source_url']})")
    
    # Chat input
    if prompt := st.chat_input("Ask a question about HDFC mutual funds..."):
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate answer
        with st.chat_message("assistant"):
            with st.spinner("Searching for information..."):
                try:
                    result = generator.generate_answer(prompt, n_results=3)
                    
                    # Format answer
                    answer = format_answer_with_fallback(result)
                    st.markdown(answer)
                    
                    # Store assistant message
                    assistant_message = {
                        "role": "assistant",
                        "content": answer,
                        "source_url": result.get('source_url')
                    }
                    st.session_state.messages.append(assistant_message)
                    
                    # Show additional info in expander
                    with st.expander("ℹ️ Details"):
                        st.write(f"**Is Factual:** {result['is_factual']}")
                        if result.get('retrieval_info'):
                            st.write(f"**Results Found:** {result['retrieval_info'].get('total_results', 0)}")
                            schemes = result['retrieval_info'].get('schemes', [])
                            if schemes:
                                st.write(f"**Schemes:** {', '.join(schemes)}")
                        if result.get('model'):
                            st.write(f"**Model:** {result['model']}")
                
                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })
    
    # Sidebar with info
    with st.sidebar:
        st.markdown("### ℹ️ About")
        st.markdown("""
        This assistant answers factual questions about HDFC mutual fund schemes.
        
        **Supported Topics:**
        - Expense ratio
        - Minimum SIP
        - Exit load
        - NAV (Net Asset Value)
        - Tax implications
        
        **Note:** This assistant provides facts only. It does not provide investment advice.
        """)
        
        st.markdown("---")
        st.markdown("### 📊 Data Status")
        
        # Check if data exists
        try:
            from src.scraper.data_storage import DataStorage
            storage = DataStorage()
            schemes = storage.load_latest_data()
            if schemes:
                st.success(f"✅ {len(schemes)} schemes loaded")
                # Get latest extraction date
                dates = [s.get('extracted_at', '') for s in schemes if s.get('extracted_at')]
                if dates:
                    latest = max(dates)
                    try:
                        date_obj = datetime.fromisoformat(latest.replace('Z', '+00:00'))
                        st.caption(f"Last updated: {date_obj.strftime('%Y-%m-%d %H:%M')}")
                    except:
                        st.caption(f"Last updated: {latest[:10]}")
            else:
                st.warning("⚠️ No data found. Run extract_data.py first.")
        except Exception as e:
            st.error(f"Error checking data: {str(e)}")
        
        st.markdown("---")
        st.markdown("### 🧹 Clear Chat")
        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.rerun()


if __name__ == "__main__":
    main()


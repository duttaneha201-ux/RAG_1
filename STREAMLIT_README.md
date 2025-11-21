# Streamlit UI - Quick Start Guide

## How to Run

**Option 1: Using the run script**
```bash
python run_app.py
```

**Option 2: Direct Streamlit command**
```bash
streamlit run src/ui/streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

## Features

✅ **Welcome Message** - Clear introduction to the assistant
✅ **3 Example Questions** - Clickable buttons for quick testing
✅ **Facts-only Note** - Prominently displayed
✅ **Chat Interface** - Interactive Q&A
✅ **Source URLs** - Every answer includes source links
✅ **Rate Limit Handling** - Shows retrieved info when LLM is unavailable
✅ **Chat History** - Conversation persists during session
✅ **Data Status** - Shows how many schemes are loaded

## Requirements Met

- ✅ Welcome line
- ✅ 3 example questions
- ✅ Note: "Facts-only. No investment advice."
- ✅ Answers include source URLs
- ✅ Handles rate limits gracefully
- ✅ Clean, modern UI

## Troubleshooting

**If the app doesn't start:**
1. Make sure you've run `extract_data.py` to get the data
2. Make sure you've run `build_vector_store.py` to create embeddings
3. Check that your `.env` file has a valid `GOOGLE_API_KEY`

**If you see API errors:**
- The app will show retrieved information even if LLM is rate-limited
- Wait 30-60 seconds and try again


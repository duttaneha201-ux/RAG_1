# Quick Start - Local Testing

## ✅ Streamlit App is Running!

Your app is already running. Open your browser and go to:

**👉 http://localhost:8501**

## Setup Checklist

### 1. API Key Setup
Make sure you have your Google Gemini API key set up:

**Option A: Using .env file (Recommended)**
Create a `.env` file in the project root:
```
GOOGLE_API_KEY=your_api_key_here
```

**Option B: Environment Variable**
Set it in your terminal/PowerShell:
```powershell
$env:GOOGLE_API_KEY="your_api_key_here"
```

### 2. Vector Store (Auto-setup)
- The app will automatically build the vector store on first run
- This takes ~30-60 seconds
- You'll see a spinner: "Setting up vector store (first time only)..."

### 3. Test the Interface

Once the app loads, you can:

1. **Use Example Questions**: Click the example question buttons
2. **Type Your Own**: Use the chat input at the bottom
3. **Try These Queries**:
   - "What is the expense ratio of HDFC Equity Fund?"
   - "What is the minimum SIP for HDFC Large Cap Fund?"
   - "What are the tax implications for HDFC ELSS Fund?"
   - "What is the NAV of HDFC Mid Cap Fund?"
   - "What is the exit load for HDFC Small Cap Fund?"

## Features to Test

✅ **Token Limits**: New truncation prevents "running out of tokens" errors
✅ **Chat Interface**: Interactive Q&A with conversation history
✅ **Source URLs**: Every answer includes source links
✅ **Rate Limit Handling**: Shows retrieved info even if LLM is unavailable
✅ **Example Questions**: Clickable buttons for quick testing

## Troubleshooting

**App won't start?**
- Make sure port 8501 is not in use
- Check that all dependencies are installed: `pip install -r requirements.txt`

**API errors?**
- Verify your `GOOGLE_API_KEY` is set correctly
- The app shows retrieved information even if LLM is rate-limited

**Vector store errors?**
- The app auto-builds it on first run
- If it fails, manually run: `python build_vector_store.py`

**Token limit errors?**
- These should now be automatically handled with truncation
- Check console for truncation warnings

## Stop the App

Press `Ctrl+C` in the terminal where it's running.

## Restart the App

```bash
python run_app.py
```

Or directly:
```bash
streamlit run src/ui/streamlit_app.py
```


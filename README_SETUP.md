# HDFC Mutual Fund FAQ Assistant - Setup Guide

## LLM Integration Setup

To use the Gemini Flash 1.5 model, you need to set up your Google AI API key:

### Step 1: Get API Key
1. Visit: https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Create a new API key
4. Copy the API key

### Step 2: Set Environment Variable

**Recommended: Using .env file (Easiest)**

1. Copy the template file:
   ```bash
   copy .env.example .env
   ```
   (On Linux/Mac: `cp .env.example .env`)

2. Open `.env` file and replace `your_api_key_here` with your actual API key

3. The `.env` file is already in `.gitignore`, so it's safe

**Alternative: Set Environment Variable**

**Windows (PowerShell):**
```powershell
$env:GOOGLE_API_KEY="your_api_key_here"
```

**Windows (Command Prompt):**
```cmd
set GOOGLE_API_KEY=your_api_key_here
```

**Linux/Mac:**
```bash
export GOOGLE_API_KEY=your_api_key_here
```

### Step 3: Test Integration
```bash
python test_llm_integration.py
```

## Complete Pipeline

1. **Extract Data**: `python extract_data.py`
2. **Build Vector Store**: `python build_vector_store.py`
3. **Test LLM**: `python test_llm_integration.py`


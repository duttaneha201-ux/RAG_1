# Streamlit Cloud Setup Guide

## Automatic Vector Store Setup

The Streamlit app now automatically builds the vector store on first run. Here's how it works:

### How It Works

1. **On First Launch:**
   - App checks if vector store exists
   - If not found, automatically builds it from JSON data files
   - Shows progress indicator: "Setting up vector store (first time only)..."
   - Takes ~30-60 seconds on first run

2. **Subsequent Runs:**
   - Vector store already exists
   - App starts immediately
   - No setup needed

### What's Included in Repository

✅ **Included (for Streamlit Cloud):**
- `data/processed/*.json` - Extracted scheme data (small files, ~50KB total)
- All source code
- Configuration files

❌ **Excluded (not needed on Streamlit Cloud):**
- `data/raw/*.html` - Raw HTML files (large, not needed)
- `data/chroma_db/` - Vector store (built automatically)
- `.env` files - API keys (use Streamlit Secrets instead)

### Setup Process

**Step 1: Data Files**
- JSON data files are now in the repository
- They contain all extracted scheme information
- Vector store is built from these on first run

**Step 2: Streamlit Secrets**
- Set `GOOGLE_API_KEY` in Streamlit Cloud Secrets
- Format: `GOOGLE_API_KEY = "your_key_here"`

**Step 3: Deploy**
- Push code to GitHub
- Streamlit Cloud auto-deploys
- On first run, vector store builds automatically

### First Run Behavior

When the app starts for the first time on Streamlit Cloud:

1. **Loading Phase:**
   ```
   "Setting up vector store (first time only)..."
   ```

2. **What Happens:**
   - Loads JSON data files from `data/processed/`
   - Creates text chunks for each scheme
   - Generates embeddings (takes ~30-60 seconds)
   - Builds ChromaDB vector store
   - Stores in `data/chroma_db/` (persists between restarts)

3. **Success Message:**
   ```
   ✓ Vector store ready!
   ```

4. **Ready to Use:**
   - App is now fully functional
   - Can answer questions immediately

### Troubleshooting

**If setup fails:**

1. **Check Logs:**
   - Go to Streamlit Cloud → Manage App → Logs
   - Look for error messages

2. **Common Issues:**
   - **No data files:** Ensure `data/processed/*.json` files are in repository
   - **Memory issues:** Streamlit Cloud free tier has memory limits
   - **Timeout:** First setup might take 60+ seconds

3. **Manual Setup (if needed):**
   - You can run `python src/utils/setup.py` locally
   - Then commit the built vector store (not recommended, large files)

### Updating Data

**To update scheme data:**

1. **Locally:**
   ```bash
   python extract_data.py
   ```

2. **Commit new JSON files:**
   ```bash
   git add data/processed/*.json
   git commit -m "Update scheme data"
   git push
   ```

3. **On Streamlit Cloud:**
   - App will detect new data on next restart
   - Vector store will rebuild automatically if needed

### File Sizes

- JSON data files: ~50KB total (small, included in repo)
- Vector store: ~5-10MB (built automatically, not in repo)
- Raw HTML: ~500KB+ (not needed, excluded)

### Benefits

✅ No manual setup required
✅ Works out of the box on Streamlit Cloud
✅ Automatic vector store creation
✅ Fast subsequent starts
✅ Easy data updates


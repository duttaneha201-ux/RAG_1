# HDFC Mutual Fund FAQ Assistant

A Retrieval-Augmented Generation (RAG) system that answers factual questions about HDFC mutual fund schemes. This assistant uses semantic search and Google's Gemini AI to provide accurate, source-backed answers about expense ratios, SIP amounts, exit loads, NAV, and tax implications.

## Features

- ✅ **Semantic Search**: Uses vector embeddings to find relevant information
- ✅ **LLM-Powered Answers**: Google Gemini 2.0 Flash for natural language responses
- ✅ **Source Attribution**: Every answer includes source URLs
- ✅ **Facts-Only Mode**: Designed to provide factual information, not investment advice
- ✅ **Token Management**: Automatic truncation to prevent token limit errors
- ✅ **Error Handling**: Graceful fallbacks and informative error messages
- ✅ **Streamlit UI**: Interactive web interface for easy access

## Data Sources

This assistant retrieves information from the following HDFC mutual fund schemes on Groww:

### 1. HDFC Equity Fund
- **Category**: Flexi Cap
- **Source URL**: [https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth](https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth)

### 2. HDFC Large Cap Fund
- **Category**: Large Cap
- **Source URL**: [https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth](https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth)

### 3. HDFC Mid Cap Fund
- **Category**: Mid Cap
- **Source URL**: [https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth](https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth)

### 4. HDFC Small Cap Fund
- **Category**: Small Cap
- **Source URL**: [https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth](https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth)

### 5. HDFC Multi Cap Fund
- **Category**: Multi Cap
- **Source URL**: [https://groww.in/mutual-funds/hdfc-multi-cap-fund-direct-growth](https://groww.in/mutual-funds/hdfc-multi-cap-fund-direct-growth)

### 6. HDFC ELSS Tax Saver Fund
- **Category**: ELSS
- **Source URL**: [https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth](https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth)

**Note**: All data is scraped from Groww mutual fund pages and stored locally. The source URLs are provided with each answer for verification.

## Supported Topics

This assistant can answer factual questions about:

- **Expense Ratio**: Annual charges and fees
- **Minimum SIP**: Minimum Systematic Investment Plan amount
- **Exit Load**: Charges for early redemption
- **NAV**: Net Asset Value information
- **Tax Implications**: Tax benefits and implications

## Sample Questions & Answers

### Example 1: Expense Ratio

**Question**: "What is the expense ratio of HDFC Equity Fund?"

**Sample Answer**: "The expense ratio for HDFC Equity Fund is 0.67% per annum (as of the latest data). This represents the annual charges deducted from the fund's assets to cover management and operational expenses.

**Source**: [https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth](https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth)"

---

### Example 2: Minimum SIP

**Question**: "What is the minimum SIP amount for HDFC Large Cap Fund?"

**Sample Answer**: "The minimum SIP investment amount for HDFC Large Cap Fund is ₹100. You can start a Systematic Investment Plan with this minimum amount and invest on a monthly, quarterly, or annual basis.

**Source**: [https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth](https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth)"

---

### Example 3: Tax Implications

**Question**: "What are the tax implications for HDFC ELSS Fund?"

**Sample Answer**: "HDFC ELSS Tax Saver Fund is an Equity Linked Savings Scheme (ELSS) that offers tax benefits under Section 80C of the Income Tax Act. You can claim a deduction of up to ₹1.5 lakh per financial year. The lock-in period is 3 years, and long-term capital gains (LTCG) above ₹1 lakh are taxed at 10% without indexation.

**Source**: [https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth](https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth)"

---

### Example 4: Exit Load

**Question**: "What is the exit load for HDFC Small Cap Fund?"

**Sample Answer**: "The exit load for HDFC Small Cap Fund is 1% if units are redeemed within 1 year from the date of investment. There is no exit load if units are redeemed after 1 year.

**Source**: [https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth](https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth)"

---

### Example 5: NAV Information

**Question**: "What is the NAV of HDFC Mid Cap Fund?"

**Sample Answer**: "The Net Asset Value (NAV) of HDFC Mid Cap Fund varies daily based on the fund's portfolio value. As of [extraction date], the NAV was [current NAV]. NAV is calculated daily after market hours and represents the per-unit market value of the fund's assets.

**Source**: [https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth](https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth)"

---

### More Example Questions to Try:

- "What is the expense ratio of HDFC Equity Fund?"
- "What is the minimum SIP for HDFC Large Cap Fund?"
- "What are the tax implications for HDFC ELSS Fund?"
- "What is the NAV of HDFC Mid Cap Fund?"
- "What is the exit load for HDFC Small Cap Fund?"
- "Compare expense ratios of HDFC Equity Fund and HDFC Large Cap Fund"
- "What is the minimum investment for HDFC Multi Cap Fund?"

## Disclaimer

### Important Legal and Usage Disclaimer

**⚠️ INFORMATION PURPOSE ONLY**: This assistant is designed for informational purposes only and provides factual data about HDFC mutual fund schemes. It does not constitute investment advice, financial planning, or recommendations.

**❌ NOT INVESTMENT ADVICE**: The information provided by this assistant should not be considered as:
- Investment recommendations or suggestions
- Financial planning or advisory services
- Buy, sell, or hold recommendations
- Portfolio allocation advice
- Risk assessment or suitability analysis

**📊 DATA ACCURACY**: 
- Information is sourced from publicly available data on Groww
- Data is scraped and may not reflect real-time updates
- Always verify information from official sources before making investment decisions
- The assistant may not have access to the most recent data

**⚖️ USER RESPONSIBILITY**:
- Users are solely responsible for their investment decisions
- Consult a qualified financial advisor before making investment choices
- Perform your own due diligence and research
- Consider your risk tolerance, investment goals, and financial situation
- Read the Scheme Information Document (SID) and Statement of Additional Information (SAI) before investing

**🔄 NO LIABILITY**:
- The developers and maintainers of this assistant are not liable for any financial losses
- No guarantee is provided regarding the accuracy, completeness, or timeliness of information
- Use of this assistant is at your own risk

**✅ FACTS ONLY**: This assistant is designed to answer factual questions about:
- Expense ratios
- Minimum SIP amounts
- Exit loads
- NAV information
- Tax implications

It does not provide opinions, comparisons between schemes, portfolio recommendations, or investment strategies.

**📝 BY USING THIS ASSISTANT**, you acknowledge that you have read, understood, and agree to this disclaimer. If you do not agree, please do not use this assistant.

---

## Quick Start

### Prerequisites

- Python 3.8+
- Google Gemini API Key ([Get it here](https://makersuite.google.com/app/apikey))

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/duttaneha201-ux/RAG_1.git
   cd RAG_1
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up API key**:
   Create a `.env` file in the project root:
   ```bash
   GOOGLE_API_KEY=your_api_key_here
   ```

4. **Extract data**:
   ```bash
   python extract_data.py
   ```

5. **Build vector store**:
   ```bash
   python build_vector_store.py
   ```

6. **Run the app**:
   ```bash
   python run_app.py
   ```

The app will open at `http://localhost:8501`

## Architecture

### System Overview

This is a Retrieval-Augmented Generation (RAG) system that combines semantic search with large language models to provide accurate, source-backed answers about HDFC mutual fund schemes.

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE LAYER                        │
│                    (Streamlit Web Application)                      │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               │ User Query
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      ANSWER GENERATION LAYER                        │
│                         (AnswerGenerator)                           │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐ │
│  │ Query Processor  │  │ Retrieval Service│  │    LLM Service   │ │
│  │ - Validate query │  │ - Process query  │  │ - Generate answer│ │
│  │ - Extract scheme │  │ - Retrieve docs  │  │ - Format response│ │
│  │ - Enhance query  │  │ - Format context │  │ - Handle errors  │ │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘ │
│           │                     │                      │           │
└───────────┼─────────────────────┼──────────────────────┼───────────┘
            │                     │                      │
            │                     ▼                      │
            │         ┌───────────────────────┐          │
            │         │   RETRIEVAL LAYER     │          │
            │         │  (RetrievalSystem)    │          │
            │         │                       │          │
            │         │  ┌─────────────────┐  │          │
            │         │  │Embedding Service│  │          │
            │         │  │  - Generate     │  │          │
            │         │  │    embeddings   │  │          │
            │         │  └────────┬────────┘  │          │
            │         │           │            │          │
            │         │           ▼            │          │
            │         │  ┌─────────────────┐  │          │
            │         │  │  Vector Store   │  │          │
            │         │  │   (ChromaDB)    │  │          │
            │         │  │  - Store docs   │  │          │
            │         │  │  - Search       │  │          │
            │         │  │  - Similarity   │  │          │
            │         │  └─────────────────┘  │          │
            │         └───────────────────────┘          │
            │                                              │
            │                                              │
            ▼                                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        DATA PROCESSING LAYER                        │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐ │
│  │  Data Extraction │  │ Data Preparation │  │  Data Storage    │ │
│  │  - Web scraping  │  │ - Create chunks  │  │  - JSON storage  │ │
│  │  - Parse HTML    │  │ - Generate       │  │  - Metadata      │ │
│  │  - Extract fields│  │   embeddings     │  │  - Versioning    │ │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                               │
                               │
                               ▼
                    ┌──────────────────────┐
                    │   DATA SOURCES       │
                    │  (Groww Website)     │
                    │  - 6 HDFC Schemes    │
                    │  - Scheme details    │
                    └──────────────────────┘
```

### Component Architecture

#### 1. **Data Extraction Layer**
- **Purpose**: Scrape and extract mutual fund data from Groww website
- **Components**:
  - `URLScraper`: Web scraping using Selenium
  - `DataExtractor`: HTML parsing and field extraction
  - `DataStorage`: Store extracted data as JSON files
- **Output**: Structured JSON files with scheme information

#### 2. **Data Processing Layer**
- **Purpose**: Prepare data for vector storage
- **Components**:
  - `DataPreparation`: Convert JSON data into text chunks
  - `EmbeddingService`: Generate vector embeddings using Sentence Transformers
  - Token management: Limit chunk sizes to prevent token overflow
- **Output**: Text chunks with embeddings and metadata

#### 3. **Vector Store Layer**
- **Purpose**: Store and search document embeddings
- **Technology**: ChromaDB (open-source vector database)
- **Features**:
  - Semantic similarity search
  - Metadata filtering (by scheme name, category)
  - Persistent storage on disk

#### 4. **Retrieval Layer**
- **Purpose**: Retrieve relevant documents for user queries
- **Components**:
  - `RetrievalSystem`: Core retrieval logic
  - `QueryProcessor`: Validate and enhance queries
  - `ResponseFormatter`: Format retrieved documents for LLM
- **Features**:
  - Query validation (factual vs. opinion-based)
  - Scheme name extraction and filtering
  - Context truncation to fit token limits

#### 5. **Answer Generation Layer**
- **Purpose**: Generate natural language answers
- **Components**:
  - `LLMService`: Google Gemini 2.0 Flash integration
  - `AnswerGenerator`: Orchestrates retrieval and generation
- **Features**:
  - Prompt engineering with context
  - Token limit management (6000 input, 4000 context)
  - Error handling and fallbacks
  - Source URL attribution

#### 6. **User Interface Layer**
- **Purpose**: Interactive web interface
- **Technology**: Streamlit
- **Features**:
  - Chat interface
  - Example questions
  - Source URL display
  - Error handling UI

### Data Flow

```
1. DATA COLLECTION PHASE:
   Groww Website → URLScraper → DataExtractor → DataStorage (JSON)

2. PREPROCESSING PHASE:
   JSON Files → DataPreparation → Text Chunks → EmbeddingService → ChromaDB

3. QUERY PROCESSING PHASE:
   User Query → QueryProcessor → Enhanced Query
                                  ↓
   Enhanced Query → EmbeddingService → Query Embedding
                                        ↓
   Query Embedding → ChromaDB → Similar Documents (Top-K)
                                        ↓
   Similar Documents → ResponseFormatter → Formatted Context
                                        ↓
   Formatted Context + Query → LLMService → Generated Answer
                                        ↓
   Answer + Source URLs → AnswerGenerator → Final Response
                                        ↓
   Final Response → Streamlit UI → User
```

### Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **UI Framework** | Streamlit | Interactive web interface |
| **LLM** | Google Gemini 2.0 Flash | Answer generation |
| **Embeddings** | Sentence Transformers (all-MiniLM-L6-v2) | Text embeddings (384 dimensions) |
| **Vector Database** | ChromaDB | Vector storage and similarity search |
| **Web Scraping** | Selenium + BeautifulSoup | Data extraction |
| **ML Framework** | PyTorch | Neural network operations (underlying embeddings) |
| **Data Storage** | JSON files | Structured data storage |
| **Token Management** | Custom token counter | Prevent token limit errors |

### Key Architectural Decisions

1. **RAG Pattern**: Combines retrieval (accuracy) with generation (natural language)
2. **Chunking Strategy**: Field-based chunks (expense_ratio, minimum_sip, etc.) for precise retrieval
3. **Token Limits**: Conservative limits (6000 input, 4000 context) to prevent API errors
4. **Fallback Mechanism**: Shows retrieved information even if LLM fails
5. **Metadata Filtering**: Scheme-specific filtering for targeted searches
6. **Source Attribution**: Every answer includes source URLs for verification

### Processing Pipeline Details

#### Query Processing Pipeline:
1. **Query Validation**: Check if query is factual (not opinion-based)
2. **Query Enhancement**: Extract scheme name, enhance with keywords
3. **Embedding Generation**: Convert query to 384-dimensional vector
4. **Vector Search**: Find top-K similar documents in ChromaDB
5. **Context Formatting**: Truncate and format documents for LLM
6. **Answer Generation**: Generate answer using Gemini with context
7. **Response Formatting**: Add source URLs and metadata

#### Error Handling:
- **LLM Failures**: Fall back to retrieved documents
- **Token Limits**: Automatic truncation with warnings
- **Empty Results**: Informative error messages
- **Invalid Queries**: Validation with helpful feedback

## Project Structure

```
RAG_1/
├── src/
│   ├── rag/              # RAG components (retrieval, LLM, answer generation)
│   ├── scraper/          # Web scraping for data extraction
│   ├── ui/               # Streamlit interface
│   └── utils/            # Utilities (token counter, setup, config)
├── config/               # Configuration files (URLs, prompts)
├── data/                 # Data storage (raw, processed, vector store)
└── run_app.py           # Main entry point
```

## Documentation

- [Setup Guide](README_SETUP.md) - Detailed setup instructions
- [Quick Start](QUICK_START.md) - Quick start guide for local testing
- [Streamlit Guide](STREAMLIT_README.md) - Streamlit-specific documentation

## License

This project is for educational and informational purposes only. Please refer to the disclaimer above before using.

## Contributing

Contributions are welcome! Please ensure that:
- All information remains factual and source-attributed
- The disclaimer is maintained and respected
- No investment advice is provided through the system

## Support

For issues, questions, or contributions, please open an issue on the GitHub repository.

---

**Remember**: This assistant provides facts only. Always consult a qualified financial advisor before making investment decisions.


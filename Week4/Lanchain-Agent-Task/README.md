# LangChain Research Agent with Multiple Tools

## 📚 Overview

This is an intelligent research agent built with LangChain that can answer company-related questions by automatically selecting and using the most appropriate tool from three different sources:

1. **Google Docs Search** - Searches insurance policy documents stored in Google Drive
2. **HR Policy Search** - Searches internal HR policy documents using RAG (Retrieval-Augmented Generation)
3. **Web Search** - Searches the internet for industry trends, benchmarks, and news

The agent uses **AWS Bedrock (Claude 3.5 Sonnet)** as the LLM and automatically decides which tool to use based on your question.

---

## 🏗️ Architecture

```
User Question
    ↓
LangChain Agent (Claude 3.5 Sonnet via AWS Bedrock)
    ↓
Decision: Which tool to use?
    ↓
    ├─→ Google Docs Search (MCP Server)
    │   ├─ Searches Google Drive folder
    │   ├─ Supports: Google Docs, Word, PDF
    │   └─ Returns: Document content
    │
    ├─→ HR Policy Search (RAG with ChromaDB)
    │   ├─ Semantic search in vector database
    │   ├─ Uses: sentence-transformers embeddings
    │   └─ Returns: Relevant policy sections
    │
    └─→ Web Search (DuckDuckGo)
        ├─ Searches the internet
        ├─ No API key required
        └─ Returns: Web results with links
    ↓
Agent formulates final answer
    ↓
User receives answer
```

## Demo
![Multi-Tool Research Agent Demo](https://github.com/KAVIRAJec/Gen-AI-Learnings/blob/main/Week4/Demo/Langchain-Agent-Demo.mp4)
---

## 🛠️ Tools Breakdown

### 1. Google Docs Search (MCP Server)

**Purpose:** Search customer feedback, marketing campaigns, insurance documents stored in Google Drive.

**Technology Stack:**

- Custom HTTP server (MCP architecture)
- Google Drive API & Google Docs API
- Service account authentication
- Supports: Google Docs, Word (.docx), PDF files

**How It Works:**

1. MCP server connects to Google Drive using service account
2. Searches for documents in specific folder ("Insurance_policy")
3. Extracts text from documents
4. Performs keyword search
5. Returns matching documents to agent

**Setup:**

```bash
# Start MCP server (Alternative Terminal)
python mcp/mcp_server.py
```

**Example Questions:**

- "Who is our insurance provider?"
- "What insurance coverage do we have?"
- "Show me customer feedback on claims"

---

### 2. HR Policy Search (RAG System)

**Purpose:** Search internal HR policies, benefits, compliance guidelines, GDPR requirements.

**Technology Stack:**

- ChromaDB (vector database)
- Sentence Transformers (all-MiniLM-L6-v2)
- LangChain document loaders & text splitters
- PyPDF2 for PDF processing

**How It Works:**

1. PDF documents are loaded from `rag/documents/`
2. Documents split into 700-character chunks
3. Chunks converted to vector embeddings
4. Stored in ChromaDB for fast similarity search
5. Agent queries return semantically similar chunks

**Setup:**

```bash
# Vectorize documents (one-time setup)
python rag/vectorize_hr_docs.py
```

**Example Questions:**

- "What is our PTO policy?"
- "How much is the 401k company match?"
- "What are the GDPR compliance requirements?"
- "What health insurance plans do we offer?"

---

### 3. Web Search (DuckDuckGo)

**Purpose:** Find industry benchmarks, market trends, regulatory updates, competitor information.

**Technology Stack:**

- DuckDuckGo Search API (free, no API key)
- Returns top 5 web results
- Privacy-focused

**How It Works:**

1. Agent sends search query to DuckDuckGo
2. Retrieves top results with titles, snippets, and links
3. Returns formatted results to agent
4. Agent synthesizes information into answer

**Example Questions:**

- "What are current insurance industry trends?"
- "Latest healthcare AI regulations"
- "Industry benchmarks for customer satisfaction"
- "What are competitors doing in insurance tech?"

---

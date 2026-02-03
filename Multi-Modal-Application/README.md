# Multi-Modal RAG System

A Retrieval-Augmented Generation (RAG) system for querying multi-modal documents (PDFs with images, text, and tables) using **LangChain**, AWS Bedrock Claude 3.5 Sonnet, and ChromaDB.

## Features

- 📄 **PDF Processing**: Extract and analyze text, images, and tables from PDFs
- 🖼️ **Image Analysis**: Process standalone images with detailed AI analysis
- 🧠 **Multi-Modal Understanding**: Claude 3.5 Sonnet analyzes visual and textual content
- 🔍 **Vector Search**: ChromaDB with HuggingFace embeddings for efficient semantic search
- 🔗 **LangChain Integration**: Uses LangChain framework for RAG pipeline
- 💬 **Console Interface**: Simple command-line interaction
- 📚 **Source Attribution**: Shows which documents were used to answer questions

## Setup
### 1. Add Documents

Place your PDF and image files in the `documents/` folder

### 2. Index Documents (Run First)

```bash
python index_documents.py
```

This will:
- Process all PDFs and images in `documents/` folder
- Extract text, analyze images and tables with Claude
- Store embeddings in ChromaDB

### 3. Query Your Documents

```bash
python main.py
```

Ask questions about your indexed documents!

Example queries:
- "What is the main topic of the document?"
- "Describe the table on page 3"
- "What does the diagram show?"
- Type `exit` to quit

## Workflow

```
Step 1: index_documents.py → Process docs → Store in ChromaDB
Step 2: main.py → Query → Retrieve context → Claude answers
```

## Project Structure

```
Multi-Modal-Application/
├── index_documents.py      # Step 1: Index documents (run first)
├── main.py                 # Step 2: Query interface
├── document_processor.py   # Multi-modal document processing
├── vector_store.py         # ChromaDB integration
├── rag_query.py           # RAG query handler
├── requirements.txt        # Dependencies
├── documents/             # Place PDFs and images here
└── chroma_db/            # ChromaDB storage (auto-created)
```

## Tech Stack

- **LangChain** - Framework for RAG pipeline and chains
- **AWS Bedrock** - Claude 3.5 Sonnet V2 for LLM and vision analysis
- **LangChain-Chroma** - Vector store integration
- **LangChain-HuggingFace** - Embeddings (all-MiniLM-L6-v2)
- **PyMuPDF** - PDF text extraction and rendering
- **ChromaDB** - Vector database for semantic search

## Architecture

```
Document Processing:
PDF/Image → PyMuPDF → Claude Vision Analysis → Embeddings → ChromaDB

Query Flow:
User Question → LangChain Retriever → Relevant Chunks → RetrievalQA Chain → Claude → Answer
```

## LangChain Components

- **ChatBedrock**: AWS Bedrock integration for Claude
- **HuggingFaceEmbeddings**: Local embedding model (all-MiniLM-L6-v2)
- **Chroma**: Vector store wrapper
- **RetrievalQA**: Automated RAG chain
- **PromptTemplate**: Custom prompts for context-aware answers

## Configuration

The system uses:
- **Model**: `us.anthropic.claude-3-5-sonnet-20241022-v2:0`
- **Region**: `us-east-1`
- **Max Tokens**: 2000
- **Temperature**: 0.3
- **Embedding Model**: all-MiniLM-L6-v2 (384 dimensions)
- **Search Results**: Top 3 relevant chunks

## Troubleshooting

### AWS Credentials
Ensure AWS credentials are configured:
```bash
aws configure
```

### ChromaDB Telemetry Warnings
The "Failed to send telemetry event" warnings are harmless and can be ignored.

### Python Version
If you see boto3 Python 3.9 deprecation warnings, consider upgrading to Python 3.10+.

## Additional Documentation

- [LANGCHAIN_CONVERSION.md](LANGCHAIN_CONVERSION.md) - Details about the LangChain implementation

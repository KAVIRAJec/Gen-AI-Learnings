# 🤖 Simple RAG Chatbot

**Chat with your documents using AI - No LangChain, No LlamaIndex!**

## 📁 Project Structure

```
RAG-Chatbot/
├── test_rag.py         # Main terminal chatbot (run this!)
├── rag_core.py         # Core RAG logic
├── documents/          # Put your documents here
├── chroma_db/          # Vector database (auto-created)
├── requirements.txt    # Dependencies
├── .env                # Your AWS credentials
└── README.md          # This file
```

## 🎮 Usage

### Run the Chatbot

```bash
python test_rag.py
```

The script will:

1. Load all documents from `documents/` folder
2. Let you ask questions
3. Show answers with source attribution
4. Support follow-up questions with memory

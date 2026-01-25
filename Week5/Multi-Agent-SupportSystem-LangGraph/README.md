# Multi-Agent Support System with LangGraph

A multi-agent support system built with LangGraph and AWS Bedrock Claude 3.5 Sonnet. The system uses a Supervisor Agent to classify queries and route them to specialized agents (IT and Finance) that leverage both File read using RAG (Retrieval-Augmented Generation) and web search capabilities.

## 📋 Architecture

```
┌─────────────┐
│    User     │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│   Supervisor    │  (Classifier Agent - ReAct pattern)
│     Agent       │
└────────┬────────┘
         │
    ┌────┴────┬────────────┐
    │         │            │
    ▼         ▼            ▼
┌────────┐ ┌────────┐ ┌─────────────┐
│   IT   │ │Finance │ │Clarification│
│ Agent  │ │ Agent  │ │    Node     │
└────────┘ └────────┘ └─────────────┘
    │         │            │
    │ Tools:  │ Tools:     │
    │ • RAG   │ • RAG      │
    │ • Web   │ • Web      │
    │         │            │
    └────┬────┴────────────┘
         │
         ▼
    ┌─────────┐
    │   END   │
    └─────────┘
```

## 🎯 Features

- **Intelligent Query Routing**: Supervisor Agent classifies queries and routes to appropriate specialist agents
- **Specialized Agents**:
  - **IT Agent**: Handles technical support, system access, VPN, software installation, etc.
  - **Finance Agent**: Manages expense reimbursement, invoice processing, budget queries, etc.
- **Dual Tool Architecture**: Each agent uses:
  - **RAG (ReadFile)**: Semantic search over internal policy documents
  - **WebSearch**: DuckDuckGo search for current information and troubleshooting
- **LangGraph Workflow**: State-based orchestration with conditional routing
- **ReAct Pattern**: All agents use Thought-Action-Observation reasoning

## 🛠️ Technology Stack

- **LLM**: AWS Bedrock Claude 3.5 Sonnet (us.anthropic.claude-3-5-sonnet-20241022-v2:0)
- **Framework**: LangChain 0.3.0+, LangGraph 0.2.0+
- **Vector Database**: ChromaDB 0.4.22
- **Embeddings**: HuggingFace all-MiniLM-L6-v2 (384 dimensions)
- **Web Search**: DuckDuckGo (ddgs package, no API keys required)
- **Document Processing**: PyPDF2 for PDF extraction

## 🔧 Configuration

### Agent Configuration

- **Temperature**: 0.0 (deterministic responses)
- **Max Tokens**: 4096
- **Max Iterations**: 5 per agent

### RAG Configuration

- **Chunk Size**: 700 characters
- **Chunk Overlap**: 150 characters
- **Top K Results**: 3 documents per query
- **Embedding Model**: all-MiniLM-L6-v2

### Web Search Configuration

- **Search Engine**: DuckDuckGo
- **Max Results**: 5 per query
- **Timeout**: 15 seconds

### Tool Usage Strategy
Both IT and Finance agents follow this strategy:

1. **ALWAYS start with ReadFile** (RAG) to check internal policies
2. **Then use WebSearch** if:
   - Information is insufficient or incomplete
   - Need current updates or regulations
   - Troubleshooting complex issues
   - Additional context required
3. **Combine information** from both sources in final answer

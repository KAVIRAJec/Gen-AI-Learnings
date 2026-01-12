# AI Models Comparison - Automated Evaluation System

**Enterprise-Grade AI Model Comparison with Automated Scoring**

## 🎯 Overview

Professional evaluation system that automatically compares AI models across software engineering use cases with **6-metric automated scoring**.

## 🤖 Models Under Evaluation

1. **Claude Sonnet 3.5** - AWS Bedrock (Premium quality)
2. **Meta Llama 3.2 90B** - AWS Bedrock (Open source powerhouse)
3. **DeepSeek-Coder** - Local via Ollama (Code specialist)

## 📊 Evaluation Categories

### 1. Code Generation (AppDev)

- REST API development
- React components
- Authentication functions

### 2. Data Analysis & SQL

- Complex SQL queries with joins
- Window functions
- Pandas data cleaning pipelines

### 3. Infrastructure Automation (DevOps)

- Multi-stage Dockerfiles
- Kubernetes deployments
- CI/CD pipelines (GitHub Actions)

## ⭐ AI-Powered Scoring (LLM-as-a-Judge)

### How It Works:

1. **AI Judge:** Claude Sonnet evaluates each response
2. **Structured Scoring:** JSON-formatted scores with reasoning
3. **6 Comprehensive Metrics:** Each scored 1-5 by the AI judge
4. **Fallback Safety:** Heuristic scoring if AI judge unavailable

Each response is evaluated by AI on:

| Metric                 | Description                                        |
| ---------------------- | -------------------------------------------------- |
| **Code Quality**       | Syntax correctness, best practices, completeness   |
| **Accuracy**           | Correctness of solution, meets requirements        |
| **Ease of Use**        | Clarity, conciseness, ready-to-use code            |
| **Speed/Latency**      | Response time performance (5s=⭐⭐⭐⭐⭐, 30s+=⭐) |
| **Explanation**        | Clear step-by-step explanations with comments      |
| **Edge Case Handling** | Error handling, null checks, validation            |

### Rating Scale

| Score | Stars      | Quality Level |
| ----- | ---------- | ------------- |
| 5     | ⭐⭐⭐⭐⭐ | Excellent     |
| 4     | ⭐⭐⭐⭐☆  | Very Good     |
| 3     | ⭐⭐⭐☆☆   | Good/Average  |
| 2     | ⭐⭐☆☆☆    | Below Average |
| 1     | ⭐☆☆☆☆     | Poor          |

## 📁 Results

All results are saved in `results/` directory:

- **JSON files** - Complete responses with metadata
- **Markdown reports** - Human-readable with scoring tables
- **Combined results** - All categories aggregated

## 🏗️ Architecture

```
src/
├── config/          # Configuration & constants
├── providers/       # Model providers (Bedrock, Ollama)
├── prompts/         # Expert system prompts
├── services/        # Evaluation orchestration
└── utils/           # Scoring, parsing, results management
```

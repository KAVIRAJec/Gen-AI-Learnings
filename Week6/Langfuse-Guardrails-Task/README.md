# LangChain Research Agent with Advanced Monitoring and Evaluation

A production-ready research agent that combines intelligent tool usage with comprehensive observability, safety guardrails, and systematic evaluation.

## Overview

This project demonstrates a complete AI agent implementation featuring three critical production capabilities: observability through distributed tracing, safety through input/output validation, and reliability through systematic evaluation.

## Core Concepts

### 1. LangChain Agent Architecture

The agent uses the ReAct (Reasoning and Acting) pattern to solve research queries. When given a question, it:

**Thinks** about what information it needs and which tools to use
**Acts** by calling appropriate tools (web search or document search)
**Observes** the results and decides the next step
**Repeats** this cycle until it has enough information to answer

This iterative approach allows the agent to break down complex questions into manageable steps and gather information from multiple sources.

### 2. LangFuse Observability

LangFuse provides comprehensive observability into the agent's behavior by tracking every step of execution.

**What it tracks:**
- Every prompt sent to the language model and the responses received
- Token consumption for cost monitoring and optimization
- Tool invocations and their results
- Complete execution traces showing the agent's reasoning process

**Why it matters:**
Without observability, debugging agent failures is like finding a needle in a haystack. LangFuse makes every decision, every tool call, and every thought process visible, enabling rapid diagnosis of issues and continuous improvement.

### 3. Guardrails AI Safety Layer

Guardrails AI acts as a safety filter, ensuring the agent stays within acceptable boundaries.

**Input Validation:**
- Detects and responds appropriately to greetings with friendly redirection
- Blocks off-topic requests like jokes, weather, or entertainment queries
- Prevents toxic or inappropriate content from being processed
- Ensures queries align with the agent's research-focused purpose

**Output Validation:**
- Scans generated responses for toxic content
- Ensures outputs maintain professional standards
- Protects against generating harmful or inappropriate content

**Implementation:**
Uses the ToxicLanguage validator from Guardrails Hub (trained on the detoxify model) combined with custom pattern matching for topic restrictions.

### 4. AgentEval Benchmarking

Systematic evaluation using the LLM-as-Judge methodology to assess agent performance across four critical dimensions.

**The Four Core Metrics:**

**Correctness (0-10 scale):**
An LLM judge evaluates whether answers are accurate, complete, and helpful. This goes beyond simple keyword matching to assess true answer quality.

**Latency (seconds):**
Measures end-to-end response time from query submission to final answer. Critical for user experience and production deployment.

**Hallucination Rate (percentage):**
Detects when the agent fabricates information or makes unsupported claims. The LLM judge examines whether statements are backed by retrieved information.

**Tool Usage Success (percentage):**
Verifies the agent selects appropriate tools for each query type. Web search for general knowledge, document search for internal information.

**Why LLM-as-Judge:**
Traditional metrics like BLEU or ROUGE fail to capture semantic quality. Using an LLM as judge provides nuanced evaluation similar to human assessment, measuring not just what the agent outputs but whether it truly answers the question correctly.

## How It Works

**Query Flow:**

1. User submits a research question
2. Guardrails validates the input for safety and appropriateness
3. Agent receives validated query and begins ReAct cycle
4. LangFuse traces every step of the reasoning process
5. Agent calls tools (web search or document search) as needed
6. LangFuse records all tool invocations and results
7. Agent synthesizes information into a final answer
8. Guardrails validates the output before returning to user
9. Complete trace is stored in LangFuse for analysis

**Evaluation Flow:**

1. Evaluator runs predefined test cases through the agent
2. For each test, captures the complete execution trace
3. Measures latency directly from execution time
4. Extracts which tools were used for tool usage validation
5. Sends query, answer, and tool usage to LLM judge
6. Judge returns scores for correctness and hallucination detection
7. Aggregates metrics across all test cases
8. Generates comprehensive markdown report with findings and recommendations

## Understanding the Evaluation Results

The evaluation generates a markdown report with four key sections:

**Summary:** High-level overview of test performance
**Core Metrics Table:** Quick view of all four metrics with pass/fail indicators
**Individual Test Results:** Detailed breakdown of each query with judge reasoning
**Recommendations:** Actionable suggestions for improvement based on the metrics

**Interpreting Scores:**

- Latency under 10 seconds: Good user experience
- Tool success rate above 80%: Agent understands query types
- Correctness above 7/10: Reliable answers
- Hallucination rate below 30%: Trustworthy information

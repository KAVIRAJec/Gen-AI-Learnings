#!/usr/bin/env python3
"""
Run Agent Evaluation - Simple 4-Metric Assessment

Evaluates the LangChain agent using AgentEval methodology:
1. Correctness - Answer quality (LLM judge)
2. Latency - Response time
3. Hallucination Rate - Fabricated information detection
4. Tool Usage Success - Correct tool selection
"""

import os
os.environ['ANONYMIZED_TELEMETRY'] = 'False'

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

import config
from agent.research_agent import ResearchAgent
from evaluation.evaluator import AgentEvaluator
from evaluation.test_cases import TEST_CASES


def main():
    """Run the agent evaluation"""
    
    # Load configuration
    if not config.load_config():
        print("Configuration failed")
        sys.exit(1)
    
    try:
        # Initialize agent and evaluator
        agent = ResearchAgent()
        evaluator = AgentEvaluator(agent)
        
        # Run benchmark
        results = evaluator.run_benchmark(TEST_CASES)
        
        # Display results
        aggregate = results['aggregate_metrics']
        print("\nResults:")
        print(f"Latency: {aggregate['avg_latency_seconds']}s")
        print(f"Tool Success Rate: {aggregate['tool_usage_success_rate']}%")
        print(f"Correctness: {aggregate['avg_correctness_score']}/10")
        print(f"Hallucination Rate: {aggregate['avg_hallucination_rate']}%")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

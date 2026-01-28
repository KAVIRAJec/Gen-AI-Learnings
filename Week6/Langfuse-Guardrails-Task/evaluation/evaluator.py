"""
AgentEval - Simple LangChain Agent Evaluation

Core Metrics:
1. Correctness - Is the answer accurate and complete?
2. Latency - How fast does the agent respond?
3. Hallucination Rate - Does the agent make up information?
4. Tool Usage Success - Does the agent use the right tools?
"""

import time
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import boto3

from agent.research_agent import ResearchAgent
import config


class AgentEvaluator:
    """
    Simple Agent Evaluator
    
    Evaluates 4 core metrics:
    - Correctness: Answer quality judged by LLM
    - Latency: Response time in seconds
    - Hallucination Rate: Checks for fabricated information
    - Tool Usage Success: Verifies correct tool selection
    """
    
    def __init__(self, agent: ResearchAgent):
        """Initialize evaluator with LLM judge"""
        self.agent = agent
        self.results_dir = Path(__file__).parent / "results"
        self.results_dir.mkdir(exist_ok=True)
        
        # Initialize Claude as judge
        self.bedrock_client = boto3.client(
            'bedrock-runtime',
            region_name=config.AWS_REGION,
            aws_access_key_id=config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY
        )
        self.model_id = config.MODEL_ID
    
    def _judge_answer(self, query: str, answer: str, expected_tool: str, tools_used: List[str]) -> Dict[str, Any]:
        """
        Use LLM judge to evaluate the answer quality
        
        Returns scores for:
        - Correctness (0-10): Is the answer accurate and complete?
        - Hallucination (0-10): Any fabricated information? (10 = none, 0 = severe)
        """
        
        judge_prompt = f"""You are evaluating an AI agent's answer quality.

**User Query:** {query}

**Agent's Answer:** {answer}

**Tools Used:** {', '.join(tools_used) if tools_used else 'None'}

**Expected Tool:** {expected_tool}

Evaluate the answer on two dimensions:

1. **Correctness (0-10):** Is the answer accurate, complete, and helpful?
   - 10: Perfect, comprehensive answer
   - 7-9: Good answer, minor gaps
   - 4-6: Partial answer, missing key information
   - 0-3: Incorrect or very incomplete

2. **Hallucination Score (0-10):** Does the answer contain fabricated or unsupported claims?
   - 10: No hallucinations, all claims supported
   - 7-9: Mostly factual, minor speculation
   - 4-6: Some unsupported claims
   - 0-3: Significant fabricated information

Respond in JSON format:
{{
  "correctness_score": <0-10>,
  "hallucination_score": <0-10>,
  "reasoning": "<brief explanation>"
}}"""

        try:
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 500,
                    "temperature": 0.1,
                    "messages": [{"role": "user", "content": judge_prompt}]
                })
            )
            
            response_body = json.loads(response['body'].read())
            judge_output = response_body['content'][0]['text']
            
            # Extract JSON
            if "```json" in judge_output:
                judge_output = judge_output.split("```json")[1].split("```")[0].strip()
            elif "```" in judge_output:
                judge_output = judge_output.split("```")[1].split("```")[0].strip()
            
            return json.loads(judge_output)
            
        except Exception as e:
            return {
                "correctness_score": 5,
                "hallucination_score": 5,
                "reasoning": f"Evaluation failed: {str(e)}"
            }
    
    def evaluate_query(self, query: str, expected_tool: str = None, 
                      ground_truth: str = None, reference_trajectory: List[Dict] = None) -> Dict[str, Any]:
        """
        Evaluate a single query on 4 core metrics
        
        Args:
            query: The test question
            expected_tool: Which tool should be used (Web_Search or Document_Search)
            ground_truth: Expected keywords in answer (optional)
            reference_trajectory: Expected execution path (optional, for reference only)
        
        Returns:
            Dictionary with all metrics and scores
        """
        # METRIC 1: LATENCY - Measure response time
        start_time = time.time()
        result = self.agent.process_query(query)
        latency_seconds = round(time.time() - start_time, 2)
        
        output = result.get("output", "")
        intermediate_steps = result.get("intermediate_steps", [])
        success = result.get("success", False)
        
        # METRIC 2: TOOL USAGE SUCCESS - Check if correct tool was used
        tools_used = []
        for step in intermediate_steps:
            if len(step) >= 1 and hasattr(step[0], 'tool'):
                tools_used.append(step[0].tool)
        
        tools_used = list(set(tools_used))  # Remove duplicates
        tool_usage_success = expected_tool in tools_used if expected_tool else True
        
        # METRICS 3 & 4: CORRECTNESS and HALLUCINATION - Use LLM judge
        judgment = self._judge_answer(query, output, expected_tool, tools_used)
        
        correctness_score = judgment["correctness_score"]
        hallucination_score = judgment["hallucination_score"]
        
        # Calculate hallucination rate (inverse of score)
        hallucination_rate = round((10 - hallucination_score) / 10 * 100, 1)
        
        # Compile all metrics
        metrics = {
            "query": query,
            "output": output[:400] + "..." if len(output) > 400 else output,
            "full_output": output,
            
            # Core Metrics
            "latency_seconds": latency_seconds,
            "tool_usage_success": tool_usage_success,
            "correctness_score": correctness_score,
            "hallucination_rate_percent": hallucination_rate,
            
            # Supporting Data
            "tools_used": tools_used,
            "expected_tool": expected_tool,
            "hallucination_score": hallucination_score,
            "judge_reasoning": judgment["reasoning"],
            "success": success,
            "timestamp": datetime.now().isoformat()
        }
        
        return metrics
    
    def run_benchmark(self, test_cases: List[Dict]) -> Dict[str, Any]:
        """
        Run complete evaluation on all test cases
        
        Evaluates each query and calculates aggregate metrics
        """
        all_results = []
        
        for i, test in enumerate(test_cases, 1):
            print(f"\nTest {i}/{len(test_cases)}: {test['query']}")
            
            result = self.evaluate_query(
                query=test["query"],
                expected_tool=test.get("expected_tool"),
                ground_truth=test.get("ground_truth"),
                reference_trajectory=test.get("reference_trajectory")
            )
            all_results.append(result)
            
            # Small delay between tests
            time.sleep(1)
        
        # Calculate aggregate metrics
        aggregate = self._calculate_aggregate(all_results)
        
        # Save results to files
        self._save_results(all_results, aggregate)
        
        return {
            "individual_results": all_results,
            "aggregate_metrics": aggregate
        }
    
    def _calculate_aggregate(self, results: List[Dict]) -> Dict[str, Any]:
        """
        Calculate average metrics across all test cases
        
        Returns aggregate scores for all 4 core metrics
        """
        total = len(results)
        
        # METRIC 1: Average Latency
        avg_latency = sum(r["latency_seconds"] for r in results) / total
        
        # METRIC 2: Tool Usage Success Rate
        tool_success_rate = sum(1 for r in results if r["tool_usage_success"]) / total
        
        # METRIC 3: Average Correctness
        avg_correctness = sum(r["correctness_score"] for r in results) / total
        
        # METRIC 4: Average Hallucination Rate
        avg_hallucination_rate = sum(r["hallucination_rate_percent"] for r in results) / total
        
        aggregate = {
            "total_tests": total,
            
            # 4 Core Metrics
            "avg_latency_seconds": round(avg_latency, 2),
            "tool_usage_success_rate": round(tool_success_rate * 100, 1),
            "avg_correctness_score": round(avg_correctness, 2),
            "avg_hallucination_rate": round(avg_hallucination_rate, 1),
            
            "timestamp": datetime.now().isoformat()
        }
        
        return aggregate
    
    def _save_results(self, results: List[Dict], aggregate: Dict):
        """Save evaluation results to JSON and Markdown files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed JSON
        json_file = self.results_dir / f"agent_eval_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump({
                "individual_results": results,
                "aggregate_metrics": aggregate
            }, f, indent=2)
        
        # Generate markdown report
        self._generate_markdown(results, aggregate, timestamp)
    
    def _generate_markdown(self, results: List[Dict], aggregate: Dict, timestamp: str):
        """Generate simple, readable markdown report"""
        md_file = self.results_dir / f"agent_eval_report_{timestamp}.md"
        
        with open(md_file, 'w') as f:
            f.write("# Agent Evaluation Report\n\n")
            f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("**Evaluation Method:** LangChain AgentEval with LLM Judge\n\n")
            f.write("**Judge Model:** Claude 3.5 Sonnet\n\n")
            f.write("---\n\n")
            
            # Summary
            f.write("## Summary\n\n")
            f.write(f"Evaluated the LangChain research agent on {aggregate['total_tests']} test queries, ")
            f.write("measuring the 4 core metrics: Correctness, Latency, Hallucination Rate, and Tool Usage Success.\n\n")
            
            # 4 Core Metrics
            f.write("## 4 Core Metrics\n\n")
            f.write("| Metric | Value | Status |\n")
            f.write("|--------|-------|--------|\n")
            
            f.write(f"| **1. Latency** | {aggregate['avg_latency_seconds']}s | ")
            f.write("Good\n" if aggregate['avg_latency_seconds'] < 10 else "Slow\n")
            
            f.write(f"| **2. Tool Usage Success** | {aggregate['tool_usage_success_rate']}% | ")
            f.write("Excellent\n" if aggregate['tool_usage_success_rate'] >= 80 else "Needs Work\n")
            
            f.write(f"| **3. Correctness** | {aggregate['avg_correctness_score']}/10 | ")
            f.write("Good\n" if aggregate['avg_correctness_score'] >= 7 else "Needs Work\n")
            
            f.write(f"| **4. Hallucination Rate** | {aggregate['avg_hallucination_rate']}% | ")
            f.write("Low\n" if aggregate['avg_hallucination_rate'] < 30 else "High\n")
            
            f.write("\n")
            
            # Individual Test Results
            f.write("## Individual Test Results\n\n")
            
            for i, r in enumerate(results, 1):
                f.write(f"### Test {i}: {r['query']}\n\n")
                
                # Metrics for this test
                f.write("| Metric | Value |\n")
                f.write("|--------|-------|\n")
                f.write(f"| Latency | {r['latency_seconds']}s |\n")
                f.write(f"| Tool Used | {', '.join(r['tools_used'])} |\n")
                f.write(f"| Tool Success | {'Yes' if r['tool_usage_success'] else 'No'} |\n")
                f.write(f"| Correctness | {r['correctness_score']}/10 |\n")
                f.write(f"| Hallucination Rate | {r['hallucination_rate_percent']}% |\n\n")
                
                # Judge reasoning
                f.write(f"**Evaluation:** {r['judge_reasoning']}\n\n")
                
                # Agent output
                f.write("<details>\n<summary>View Full Answer</summary>\n\n")
                f.write(f"{r['full_output']}\n\n")
                f.write("</details>\n\n")
                f.write("---\n\n")
            
            # Recommendations
            f.write("## Recommendations\n\n")
            
            if aggregate['avg_hallucination_rate'] > 30:
                f.write("- **High Hallucination Rate:** Add source citations and fact-checking\n")
            
            if aggregate['avg_latency_seconds'] > 10:
                f.write("- **Slow Response:** Optimize tool calls or add caching\n")
            
            if aggregate['tool_usage_success_rate'] < 80:
                f.write("- **Tool Selection Issues:** Improve tool descriptions in prompts\n")
            
            if aggregate['avg_correctness_score'] < 7:
                f.write("- **Low Correctness:** Enhance answer completeness and accuracy\n")
            
            if (aggregate['tool_usage_success_rate'] >= 80 and 
                aggregate['avg_correctness_score'] >= 7 and 
                aggregate['avg_hallucination_rate'] < 30):
                f.write("- **Good Performance:** Agent shows strong capabilities across all metrics\n")
            
            f.write("\n---\n\n")
            f.write(f"*Report generated on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}*\n")

"""
Results manager for saving and managing evaluation results.
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from ..config.constants import RESULTS_DIR, MARKDOWN_RESPONSE_TRUNCATE_LENGTH
from .ai_scorer import AIResponseScorer

logger = logging.getLogger(__name__)


class ResultsManager:
    """Manages saving and formatting of evaluation results."""
    
    def __init__(self, results_dir: str = RESULTS_DIR, judge_model=None):
        """
        Initialize results manager.
        
        Args:
            results_dir: Directory for saving results
            judge_model: AI model to use as judge for scoring (optional)
        """
        self._results_dir = Path(results_dir)
        self._scorer = AIResponseScorer(judge_model=judge_model)
        self._results_dir.mkdir(exist_ok=True)
        logger.info(f"Results directory: {self._results_dir}")
    
    def save_json_results(
        self,
        results: Dict[str, Any],
        category: str
    ) -> Path:
        """
        Save results to JSON file.
        
        Args:
            results: Results dictionary
            category: Category name for filename
            
        Returns:
            Path to saved JSON file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self._results_dir / f"{category}_results_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved JSON results to: {filename}")
        return filename
    
    def generate_markdown_report(
        self,
        results: Dict[str, Any],
        category: str
    ) -> str:
        """
        Generate markdown report from results.
        
        Args:
            results: Results dictionary
            category: Category name
            
        Returns:
            Markdown formatted string
        """
        md_lines = [
            f"# {category.upper()} - AI Model Comparison Results",
            "",
            f"**Generated:** {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}",
            "",
            "---",
            "",
            "## System Prompt Used",
            "",
            "```",
            results.get('system_prompt', ''),
            "```",
            "",
            "---",
            ""
        ]
        
        for question in results.get('questions', []):
            md_lines.extend([
                f"## Question {question['number']}: {question['title']}",
                "",
                "### Prompt",
                "```",
                question['prompt'],
                "```",
                ""
            ])
            
            # Score all responses for this question
            scores_by_model = {}
            for model_name, response_data in question.get('responses', {}).items():
                score = self._scorer.score_response(
                    response_content=response_data.get('response', ''),
                    response_time=response_data.get('time_seconds', 0),
                    status=response_data.get('status', 'error'),
                    category=results.get('category', ''),
                    question_prompt=question.get('prompt', '')
                )
                scores_by_model[model_name] = score
            
            # Add score summary table
            md_lines.append(self._scorer.generate_score_summary(scores_by_model))
            md_lines.extend(["", "### Detailed Responses", ""])
            
            for model_name, response_data in question.get('responses', {}).items():
                status_icon = "✅" if response_data['status'] == "success" else "❌"
                time_str = f"{response_data['time_seconds']:.2f}s"
                status_str = response_data['status']
                
                md_lines.extend([
                    f"#### {status_icon} {model_name}",
                    "",
                    f"**Time:** {time_str} | **Status:** {status_str}",
                    ""
                ])
                
                if response_data['status'] == "success":
                    response_text = response_data['response']
                    if len(response_text) > MARKDOWN_RESPONSE_TRUNCATE_LENGTH:
                        response_text = response_text[:MARKDOWN_RESPONSE_TRUNCATE_LENGTH] + "..."
                        md_lines.extend([
                            "```",
                            response_text,
                            "```",
                            "",
                            "*Response truncated. Full response in JSON file.*",
                            ""
                        ])
                    else:
                        md_lines.extend([
                            "```",
                            response_text,
                            "```",
                            ""
                        ])
                else:
                    error_msg = response_data.get('error_message', status_str)
                    md_lines.extend([
                        f"*Error: {error_msg}*",
                        ""
                    ])
            
            md_lines.extend(["---", ""])
        
        return '\n'.join(md_lines)
    
    def save_markdown_report(
        self,
        results: Dict[str, Any],
        category: str
    ) -> Path:
        """
        Generate and save markdown report.
        
        Args:
            results: Results dictionary
            category: Category name for filename
            
        Returns:
            Path to saved markdown file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self._results_dir / f"{category}_results_{timestamp}.md"
        
        markdown_content = self.generate_markdown_report(results, category)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        logger.info(f"Saved markdown report to: {filename}")
        return filename
    
    def save_combined_results(
        self,
        all_results: Dict[str, Dict[str, Any]]
    ) -> Path:
        """
        Save combined results for all categories.
        
        Args:
            all_results: Dictionary mapping categories to results
            
        Returns:
            Path to saved combined JSON file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self._results_dir / f"all_results_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved combined results to: {filename}")
        return filename

"""
AI-Powered Response Scoring System (LLM-as-a-Judge)

Enterprise-grade evaluation using AI models to judge other AI responses.
This follows industry best practices where AI evaluates AI performance.
"""

import json
import re
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ResponseScore:
    """Scores for a model response."""
    code_quality: int       # 1-5: Syntax correctness, best practices, completeness
    accuracy: int           # 1-5: Correctness of solution, meets requirements
    ease_of_use: int        # 1-5: Clarity, conciseness, ready-to-use
    speed_latency: int      # 1-5: Response time performance
    explanation: int        # 1-5: Clarity of explanation, step-by-step approach
    edge_case_handling: int # 1-5: Handles nulls, errors, edge cases
    reasoning: str = ""     # AI's reasoning for the scores
    
    @property
    def total(self) -> int:
        """Calculate total score."""
        return (self.code_quality + self.accuracy + self.ease_of_use + 
                self.speed_latency + self.explanation + self.edge_case_handling)
    
    @property
    def average(self) -> float:
        """Calculate average score."""
        return self.total / 6


class AIResponseScorer:
    """
    AI-Powered Response Scorer (LLM-as-a-Judge).
    
    Uses an AI model to evaluate other AI model responses based on
    multiple criteria. This is the industry standard approach used by
    leading AI companies for model evaluation.
    """
    
    # Speed thresholds (seconds) - only metric not evaluated by AI
    SPEED_EXCELLENT = 5
    SPEED_GOOD = 10
    SPEED_AVERAGE = 20
    SPEED_SLOW = 30
    
    EVALUATION_PROMPT = """You are an expert AI evaluator tasked with scoring another AI model's response.

**Context:**
- Question Category: {category}
- Question Prompt: {question_prompt}
- AI Response: {response_content}
- Response Time: {response_time:.2f} seconds

**Your Task:**
Evaluate the AI response on the following criteria (1-5 scale, where 1=Poor, 5=Excellent):

1. **Code Quality** (1-5): Evaluate syntax correctness, adherence to best practices, code structure, and completeness.
   - For SQL: Check for proper joins, CTEs, indexing considerations, query structure
   - For Code: Check for proper imports, error handling, code organization, design patterns
   - For Infrastructure: Check for security best practices, configuration completeness, documentation

2. **Accuracy** (1-5): Does the solution correctly solve the problem as stated?
   - Does it meet all requirements?
   - Is the logic sound and correct?
   - Would this work in production?

3. **Ease of Use** (1-5): How ready-to-use is this code?
   - Is it clear and well-documented?
   - Can a developer copy-paste and use it immediately?
   - Is the code concise without being cryptic?

4. **Explanation** (1-5): Quality of explanations and documentation.
   - Are there helpful comments?
   - Is the approach explained clearly?
   - Are there step-by-step instructions if needed?

5. **Edge Case Handling** (1-5): Does the code handle errors and edge cases?
   - Null/undefined/empty checks
   - Error handling (try-catch, validation)
   - Input validation
   - Graceful failure handling

**Output Format (JSON only, no other text):**
{{
  "code_quality": <1-5>,
  "accuracy": <1-5>,
  "ease_of_use": <1-5>,
  "explanation": <1-5>,
  "edge_case_handling": <1-5>,
  "reasoning": "<brief explanation of your evaluation (2-3 sentences)>"
}}

Be strict but fair. Production-quality code should score 4-5. Average attempts score 2-3."""
    
    def __init__(self, judge_model=None):
        """
        Initialize AI-powered scorer.
        
        Args:
            judge_model: The AI model provider to use as judge (Claude/Llama/DeepSeek)
                        If None, will use the first available provider
        """
        self._judge_model = judge_model
        logger.info("Initialized AI-powered response scorer (LLM-as-a-Judge)")
    
    def score_response(
        self,
        response_content: str,
        response_time: float,
        status: str,
        category: str,
        question_prompt: str,
        judge_model=None
    ) -> ResponseScore:
        """
        Score a model response using AI evaluation.
        
        Args:
            response_content: The model's response text
            response_time: Time taken to generate response (seconds)
            status: Response status (success/error)
            category: Question category (appdev/data/devops)
            question_prompt: The original question/prompt
            judge_model: Optional judge model to use (overrides instance default)
            
        Returns:
            ResponseScore with ratings for each metric
        """
        # Handle failed responses
        if status != "success" or not response_content:
            return ResponseScore(
                code_quality=1,
                accuracy=1,
                ease_of_use=1,
                speed_latency=1,
                explanation=1,
                edge_case_handling=1,
                reasoning="Response failed or empty"
            )
        
        # Use AI to evaluate the response
        model = judge_model or self._judge_model
        
        if model:
            try:
                ai_scores = self._evaluate_with_ai(
                    response_content=response_content,
                    response_time=response_time,
                    category=category,
                    question_prompt=question_prompt,
                    judge_model=model
                )
                if ai_scores:
                    return ai_scores
            except Exception as e:
                logger.warning(f"AI evaluation failed, using fallback: {e}")
        
        # Fallback to heuristic scoring if AI evaluation unavailable
        return self._fallback_heuristic_scoring(
            response_content, response_time, status, category
        )
    
    def _evaluate_with_ai(
        self,
        response_content: str,
        response_time: float,
        category: str,
        question_prompt: str,
        judge_model
    ) -> Optional[ResponseScore]:
        """
        Use AI model to evaluate the response.
        
        Args:
            response_content: Response to evaluate
            response_time: Time taken
            category: Question category
            question_prompt: Original question
            judge_model: The judge model provider
            
        Returns:
            ResponseScore if successful, None otherwise
        """
        # Truncate very long responses for evaluation
        eval_content = response_content[:4000] if len(response_content) > 4000 else response_content
        
        # Format evaluation prompt
        eval_prompt = self.EVALUATION_PROMPT.format(
            category=category.upper(),
            question_prompt=question_prompt[:500],  # Truncate long prompts
            response_content=eval_content,
            response_time=response_time
        )
        
        try:
            # Call the judge model
            logger.debug(f"Requesting AI evaluation from {judge_model.get_model_name()}")
            
            evaluation_response = judge_model.generate(
                system_prompt="You are an expert code reviewer and AI evaluator. Provide objective, constructive evaluations.",
                user_prompt=eval_prompt
            )
            
            if evaluation_response.status != "success":
                logger.warning(f"Judge model failed: {evaluation_response.error_message}")
                return None
            
            # Parse JSON response
            scores_dict = self._extract_json_scores(evaluation_response.content)
            
            if scores_dict:
                # Speed is calculated separately (not AI-judged)
                speed_score = self._score_speed(response_time)
                
                return ResponseScore(
                    code_quality=scores_dict.get('code_quality', 3),
                    accuracy=scores_dict.get('accuracy', 3),
                    ease_of_use=scores_dict.get('ease_of_use', 3),
                    speed_latency=speed_score,
                    explanation=scores_dict.get('explanation', 3),
                    edge_case_handling=scores_dict.get('edge_case_handling', 3),
                    reasoning=scores_dict.get('reasoning', 'AI evaluation completed')
                )
            
        except Exception as e:
            logger.error(f"Error in AI evaluation: {e}", exc_info=True)
        
        return None
    
    def _extract_json_scores(self, ai_response: str) -> Optional[Dict[str, Any]]:
        """
        Extract JSON scores from AI response.
        
        Args:
            ai_response: Raw AI response text
            
        Returns:
            Dictionary of scores or None if parsing fails
        """
        try:
            # Try to find JSON in the response
            json_match = re.search(r'\{[^}]+\}', ai_response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                scores = json.loads(json_str)
                
                # Validate scores are in range
                for key in ['code_quality', 'accuracy', 'ease_of_use', 'explanation', 'edge_case_handling']:
                    if key in scores:
                        scores[key] = max(1, min(5, int(scores[key])))
                
                return scores
        except Exception as e:
            logger.warning(f"Failed to parse JSON scores: {e}")
        
        return None
    
    def _score_speed(self, response_time: float) -> int:
        """
        Score based on response speed (not AI-judged).
        
        Args:
            response_time: Time in seconds
            
        Returns:
            Score from 1-5
        """
        if response_time <= self.SPEED_EXCELLENT:
            return 5
        elif response_time <= self.SPEED_GOOD:
            return 4
        elif response_time <= self.SPEED_AVERAGE:
            return 3
        elif response_time <= self.SPEED_SLOW:
            return 2
        else:
            return 1
    
    def _fallback_heuristic_scoring(
        self,
        response_content: str,
        response_time: float,
        status: str,
        category: str
    ) -> ResponseScore:
        """
        Fallback to simple heuristic scoring if AI evaluation unavailable.
        
        Args:
            response_content: Response text
            response_time: Response time
            status: Success/error status
            category: Question category
            
        Returns:
            ResponseScore using basic heuristics
        """
        logger.info("Using fallback heuristic scoring")
        
        # Basic heuristics
        has_code = bool(re.search(r'```|SELECT|FROM|def |function|class ', response_content, re.IGNORECASE))
        length = len(response_content)
        has_comments = bool(re.search(r'(#|//|/\*)', response_content))
        has_error_handling = bool(re.search(r'(try|except|catch|error|null|none)', response_content, re.IGNORECASE))
        
        code_quality = 3 if has_code else 2
        if has_comments:
            code_quality += 1
        
        accuracy = 3 if has_code and length > 200 else 2
        ease_of_use = 3 if 200 < length < 3000 else 2
        explanation = 3 if has_comments else 2
        edge_cases = 3 if has_error_handling else 2
        speed = self._score_speed(response_time)
        
        return ResponseScore(
            code_quality=min(5, code_quality),
            accuracy=min(5, accuracy),
            ease_of_use=min(5, ease_of_use),
            speed_latency=speed,
            explanation=min(5, explanation),
            edge_case_handling=min(5, edge_cases),
            reasoning="Fallback heuristic scoring (AI evaluation unavailable)"
        )
    
    def generate_score_summary(
        self,
        scores_by_model: Dict[str, ResponseScore]
    ) -> str:
        """
        Generate a markdown table summarizing scores.
        
        Args:
            scores_by_model: Dictionary mapping model names to their scores
            
        Returns:
            Markdown table string
        """
        if not scores_by_model:
            return ""
        
        table = "\n### 📊 Performance Metrics (1-5 Scale, AI-Evaluated)\n\n"
        table += "| Model | Code Quality | Accuracy | Ease of Use | Speed | Explanation | Edge Cases | **Avg** |\n"
        table += "|-------|--------------|----------|-------------|-------|-------------|------------|----------|\n"
        
        for model_name, score in scores_by_model.items():
            table += (
                f"| {model_name} | "
                f"{self._rating_stars(score.code_quality)} | "
                f"{self._rating_stars(score.accuracy)} | "
                f"{self._rating_stars(score.ease_of_use)} | "
                f"{self._rating_stars(score.speed_latency)} | "
                f"{self._rating_stars(score.explanation)} | "
                f"{self._rating_stars(score.edge_case_handling)} | "
                f"**{score.average:.1f}** |\n"
            )
        
        # Add reasoning section if available
        if any(score.reasoning for score in scores_by_model.values()):
            table += "\n#### 🤖 AI Judge Reasoning\n\n"
            for model_name, score in scores_by_model.items():
                if score.reasoning and "fallback" not in score.reasoning.lower():
                    table += f"**{model_name}:** {score.reasoning}\n\n"
        
        return table
    
    def _rating_stars(self, rating: int) -> str:
        """Convert numeric rating to stars."""
        filled = "⭐" * rating
        empty = "☆" * (5 - rating)
        return f"{filled}{empty} ({rating})"


# Alias for backward compatibility
ResponseScorer = AIResponseScorer

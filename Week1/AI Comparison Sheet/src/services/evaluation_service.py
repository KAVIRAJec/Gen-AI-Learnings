"""
Core evaluation service orchestrating the model evaluation process.
"""

import time
import logging
from typing import List, Dict, Any
from datetime import datetime

from ..providers import BaseModelProvider
from ..prompts import SystemPromptTemplates
from ..utils import QuestionParser, Question, ResultsManager
from ..config.constants import REQUEST_DELAY_SECONDS, CATEGORY_NAMES

logger = logging.getLogger(__name__)


class EvaluationService:
    """
    Orchestrates the AI model evaluation process.
    
    This service coordinates question loading, model invocation,
    and results collection for model comparison.
    """
    
    def __init__(
        self,
        providers: List[BaseModelProvider],
        question_parser: QuestionParser,
        results_manager: ResultsManager
    ):
        """
        Initialize evaluation service.
        
        Args:
            providers: List of model providers to evaluate
            question_parser: Parser for loading questions
            results_manager: Manager for saving results
        """
        self._providers = providers
        self._question_parser = question_parser
        self._results_manager = results_manager
        
        # Filter to only available providers
        self._active_providers = [
            p for p in providers if p.is_available()
        ]
        
        # Set judge model (use first Claude if available, otherwise first provider)
        self._judge_model = self._get_judge_model()
        if self._judge_model:
            logger.info(f"Using {self._judge_model.get_model_name()} as AI judge for scoring")
            # Update results manager with judge model
            self._results_manager._scorer._judge_model = self._judge_model
        
        logger.info(f"Initialized with {len(self._active_providers)} active providers")
    
    def evaluate_category(self, category: str) -> Dict[str, Any]:
        """
        Evaluate all models on questions from a specific category.
        
        Args:
            category: Category name ('appdev', 'data', or 'devops')
            
        Returns:
            Dictionary containing evaluation results
        """
        logger.info(f"Starting evaluation for category: {category}")
        
        self._print_category_header(category)
        
        # Load questions and system prompt
        questions = self._question_parser.load_questions_for_category(category)
        system_prompt = SystemPromptTemplates.get_prompt_for_category(category)
        
        # Initialize results structure
        results = {
            'category': category,
            'category_display_name': CATEGORY_NAMES.get(category, category),
            'system_prompt': system_prompt,
            'evaluation_timestamp': datetime.now().isoformat(),
            'questions': []
        }
        
        # Evaluate each question
        for question in questions:
            question_results = self._evaluate_question(question, system_prompt)
            results['questions'].append(question_results)
        
        logger.info(f"Completed evaluation for category: {category}")
        return results
    
    def _evaluate_question(
        self,
        question: Question,
        system_prompt: str
    ) -> Dict[str, Any]:
        """
        Evaluate a single question across all providers.
        
        Args:
            question: Question object to evaluate
            system_prompt: System prompt for the category
            
        Returns:
            Dictionary containing question and all responses
        """
        self._print_question_header(question)
        
        question_results = {
            'number': question.number,
            'title': question.title,
            'prompt': question.prompt,
            'responses': {}
        }
        
        for provider in self._active_providers:
            model_name = provider.get_model_name()
            
            print(f"  Testing {model_name}...", end=" ", flush=True)
            logger.debug(f"Invoking {model_name} for question {question.number}")
            
            # Generate response
            response = provider.generate(system_prompt, question.prompt)
            
            # Store results
            question_results['responses'][model_name] = {
                'response': response.content,
                'time_seconds': response.elapsed_time,
                'status': response.status,
                'error_message': response.error_message,
                'timestamp': datetime.now().isoformat()
            }
            
            # Print status
            if response.is_success:
                print(f"✓ ({response.elapsed_time:.2f}s)")
            else:
                error_display = response.error_message[:50] if response.error_message else response.status
                print(f"✗ ({error_display})")
            
            logger.debug(
                f"{model_name} completed in {response.elapsed_time:.2f}s "
                f"with status: {response.status}"
            )
            
            # Rate limiting delay
            time.sleep(REQUEST_DELAY_SECONDS)
        
        return question_results
    
    def evaluate_all_categories(
        self,
        categories: List[str] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Evaluate all specified categories.
        
        Args:
            categories: List of category names. If None, evaluates all.
            
        Returns:
            Dictionary mapping category names to results
        """
        if categories is None:
            categories = list(CATEGORY_NAMES.keys())
        
        all_results = {}
        
        for category in categories:
            try:
                results = self.evaluate_category(category)
                all_results[category] = results
                
                # Save individual category results
                self._results_manager.save_json_results(results, category)
                self._results_manager.save_markdown_report(results, category)
                
            except Exception as e:
                logger.error(f"Failed to evaluate category {category}: {e}", exc_info=True)
                print(f"\n❌ Error evaluating {category}: {e}")
        
        # Save combined results
        if all_results:
            self._results_manager.save_combined_results(all_results)
        
        return all_results
    
    def _get_judge_model(self):
        """
        Select the best available model to use as the AI judge.
        Prefers Claude Sonnet for its strong evaluation capabilities.
        
        Returns:
            The selected judge model provider or None
        """
        if not self._active_providers:
            return None
        
        # Prefer Claude for judging (best at evaluation tasks)
        for provider in self._active_providers:
            model_name = provider.get_model_name().lower()
            if 'claude' in model_name and 'sonnet' in model_name:
                return provider
        
        # Fallback to Llama (good alternative)
        for provider in self._active_providers:
            if 'llama' in provider.get_model_name().lower():
                return provider
        
        # Use first available provider
        return self._active_providers[0] if self._active_providers else None
    
    def _print_category_header(self, category: str) -> None:
        """Print formatted category header."""
        print(f"\n{'='*80}")
        print(f"EVALUATING: {CATEGORY_NAMES.get(category, category).upper()}")
        print(f"{'='*80}\n")
    
    def _print_question_header(self, question: Question) -> None:
        """Print formatted question header."""
        print(f"\n{str(question)}")
        print(f"{'-'*80}")
    
    @property
    def active_providers(self) -> List[BaseModelProvider]:
        """Get list of active providers."""
        return self._active_providers

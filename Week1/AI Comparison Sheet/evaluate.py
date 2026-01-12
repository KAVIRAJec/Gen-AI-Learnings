#!/usr/bin/env python3
"""
AI Model Evaluation System - Main Entry Point

A professional tool for evaluating AI models across different use cases.
Designed with enterprise-grade architecture and best practices.
"""

import sys
import logging
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.config import ConfigurationManager
from src.providers import (
    BedrockClaudeProvider,
    BedrockLlamaProvider,
    OllamaDeepSeekProvider
)
from src.services import EvaluationService
from src.utils import QuestionParser, ResultsManager, setup_logging

logger = logging.getLogger(__name__)


class ApplicationOrchestrator:
    """Main application orchestrator."""
    
    def __init__(self):
        """Initialize application components."""
        # Setup logging
        setup_logging(level=logging.INFO)
        logger.info("Initializing AI Model Evaluation System")
        
        # Load configuration
        self.config = ConfigurationManager()
        
        # Initialize providers
        self.providers = self._initialize_providers()
        
        # Initialize services
        self.question_parser = QuestionParser()
        self.results_manager = ResultsManager()
        self.evaluation_service = EvaluationService(
            providers=self.providers,
            question_parser=self.question_parser,
            results_manager=self.results_manager
        )
    
    def _initialize_providers(self) -> list:
        """Initialize all model providers."""
        providers = []
        
        # AWS Bedrock Claude
        bedrock_claude = BedrockClaudeProvider(self.config.aws)
        providers.append(bedrock_claude)
        
        # AWS Bedrock Llama
        bedrock_llama = BedrockLlamaProvider(self.config.aws)
        providers.append(bedrock_llama)
        
        # Ollama DeepSeek
        ollama_provider = OllamaDeepSeekProvider(self.config.ollama)
        providers.append(ollama_provider)
        
        return providers
    
    def display_system_status(self) -> None:
        """Display system status and available providers."""
        print("\n" + "=" * 80)
        print("AI MODEL EVALUATION SYSTEM v1.0")
        print("=" * 80)
        print("\n📊 System Status:")
        
        provider_status = self.config.get_enabled_providers()
        
        # AWS Bedrock
        if provider_status['aws_bedrock']:
            print("  ✓ AWS Bedrock (Claude Sonnet 3.5) - Configured")
            print("  ✓ AWS Bedrock (Meta Llama 3.2 90B) - Configured")
        else:
            print("  ⊗ AWS Bedrock - Not configured")
        
        # Ollama
        ollama_provider = next(
            (p for p in self.providers if isinstance(p, OllamaDeepSeekProvider)),
            None
        )
        if ollama_provider and ollama_provider.is_available():
            print("  ✓ Ollama (DeepSeek-Coder) - Running")
        else:
            print("  ⊗ Ollama (DeepSeek-Coder) - Not running")
            print("     Start with: ollama serve")
        
        active_count = len(self.evaluation_service.active_providers)
        print(f"\n📈 Active Providers: {active_count}")
        
        if active_count == 0:
            print("\n⚠️  Warning: No providers are configured!")
            print("   Please configure at least one provider in .env file")
            print("   See .env.example for configuration template")
        
        print("=" * 80)
    
    def run_interactive_mode(self) -> None:
        """Run in interactive mode with user prompts."""
        self.display_system_status()
        
        if len(self.evaluation_service.active_providers) == 0:
            print("\n❌ Cannot proceed without any active providers.")
            print("   Please configure credentials and try again.")
            sys.exit(1)
        
        print("\n📋 Select categories to evaluate:")
        print("  1. AppDev (Code Generation)")
        print("  2. Data (SQL & Data Analysis)")
        print("  3. DevOps (Infrastructure Automation)")
        print("  4. All categories")
        
        try:
            choice = input("\nEnter choice (1-4) [default: 4]: ").strip() or "4"
        except (KeyboardInterrupt, EOFError):
            print("\n\nOperation cancelled by user.")
            sys.exit(0)
        
        category_map = {
            '1': ['appdev'],
            '2': ['data'],
            '3': ['devops'],
            '4': ['appdev', 'data', 'devops']
        }
        
        categories = category_map.get(choice, ['appdev', 'data', 'devops'])
        
        print(f"\n🚀 Starting evaluation for: {', '.join(categories)}")
        print("=" * 80)
        
        try:
            self.evaluation_service.evaluate_all_categories(categories)
            
            print("\n" + "=" * 80)
            print("✅ EVALUATION COMPLETE!")
            print("=" * 80)
            print("\n📁 Results saved in: results/")
            print("   - JSON files contain detailed responses")
            print("   - Markdown files contain formatted reports")
            print("\n✨ Thank you for using AI Model Evaluation System!")
            print("=" * 80 + "\n")
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Evaluation interrupted by user.")
            logger.info("Evaluation interrupted by user")
        except Exception as e:
            print(f"\n\n❌ Evaluation failed: {e}")
            logger.error(f"Evaluation failed: {e}", exc_info=True)
            sys.exit(1)
    
    def run_batch_mode(self, categories: list) -> None:
        """
        Run in batch mode without interaction.
        
        Args:
            categories: List of categories to evaluate
        """
        self.display_system_status()
        
        if len(self.evaluation_service.active_providers) == 0:
            logger.error("No active providers available")
            sys.exit(1)
        
        logger.info(f"Running batch evaluation for: {categories}")
        
        try:
            self.evaluation_service.evaluate_all_categories(categories)
            logger.info("Batch evaluation completed successfully")
        except Exception as e:
            logger.error(f"Batch evaluation failed: {e}", exc_info=True)
            sys.exit(1)


def main():
    """Main entry point."""
    try:
        app = ApplicationOrchestrator()
        
        # Check for command-line arguments
        if len(sys.argv) > 1:
            categories = sys.argv[1].split(',')
            app.run_batch_mode(categories)
        else:
            app.run_interactive_mode()
    
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        logging.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

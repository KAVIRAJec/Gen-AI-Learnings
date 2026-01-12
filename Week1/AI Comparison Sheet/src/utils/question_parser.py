"""
Question parser for loading and parsing test questions from text files.
"""

import logging
from pathlib import Path
from typing import List
from dataclasses import dataclass

from ..config.constants import QUESTIONS_DIR, QUESTION_FILES

logger = logging.getLogger(__name__)


@dataclass
class Question:
    """Represents a test question."""
    number: str
    title: str
    prompt: str
    category: str
    
    def __str__(self) -> str:
        return f"Question {self.number}: {self.title}"


class QuestionParser:
    """Parser for loading and parsing test questions from text files."""
    
    def __init__(self, questions_dir: str = QUESTIONS_DIR):
        """
        Initialize question parser.
        
        Args:
            questions_dir: Directory containing question files
        """
        self._questions_dir = Path(questions_dir)
        
        if not self._questions_dir.exists():
            raise FileNotFoundError(
                f"Questions directory not found: {self._questions_dir}"
            )
    
    def load_questions_for_category(self, category: str) -> List[Question]:
        """
        Load questions for a specific category.
        
        Args:
            category: Category name ('appdev', 'data', or 'devops')
            
        Returns:
            List of Question objects
            
        Raises:
            ValueError: If category is invalid
            FileNotFoundError: If question file doesn't exist
        """
        if category not in QUESTION_FILES:
            raise ValueError(
                f"Invalid category: {category}. "
                f"Must be one of: {list(QUESTION_FILES.keys())}"
            )
        
        file_path = self._questions_dir / QUESTION_FILES[category]
        
        if not file_path.exists():
            raise FileNotFoundError(f"Question file not found: {file_path}")
        
        logger.info(f"Loading questions from: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return self._parse_questions(content, category)
    
    def _parse_questions(self, content: str, category: str) -> List[Question]:
        """
        Parse questions from file content.
        
        Args:
            content: Raw file content
            category: Category name for the questions
            
        Returns:
            List of parsed Question objects
        """
        questions = []
        sections = content.split('QUESTION ')
        
        for section in sections[1:]:  # Skip header
            lines = section.strip().split('\n')
            
            if not lines:
                continue
            
            # Parse question number and title
            first_line = lines[0]
            parts = first_line.split(':', 1)
            
            if len(parts) < 2:
                logger.warning(f"Skipping malformed question: {first_line}")
                continue
            
            question_num = parts[0].strip()
            question_title = parts[1].strip()
            
            # Parse question body (everything after the first line)
            question_text = '\n'.join(lines[1:]).strip()
            
            questions.append(Question(
                number=question_num,
                title=question_title,
                prompt=question_text,
                category=category
            ))
            
            logger.debug(f"Parsed: Question {question_num} - {question_title}")
        
        logger.info(f"Loaded {len(questions)} questions for category: {category}")
        return questions

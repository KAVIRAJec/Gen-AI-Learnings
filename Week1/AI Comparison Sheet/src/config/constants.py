"""
Configuration constants for AI Model Evaluation System.
"""

from typing import Final

# API Endpoints
GEMINI_API_BASE_URL: Final[str] = "https://generativelanguage.googleapis.com/v1/models"
GEMINI_MODEL_ID: Final[str] = "gemini-2.5-flash"
OLLAMA_DEFAULT_BASE_URL: Final[str] = "http://localhost:11434"
OLLAMA_MODEL_ID: Final[str] = "deepseek-coder:latest"

# AWS Bedrock
# Using inference profile ARN for cross-region support
BEDROCK_CLAUDE_MODEL_ID: Final[str] = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
BEDROCK_LLAMA_MODEL_ID: Final[str] = "us.meta.llama3-2-90b-instruct-v1:0"
BEDROCK_ANTHROPIC_VERSION: Final[str] = "bedrock-2023-05-31"
DEFAULT_AWS_REGION: Final[str] = "us-east-1"

# Model Parameters
DEFAULT_TEMPERATURE: Final[float] = 0.3
DEFAULT_TOP_P: Final[float] = 0.9
DEFAULT_MAX_TOKENS: Final[int] = 4000

# Request Timeouts (seconds)
GEMINI_TIMEOUT: Final[int] = 60
OLLAMA_TIMEOUT: Final[int] = 120
BEDROCK_TIMEOUT: Final[int] = 60

# File Paths
QUESTIONS_DIR: Final[str] = "questions"
RESULTS_DIR: Final[str] = "results"

# Question File Mapping
QUESTION_FILES: Final[dict] = {
    'appdev': 'appdev_questions.txt',
    'data': 'data_questions.txt',
    'devops': 'devops_questions.txt'
}

# Category Display Names
CATEGORY_NAMES: Final[dict] = {
    'appdev': 'Code Generation (AppDev)',
    'data': 'SQL & Data Analysis (Data)',
    'devops': 'Infrastructure Automation (DevOps)'
}

# Credentials Validation
MIN_CREDENTIAL_LENGTH: Final[int] = 10
PLACEHOLDER_API_KEY: Final[str] = "1-9"
PLACEHOLDER_AWS_KEY: Final[str] = "your_aws_access_key_here"

# Delays
REQUEST_DELAY_SECONDS: Final[float] = 1.0

# Truncation
MARKDOWN_RESPONSE_TRUNCATE_LENGTH: Final[int] = 2000

"""
Configuration management for AI Model Evaluation System.
"""

import os
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

from .constants import (
    DEFAULT_AWS_REGION,
    OLLAMA_DEFAULT_BASE_URL,
    MIN_CREDENTIAL_LENGTH,
    PLACEHOLDER_API_KEY,
    PLACEHOLDER_AWS_KEY
)


@dataclass(frozen=True)
class AWSConfig:
    """AWS Bedrock configuration."""
    access_key_id: str
    secret_access_key: str
    region: str
    
    def is_valid(self) -> bool:
        """Check if AWS credentials are valid (not placeholder)."""
        return (
            bool(self.access_key_id) and 
            bool(self.secret_access_key) and
            self.access_key_id != PLACEHOLDER_AWS_KEY and
            len(self.access_key_id) > MIN_CREDENTIAL_LENGTH and
            len(self.secret_access_key) > MIN_CREDENTIAL_LENGTH
        )


@dataclass(frozen=True)
class GoogleConfig:
    """Google Gemini API configuration."""
    api_key: str
    
    def is_valid(self) -> bool:
        """Check if Google API key is valid (not placeholder)."""
        return (
            bool(self.api_key) and 
            self.api_key != PLACEHOLDER_API_KEY and
            len(self.api_key) > MIN_CREDENTIAL_LENGTH
        )


@dataclass(frozen=True)
class OllamaConfig:
    """Ollama local model configuration."""
    base_url: str
    
    def is_valid(self) -> bool:
        """Ollama is always considered valid as it's local."""
        return bool(self.base_url)


class ConfigurationManager:
    """Manages application configuration and credentials."""
    
    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            env_file: Path to .env file. If None, uses default .env
        """
        load_dotenv(env_file)
        self._aws_config = self._load_aws_config()
        self._google_config = self._load_google_config()
        self._ollama_config = self._load_ollama_config()
    
    def _load_aws_config(self) -> AWSConfig:
        """Load AWS configuration from environment."""
        return AWSConfig(
            access_key_id=os.getenv('AWS_ACCESS_KEY_ID', ''),
            secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY', ''),
            region=os.getenv('AWS_REGION', DEFAULT_AWS_REGION)
        )
    
    def _load_google_config(self) -> GoogleConfig:
        """Load Google configuration from environment."""
        return GoogleConfig(
            api_key=os.getenv('GOOGLE_API_KEY', PLACEHOLDER_API_KEY)
        )
    
    def _load_ollama_config(self) -> OllamaConfig:
        """Load Ollama configuration from environment."""
        return OllamaConfig(
            base_url=os.getenv('OLLAMA_BASE_URL', OLLAMA_DEFAULT_BASE_URL)
        )
    
    @property
    def aws(self) -> AWSConfig:
        """Get AWS configuration."""
        return self._aws_config
    
    @property
    def google(self) -> GoogleConfig:
        """Get Google configuration."""
        return self._google_config
    
    @property
    def ollama(self) -> OllamaConfig:
        """Get Ollama configuration."""
        return self._ollama_config
    
    def get_enabled_providers(self) -> dict[str, bool]:
        """
        Get status of all providers.
        
        Returns:
            Dictionary mapping provider names to enabled status
        """
        return {
            'aws_bedrock': self._aws_config.is_valid(),
            'google_gemini': self._google_config.is_valid(),
            'ollama': self._ollama_config.is_valid()
        }

"""
AWS Bedrock model provider implementation.
"""

import json
import time
import logging
from typing import Optional

from .base_provider import BaseModelProvider, ModelResponse
from ..config import AWSConfig
from ..config.constants import (
    BEDROCK_CLAUDE_MODEL_ID,
    BEDROCK_ANTHROPIC_VERSION,
    DEFAULT_TEMPERATURE,
    DEFAULT_TOP_P,
    DEFAULT_MAX_TOKENS
)

logger = logging.getLogger(__name__)

try:
    import boto3
    from botocore.exceptions import ClientError, BotoCoreError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False
    logger.warning("boto3 not installed. AWS Bedrock provider will be unavailable.")


class BedrockClaudeProvider(BaseModelProvider):
    """AWS Bedrock Claude model provider."""
    
    def __init__(self, config: AWSConfig):
        """
        Initialize Bedrock Claude provider.
        
        Args:
            config: AWS configuration object
        """
        self._config = config
        self._client: Optional[any] = None
        self._is_initialized = False
        
        if BOTO3_AVAILABLE and config.is_valid():
            self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize boto3 Bedrock client."""
        try:
            session = boto3.Session(
                aws_access_key_id=self._config.access_key_id,
                aws_secret_access_key=self._config.secret_access_key,
                region_name=self._config.region
            )
            self._client = session.client('bedrock-runtime')
            self._is_initialized = True
            logger.info("AWS Bedrock client initialized successfully")
        except (ClientError, BotoCoreError) as e:
            logger.error(f"Failed to initialize AWS Bedrock client: {e}")
            self._is_initialized = False
    
    def generate(
        self,
        system_prompt: str,
        user_prompt: str
    ) -> ModelResponse:
        """Generate response using Claude via AWS Bedrock."""
        if not self.is_available():
            return ModelResponse(
                content="",
                elapsed_time=0.0,
                status="unavailable",
                error_message="AWS Bedrock client not configured"
            )
        
        try:
            start_time = time.time()
            
            request_body = {
                "anthropic_version": BEDROCK_ANTHROPIC_VERSION,
                "max_tokens": DEFAULT_MAX_TOKENS,
                "system": system_prompt,
                "messages": [
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
                "temperature": DEFAULT_TEMPERATURE,
                "top_p": DEFAULT_TOP_P
            }
            
            response = self._client.invoke_model(
                modelId=BEDROCK_CLAUDE_MODEL_ID,
                body=json.dumps(request_body)
            )
            
            elapsed_time = time.time() - start_time
            
            response_body = json.loads(response['body'].read())
            content = response_body['content'][0]['text']
            
            return ModelResponse(
                content=content,
                elapsed_time=elapsed_time,
                status="success"
            )
            
        except (ClientError, BotoCoreError) as e:
            logger.error(f"Bedrock API error: {e}")
            return ModelResponse(
                content="",
                elapsed_time=0.0,
                status="error",
                error_message=f"AWS error: {str(e)[:100]}"
            )
        except Exception as e:
            logger.error(f"Unexpected error in Bedrock provider: {e}")
            return ModelResponse(
                content="",
                elapsed_time=0.0,
                status="error",
                error_message=f"Error: {str(e)}"
            )
    
    def is_available(self) -> bool:
        """Check if Bedrock client is available."""
        return BOTO3_AVAILABLE and self._is_initialized and self._client is not None
    
    def get_model_name(self) -> str:
        """Get model display name."""
        return "Claude Sonnet 3.5 (AWS Bedrock)"

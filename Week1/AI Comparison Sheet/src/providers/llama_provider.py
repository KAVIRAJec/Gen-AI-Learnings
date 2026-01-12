"""
AWS Bedrock Meta Llama provider implementation.
"""

import json
import time
import logging

import boto3
from botocore.exceptions import ClientError

from .base_provider import BaseModelProvider, ModelResponse
from ..config import AWSConfig
from ..config.constants import (
    BEDROCK_LLAMA_MODEL_ID,
    DEFAULT_TEMPERATURE,
    DEFAULT_TOP_P,
    DEFAULT_MAX_TOKENS
)

logger = logging.getLogger(__name__)


class BedrockLlamaProvider(BaseModelProvider):
    """Meta Llama 3.2 provider via AWS Bedrock."""
    
    def __init__(self, config: AWSConfig):
        """
        Initialize Bedrock Llama provider.
        
        Args:
            config: AWS configuration
        """
        self._config = config
        self._client = None
        
        if config.is_valid():
            try:
                self._client = boto3.client(
                    service_name='bedrock-runtime',
                    region_name=config.region,
                    aws_access_key_id=config.access_key_id,
                    aws_secret_access_key=config.secret_access_key
                )
                logger.info(f"Initialized Bedrock Llama provider in region: {config.region}")
            except Exception as e:
                logger.error(f"Failed to initialize Bedrock Llama client: {e}")
                self._client = None
    
    def generate(self, system_prompt: str, user_prompt: str) -> ModelResponse:
        """
        Generate response using Meta Llama on Bedrock.
        
        Args:
            system_prompt: System-level instructions
            user_prompt: User's question or request
            
        Returns:
            ModelResponse with generated content and metadata
        """
        if not self._client:
            return ModelResponse(
                content="",
                elapsed_time=0.0,
                status="error",
                error_message="Bedrock client not initialized"
            )
        
        try:
            start_time = time.time()
            
            # Llama expects a different format than Claude
            # Combine system and user prompts into a single instruction
            full_prompt = f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n{user_prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
            
            payload = {
                "prompt": full_prompt,
                "temperature": DEFAULT_TEMPERATURE,
                "top_p": DEFAULT_TOP_P,
                "max_gen_len": DEFAULT_MAX_TOKENS
            }
            
            logger.debug(f"Invoking Llama model: {BEDROCK_LLAMA_MODEL_ID}")
            
            response = self._client.invoke_model(
                modelId=BEDROCK_LLAMA_MODEL_ID,
                body=json.dumps(payload),
                contentType='application/json',
                accept='application/json'
            )
            
            elapsed_time = time.time() - start_time
            
            response_body = json.loads(response['body'].read())
            content = response_body.get('generation', '')
            
            logger.info(f"Llama response received in {elapsed_time:.2f}s")
            
            return ModelResponse(
                content=content.strip(),
                elapsed_time=elapsed_time,
                status="success"
            )
            
        except ClientError as e:
            error_msg = f"An error occurred ({e.response['Error']['Code']}) when calling the InvokeModel operation: {e.response['Error']['Message']}"
            logger.error(f"Bedrock Llama error: {error_msg}")
            
            return ModelResponse(
                content="",
                elapsed_time=0.0,
                status="error",
                error_message=f"Error: {error_msg}"
            )
            
        except Exception as e:
            logger.error(f"Unexpected error in Bedrock Llama provider: {e}")
            return ModelResponse(
                content="",
                elapsed_time=0.0,
                status="error",
                error_message=f"Error: {str(e)}"
            )
    
    def is_available(self) -> bool:
        """
        Check if Bedrock Llama is available.
        
        Returns:
            bool: True if client is initialized
        """
        return self._client is not None
    
    def get_model_name(self) -> str:
        """
        Get the display name of the model.
        
        Returns:
            str: Model display name
        """
        return "Meta Llama 3.2 90B (AWS Bedrock)"

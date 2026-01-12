"""
Ollama local model provider implementation.
"""

import time
import logging
import requests

from .base_provider import BaseModelProvider, ModelResponse
from ..config import OllamaConfig
from ..config.constants import (
    OLLAMA_MODEL_ID,
    OLLAMA_TIMEOUT,
    DEFAULT_TEMPERATURE,
    DEFAULT_TOP_P,
    DEFAULT_MAX_TOKENS
)

logger = logging.getLogger(__name__)


class OllamaDeepSeekProvider(BaseModelProvider):
    """Ollama DeepSeek-Coder model provider."""
    
    def __init__(self, config: OllamaConfig):
        """
        Initialize Ollama DeepSeek provider.
        
        Args:
            config: Ollama configuration object
        """
        self._config = config
        self._api_url = f"{config.base_url}/api/generate"
    
    def generate(
        self,
        system_prompt: str,
        user_prompt: str
    ) -> ModelResponse:
        """Generate response using DeepSeek-Coder via Ollama."""
        if not self.is_available():
            return ModelResponse(
                content="",
                elapsed_time=0.0,
                status="unavailable",
                error_message="Ollama server not running"
            )
        
        try:
            start_time = time.time()
            
            # Combine system and user prompts
            full_prompt = f"{system_prompt}\n\n---\n\nUser Request:\n{user_prompt}"
            
            payload = {
                "model": OLLAMA_MODEL_ID,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": DEFAULT_TEMPERATURE,
                    "top_p": DEFAULT_TOP_P,
                    "num_predict": DEFAULT_MAX_TOKENS
                }
            }
            
            response = requests.post(self._api_url, json=payload, timeout=OLLAMA_TIMEOUT)
            elapsed_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                content = data.get('response', '')
                
                return ModelResponse(
                    content=content,
                    elapsed_time=elapsed_time,
                    status="success"
                )
            else:
                error_msg = f"HTTP {response.status_code}"
                logger.error(f"Ollama API error: {error_msg}")
                
                return ModelResponse(
                    content="",
                    elapsed_time=elapsed_time,
                    status="error",
                    error_message=error_msg
                )
                
        except requests.exceptions.Timeout:
            logger.error("Ollama API request timed out")
            return ModelResponse(
                content="",
                elapsed_time=0.0,
                status="error",
                error_message="Request timed out (Ollama may be slow or unresponsive)"
            )
        except requests.exceptions.ConnectionError:
            logger.error("Cannot connect to Ollama server")
            return ModelResponse(
                content="",
                elapsed_time=0.0,
                status="error",
                error_message="Cannot connect to Ollama server. Is it running?"
            )
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama API request error: {e}")
            return ModelResponse(
                content="",
                elapsed_time=0.0,
                status="error",
                error_message=f"Request error: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error in Ollama provider: {e}")
            return ModelResponse(
                content="",
                elapsed_time=0.0,
                status="error",
                error_message=f"Error: {str(e)}"
            )
    
    def is_available(self) -> bool:
        """Check if Ollama server is available."""
        try:
            response = requests.get(
                f"{self._config.base_url}/api/tags",
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def get_model_name(self) -> str:
        """Get model display name."""
        return "DeepSeek-Coder (Ollama Local)"

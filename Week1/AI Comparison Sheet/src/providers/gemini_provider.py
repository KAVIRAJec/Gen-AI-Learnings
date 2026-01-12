"""
Google Gemini API provider implementation.
"""

import time
import logging
import requests

from .base_provider import BaseModelProvider, ModelResponse
from ..config import GoogleConfig
from ..config.constants import (
    GEMINI_API_BASE_URL,
    GEMINI_MODEL_ID,
    GEMINI_TIMEOUT,
    DEFAULT_TEMPERATURE,
    DEFAULT_TOP_P,
    DEFAULT_MAX_TOKENS
)

logger = logging.getLogger(__name__)


class GeminiFlashProvider(BaseModelProvider):
    """Google Gemini Flash model provider."""
    
    def __init__(self, config: GoogleConfig):
        """
        Initialize Gemini Flash provider.
        
        Args:
            config: Google configuration object
        """
        self._config = config
        self._api_url = f"{GEMINI_API_BASE_URL}/{GEMINI_MODEL_ID}:generateContent"
    
    def generate(
        self,
        system_prompt: str,
        user_prompt: str
    ) -> ModelResponse:
        """Generate response using Gemini Flash."""
        if not self.is_available():
            return ModelResponse(
                content="",
                elapsed_time=0.0,
                status="unavailable",
                error_message="Google API key not configured"
            )
        
        try:
            start_time = time.time()
            
            # Combine system and user prompts for Gemini
            full_prompt = f"{system_prompt}\n\n---\n\nUser Request:\n{user_prompt}"
            
            url = f"{self._api_url}?key={self._config.api_key}"
            
            payload = {
                "contents": [{
                    "parts": [{
                        "text": full_prompt
                    }]
                }],
                "generationConfig": {
                    "temperature": DEFAULT_TEMPERATURE,
                    "topP": DEFAULT_TOP_P,
                    "maxOutputTokens": DEFAULT_MAX_TOKENS
                }
            }
            
            response = requests.post(url, json=payload, timeout=GEMINI_TIMEOUT)
            elapsed_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                content = data['candidates'][0]['content']['parts'][0]['text']
                
                return ModelResponse(
                    content=content,
                    elapsed_time=elapsed_time,
                    status="success"
                )
            else:
                error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                logger.error(f"Gemini API error: {error_msg}")
                
                return ModelResponse(
                    content="",
                    elapsed_time=elapsed_time,
                    status="error",
                    error_message=error_msg
                )
                
        except requests.exceptions.Timeout:
            logger.error("Gemini API request timed out")
            return ModelResponse(
                content="",
                elapsed_time=0.0,
                status="error",
                error_message="Request timed out"
            )
        except requests.exceptions.RequestException as e:
            logger.error(f"Gemini API request error: {e}")
            return ModelResponse(
                content="",
                elapsed_time=0.0,
                status="error",
                error_message=f"Request error: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error in Gemini provider: {e}")
            return ModelResponse(
                content="",
                elapsed_time=0.0,
                status="error",
                error_message=f"Error: {str(e)}"
            )
    
    def is_available(self) -> bool:
        """Check if Gemini API is available."""
        return self._config.is_valid()
    
    def get_model_name(self) -> str:
        """Get model display name."""
        return "Gemini 2.0 Flash (Google API)"

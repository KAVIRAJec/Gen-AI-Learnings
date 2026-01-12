"""
Base model provider interface.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ModelResponse:
    """Response from a model provider."""
    content: str
    elapsed_time: float
    status: str
    error_message: str = ""
    
    @property
    def is_success(self) -> bool:
        """Check if the response was successful."""
        return self.status == "success"


class BaseModelProvider(ABC):
    """Abstract base class for AI model providers."""
    
    @abstractmethod
    def generate(
        self,
        system_prompt: str,
        user_prompt: str
    ) -> ModelResponse:
        """
        Generate a response from the model.
        
        Args:
            system_prompt: System-level instructions for the model
            user_prompt: User's question or request
            
        Returns:
            ModelResponse containing the generated content and metadata
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the provider is available and configured.
        
        Returns:
            True if provider can be used, False otherwise
        """
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """
        Get the display name of the model.
        
        Returns:
            Human-readable model name
        """
        pass

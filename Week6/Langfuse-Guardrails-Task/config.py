"""
Configuration Module
"""
import os
from dotenv import load_dotenv

# AWS Bedrock
AWS_ACCESS_KEY_ID = None
AWS_SECRET_ACCESS_KEY = None
AWS_REGION = None
MODEL_ID = None
TEMPERATURE = None

# LangFuse
LANGFUSE_PUBLIC_KEY = None
LANGFUSE_SECRET_KEY = None
LANGFUSE_HOST = None

def load_config() -> bool:
    """
    Load configuration from environment variables
    
    Returns:
        bool: True if config loaded successfully
    """
    global AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, MODEL_ID, TEMPERATURE
    global LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_HOST
    
    load_dotenv()
    
    # AWS Configuration
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
    MODEL_ID = os.getenv('MODEL_ID', 'us.anthropic.claude-3-5-sonnet-20241022-v2:0')
    TEMPERATURE = float(os.getenv('TEMPERATURE', '0.0'))
    
    # LangFuse Configuration
    LANGFUSE_PUBLIC_KEY = os.getenv('LANGFUSE_PUBLIC_KEY')
    LANGFUSE_SECRET_KEY = os.getenv('LANGFUSE_SECRET_KEY')
    LANGFUSE_HOST = os.getenv('LANGFUSE_BASE_URL')
    
    # Validate AWS credentials
    if not all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY]):
        print("ERROR: AWS credentials not found")
        return False
    
    # LangFuse is optional
    if not all([LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY]):
        print("WARNING: LangFuse credentials not found. Tracing disabled.")
    
    return True

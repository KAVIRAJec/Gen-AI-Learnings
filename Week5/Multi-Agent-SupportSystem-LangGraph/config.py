"""
Configuration Loader for Multi-Agent Support System
"""
import os 
from dotenv import load_dotenv

# Global configuration variables
AWS_ACCESS_KEY_ID = None
AWS_SECRET_ACCESS_KEY = None
AWS_REGION = None
MODEL_ID = None
TEMPERATURE = None

def load_config():
    """Load configuration from environment variables
    
    returns: true if all required configs are present, else raises ValueError
    """
    global AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, MODEL_ID, TEMPERATURE
    
    load_dotenv()

    # AWS Bedrock Configuration
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_REGION = os.getenv('AWS_REGION')
    MODEL_ID = os.getenv('MODEL_ID')
    TEMPERATURE = float(os.getenv('TEMPERATURE', '0.0'))

    if not all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, MODEL_ID]):
        raise ValueError("Missing AWS configuration in environment variables")
    
    print(f"Using MODEL_ID={MODEL_ID}, REGION={AWS_REGION}")
    print(f"Temperature: {TEMPERATURE}")
    return True


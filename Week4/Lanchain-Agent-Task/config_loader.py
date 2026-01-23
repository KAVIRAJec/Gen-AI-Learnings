"""
Configuration Loader for Langchain Agent Application
"""
import os 
from dotenv import load_dotenv

# Global configuration variables
AWS_ACCESS_KEY_ID = None
AWS_SECRET_ACCESS_KEY = None
AWS_REGION = None
BEDROCK_MODEL_ID = None
MCP_SERVER_HOST = None
MCP_SERVER_PORT = None
GOOGLE_DOCS_FOLDER_NAME = None

def load_config():
    """Load configuration from environment variables
    
    returns: true if all required configs are present, else raises ValueError
    """
    global AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, BEDROCK_MODEL_ID
    global MCP_SERVER_HOST, MCP_SERVER_PORT, GOOGLE_DOCS_FOLDER_NAME
    
    load_dotenv()

    # AWS Bedrock Configuration
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_REGION = os.getenv('AWS_REGION')
    BEDROCK_MODEL_ID = os.getenv('BEDROCK_MODEL_ID')
    
    # MCP Configuration
    MCP_SERVER_HOST = os.getenv('MCP_SERVER_HOST')
    MCP_SERVER_PORT = int(os.getenv('MCP_SERVER_PORT'))
    GOOGLE_DOCS_FOLDER_NAME = os.getenv('GOOGLE_DOCS_FOLDER_NAME', 'Insurance_policy')

    if not all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, BEDROCK_MODEL_ID]):
        raise ValueError("Missing AWS configuration in environment variables")
    
    print(f"Using MODEL_ID={BEDROCK_MODEL_ID}, REGION={AWS_REGION}")
    print(f"MCP Server: {MCP_SERVER_HOST}:{MCP_SERVER_PORT}")
    print(f"Google Docs Folder: {GOOGLE_DOCS_FOLDER_NAME}")
    return True

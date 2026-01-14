import os
import json
import boto3
from dotenv import load_dotenv

# Initialize environment
load_dotenv()

# CONSTANTS

# Model Configuration - Claude 3.5 Sonnet V2 (using inference profile)
BEDROCK_CLAUDE_MODEL_ID: str = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
BEDROCK_ANTHROPIC_VERSION: str = "bedrock-2023-05-31"

# Model Parameters
DEFAULT_TEMPERATURE: float = 0.3
DEFAULT_MAX_TOKENS: int = 4000

# Load System Prompt from file
with open("system_prompt.txt", "r") as file:
    SYSTEM_PROMPT: str = file.read()

def _initialize_chatbot() -> boto3.client:
    """
    Initialize the chatbot with necessary configurations.
    """
    try:
        print("Chatbot initialized with model:", BEDROCK_CLAUDE_MODEL_ID)
        client = boto3.client(
            service_name='bedrock-runtime',
            region_name='us-east-1',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )
        return client
    except Exception as e:
        print("Error initializing chatbot:", e)
        raise

def _get_chatbot_response(client: boto3.client, query: str) -> str:
    """
    Get response from the chatbot for a given query.
    """
    try:
        # Construct the request body for Claude
        body = json.dumps({
            'anthropic_version': BEDROCK_ANTHROPIC_VERSION,
            'max_tokens': DEFAULT_MAX_TOKENS,
            'temperature': DEFAULT_TEMPERATURE,
            'system': SYSTEM_PROMPT,
            'messages': [
                {"role": "user", "content": query}
            ]
        })
        
        response = client.invoke_model(
            modelId=BEDROCK_CLAUDE_MODEL_ID,
            body=body,
            contentType='application/json',
            accept='application/json'
        )
        
        response_body = json.loads(response['body'].read())
        return response_body['content'][0]['text']
    except Exception as e:
        print("Error getting chatbot response:", e)
        raise

def main():
    print("AI Assistant Chatbot")
    try:
        chat_client = _initialize_chatbot()

        while True:
            user_query = input("(*_*) Enter your query: ")

            if user_query.lower() in ['exit', 'quit']:
                print("Exiting the chatbot. Thank you!")
                break

            response = _get_chatbot_response(chat_client, user_query)
            print(f"Chatbot Response: {response}\n")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
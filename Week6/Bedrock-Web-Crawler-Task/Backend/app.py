from flask import Flask, request, jsonify
from flask_cors import CORS
import boto3
import json
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
CORS(app)

AGENT_ID = os.getenv('AGENT_ID')
AGENT_ALIAS_ID = os.getenv('AGENT_ALIAS_ID')
bedrock = boto3.client('bedrock-agent-runtime', region_name='us-east-1')


@app.route('/crawl', methods=['POST'])
def crawl():
    try:
        url = request.json['url']
        
        response = bedrock.invoke_agent(
            agentId=AGENT_ID,
            agentAliasId=AGENT_ALIAS_ID,
            sessionId='session',
            inputText=f"Crawl this URL: {url}"
        )
        
        result = ""
        for event in response['completion']:
            if 'chunk' in event and 'bytes' in event['chunk']:
                result += event['chunk']['bytes'].decode('utf-8')
        
        try:
            return jsonify(json.loads(result))
        except:
            return jsonify({'text': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    app.run(port=5000)

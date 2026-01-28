import json
import boto3
from scraper import WebScraper
from cleaner import ContentCleaner

scraper = WebScraper()
cleaner = ContentCleaner()
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')


def lambda_handler(event, context):
    """Handle Bedrock Agent web scraping requests"""
    print(f"Received event: {json.dumps(event)}")
    
    # Get URL from parameters
    url = None
    for param in event.get('parameters', []):
        if param.get('name') == 'url':
            url = param.get('value')
            break
    
    if not url:
        return bedrock_response("Missing required parameter: url")
    
    try:
        # Fetch and clean the page
        print(f"Fetching URL: {url}")
        html, final_url, _ = scraper.fetch(url)
        
        print(f"Cleaning content from: {final_url}")
        text = cleaner.clean_html(html)
        
        # Summarize if too long
        if len(text) > 5000:
            print("Summarizing long content...")
            summary = summarize(text)
            result = {
                "url": final_url,
                "summary": summary,
                "length": len(text)
            }
        else:
            result = {
                "url": final_url,
                "text": text,
                "length": len(text)
            }
        
        return bedrock_response(result)
        
    except Exception as e:
        print(f"Error: {e}")
        return bedrock_response(f"Failed: {e}")


def summarize(text):
    """Use Claude to summarize long text"""
    try:
        response = bedrock.invoke_model(
            modelId='us.anthropic.claude-3-5-sonnet-20241022-v2:0',
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "messages": [{
                    "role": "user",
                    "content": f"Summarize this web page concisely:\n\n{text[:8000]}"
                }]
            })
        )
        result = json.loads(response['body'].read())
        return result['content'][0]['text']
    except Exception as e:
        return text[:1000] + "..."


def bedrock_response(body):
    """Format response for Bedrock Agent"""
    if isinstance(body, dict):
        body = json.dumps(body, indent=2)
    else:
        body = str(body)
    
    return {
        'messageVersion': '1.0',
        'response': {
            'actionGroup': 'WebScraperActionGroup',
            'function': 'web_scrape',
            'functionResponse': {
                'responseBody': {
                    'TEXT': {'body': body}
                }
            }
        }
    }

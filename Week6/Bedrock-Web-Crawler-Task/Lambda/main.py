"""
Local testing script for Lambda function
"""

import json
from lambda_function import lambda_handler

# Test cases
test_cases = [
    {
        "name": "Test 1: Example.com",
        "event": {
            "agent": "test-agent",
            "actionGroup": "WebScraperActionGroup",
            "function": "web_scrape",
            "parameters": [
                {
                    "name": "url",
                    "value": "https://example.com"
                }
            ]
        }
    },
    {
        "name": "Test 2: GitHub",
        "event": {
            "agent": "test-agent",
            "actionGroup": "WebScraperActionGroup",
            "function": "web_scrape",
            "parameters": [
                {
                    "name": "url",
                    "value": "https://github.com/KAVIRAJec/Gen-AI-Learnings"
                }
            ]
        }
    },
    {
        "name": "Test 3: Wikipedia (Long content)",
        "event": {
            "agent": "test-agent",
            "actionGroup": "WebScraperActionGroup",
            "function": "web_scrape",
            "parameters": [
                {
                    "name": "url",
                    "value": "https://en.wikipedia.org/wiki/Web_scraping"
                }
            ]
        }
    },
    {
        "name": "Test 4: Invalid URL",
        "event": {
            "agent": "test-agent",
            "actionGroup": "WebScraperActionGroup",
            "function": "web_scrape",
            "parameters": [
                {
                    "name": "url",
                    "value": "not-a-valid-url"
                }
            ]
        }
    },
    {
        "name": "Test 5: Missing Parameter",
        "event": {
            "agent": "test-agent",
            "actionGroup": "WebScraperActionGroup",
            "function": "web_scrape",
            "parameters": []
        }
    }
]


def run_tests():
    """Run all test cases"""
    print("="*70)
    print("LAMBDA FUNCTION LOCAL TESTING")
    print("="*70)
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*70}")
        print(f"Test {i}: {test['name']}")
        print(f"{'='*70}")
        
        try:
            # Call the lambda handler
            response = lambda_handler(test['event'], None)
            
            # Parse response
            response_body = response['response']['functionResponse']['responseBody']['TEXT']['body']
            
            # Pretty print
            print("\nResponse received:")
            print("-" * 70)
            
            # Try to parse as JSON for better display
            try:
                parsed = json.loads(response_body)
                print(json.dumps(parsed, indent=2))
            except:
                print(response_body)
            
            print("\n✓ Test PASSED")
            passed += 1
            
        except Exception as e:
            print(f"\n✗ Test FAILED: {str(e)}")
            print(f"Error details: {type(e).__name__}")
            failed += 1
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Passed: {passed}/{len(test_cases)}")
    print(f"Failed: {failed}/{len(test_cases)}")
    print("="*70)


if __name__ == "__main__":
    run_tests()
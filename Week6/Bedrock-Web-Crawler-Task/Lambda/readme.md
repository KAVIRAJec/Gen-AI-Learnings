# Code Building Guide
## Create package directory
mkdir -p package

## Install dependencies
pip install -r requirements.txt -t package/

## Copy Lambda function files
cp lambda_function.py package/
cp scraper.py package/
cp cleaner.py package/

## Create ZIP file
cd package
zip -r ../web-crawler-lambda.zip .
cd ..

# Testing
## Test Locally
```
python main.py
```

# AWS Deployment Guide
## Part 1: Deploy Lambda Function

### Step 1: Create Lambda Function

1. Go to AWS Console → Lambda → Create function
2. Choose "Author from scratch"
3. Function name: `web-crawler-scraper`
4. Runtime: Python 3.11
5. Architecture: x86_64
6. Click "Create function"

### Step 2: Upload Code

1. In the function page, go to "Code" tab
2. Click "Upload from" → ".zip file"
3. Upload `web-crawler-lambda.zip`
4. Click "Save"

### Step 3: Configure Function

1. Go to "Configuration" → "General configuration"
2. Click "Edit"
3. Set:
   - Memory: 512 MB
   - Timeout: 1 min 30 sec
4. Click "Save"

### Step 4: Add Environment Variables (Optional)

1. Go to "Configuration" → "Environment variables"
2. Add if needed (none required for basic setup)

### Step 5: Test Lambda Function

1. Go to "Test" tab
2. Create new test event:

```json
{
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

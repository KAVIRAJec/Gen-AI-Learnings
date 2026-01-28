import requests


class WebScraper:
    def __init__(self):
        self.max_size = 10 * 1024 * 1024  # 10MB
        self.timeout = 60
    
    def fetch(self, url):
        """Fetch HTML content from a URL"""
        
        # Basic URL validation
        if not url.startswith(('http://', 'https://')):
            raise ValueError(f"Invalid URL: {url}")
        
        try:
            # Fetch the page - requests handles gzip and redirects automatically
            response = requests.get(
                url,
                timeout=self.timeout,
                headers={'User-Agent': 'Mozilla/5.0 AWS-Bedrock-Crawler'},
                stream=True
            )
            
            response.raise_for_status()
            
            # Check if it's HTML
            content_type = response.headers.get('Content-Type', '')
            if 'html' not in content_type.lower():
                raise ValueError(f"Not HTML content: {content_type}")
            
            # Read content with size limit
            content = b''
            for chunk in response.iter_content(chunk_size=8192):
                content += chunk
                if len(content) > self.max_size:
                    raise ValueError("Content too large (max 10MB)")
            
            # Convert to text
            html = content.decode('utf-8', errors='ignore')
            final_url = response.url
            
            return html, final_url, content_type
            
        except requests.Timeout:
            raise TimeoutError(f"Timeout after {self.timeout}s")
        except requests.RequestException as e:
            raise ConnectionError(f"Failed to fetch: {e}")
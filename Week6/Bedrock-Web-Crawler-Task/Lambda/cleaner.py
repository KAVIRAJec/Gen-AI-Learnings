from bs4 import BeautifulSoup
import re


class ContentCleaner:
    def clean_html(self, html):
        """Extract readable text from HTML"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove script, style, and other non-content tags
            for tag in ['script', 'style', 'nav', 'footer', 'header']:
                for element in soup.find_all(tag):
                    element.decompose()
            
            # Try to find the main content area
            main = (
                soup.find('main') or 
                soup.find('article') or 
                soup.find('div', id=re.compile('content|main', re.I)) or
                soup.find('body') or 
                soup
            )
            
            # For Wikipedia, get paragraphs directly
            if 'wikipedia.org' in str(soup):
                text_parts = []
                for p in main.find_all('p'):
                    text = p.get_text(strip=True)
                    if len(text) > 20:  # Skip short fragments
                        text_parts.append(text)
                text = '\n\n'.join(text_parts)
            else:
                # For regular sites, get all text
                text = main.get_text(separator='\n', strip=True)
            
            # Clean up whitespace
            text = self._clean_text(text)
            
            return text if text else "No content found"
            
        except Exception as e:
            return f"Error: {e}"
    
    def _clean_text(self, text):
        """Remove extra whitespace"""
        if not text:
            return ""
        
        # Remove multiple blank lines
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # Remove long repeated characters
        text = re.sub(r'(.)\1{10,}', r'\1\1\1', text)
        
        return text.strip()

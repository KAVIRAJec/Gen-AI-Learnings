"""
Simple Web Search Tool using DuckDuckGo

This module provides web search functionality without requiring API keys.
Uses DuckDuckGo search to find industry benchmarks, trends, and regulatory updates.
"""

from ddgs import DDGS
from typing import List, Dict

# CONFIGURATION
MAX_RESULTS = 5
TIMEOUT = 15


def search_web(query: str) -> str:
    """
    Search the web using DuckDuckGo for industry information
    
    Args:
        query: Search query string (e.g., "insurance industry trends 2026")
    
    Returns:
        str: Formatted search results with titles, snippets, and links
    """
    try:
        # Perform DuckDuckGo search
        with DDGS() as ddgs:
            results = list(ddgs.text(
                query,
                max_results=MAX_RESULTS
            ))
        
        if not results:
            return f"No web search results found for: '{query}'"
        
        formatted_output = f"Found {len(results)} web search result(s) for '{query}':\n\n"
        
        for i, result in enumerate(results, 1):
            title = result.get('title', 'No title')
            snippet = result.get('body', 'No description available')
            link = result.get('href', 'No link')
            
            formatted_output += f"Result {i}: {title}\n"
            formatted_output += "-" * 70 + "\n"
            formatted_output += f"Summary: {snippet}\n"
            formatted_output += f"Source: {link}\n"
            formatted_output += "-" * 70 + "\n\n"
        
        print(f"Retrieved {len(results)} result(s)")
        return formatted_output
    
    except Exception as e:
        error_msg = f"❌ Error performing web search: {str(e)}"
        print(error_msg)
        return error_msg


def search_news(query: str, max_results: int = 5) -> List[Dict]:
    """
    Search for recent news articles using DuckDuckGo
    
    Args:
        query: Search query string
        max_results: Number of results to return
    
    Returns:
        list: List of news articles with title, body, url, date
    """
    try:
        with DDGS() as ddgs:
            news_results = list(ddgs.news(
                query,
                max_results=max_results
            ))
        return news_results
    
    except Exception as e:
        print(f"Error searching news: {e}")
        return []

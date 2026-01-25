"""
Web Search Tool using DuckDuckGo
"""

from ddgs import DDGS

# CONFIGURATION
MAX_RESULTS = 5
TIMEOUT = 15


def search_web(query: str) -> str:
    """
    Search the web using DuckDuckGo
    
    This function is used by both IT and Finance agents to search
    for information not available in internal documents.
    
    Args:
        query: Search query string
    
    Returns:
        str: Formatted search results with titles, snippets, and links
    """
    try:
        print(f"-> Searching web for: {query}")
        
        # Perform DuckDuckGo search
        with DDGS() as ddgs:
            results = list(ddgs.text(
                query,
                max_results=MAX_RESULTS
            ))
        
        if not results:
            return f"No web search results found for: '{query}'"
        
        # Format results
        formatted_output = f"Found {len(results)} web search result(s):\n\n"
        
        for i, result in enumerate(results, 1):
            title = result.get('title', 'No title')
            snippet = result.get('body', 'No description available')
            link = result.get('href', 'No link')
            
            formatted_output += f"[Result {i}] {title}\n"
            formatted_output += f"Summary: {snippet}\n"
            formatted_output += f"Source: {link}\n"
            formatted_output += "-" * 70 + "\n\n"
        
        print(f"-> Retrieved {len(results)} result(s)")
        return formatted_output
    
    except Exception as e:
        error_msg = f"Error performing web search: {str(e)}"
        print(f"-> {error_msg}")
        return error_msg

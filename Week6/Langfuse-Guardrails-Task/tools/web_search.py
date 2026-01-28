"""
Web Search Tool using DuckDuckGo
"""

from ddgs import DDGS

MAX_RESULTS = 5

def search_web(query: str) -> str:
    """
    Search the web using DuckDuckGo
    
    Args:
        query: Search query string
    Returns:
        Formatted search results
    """
    try:
        print(f"-> Searching web for: {query}")
        
        results = []
        with DDGS() as ddgs:
            search_results = list(ddgs.text(query, max_results=MAX_RESULTS))
            
            for i, result in enumerate(search_results, 1):
                title = result.get('title', 'No title')
                body = result.get('body', 'No description')
                href = result.get('href', 'No URL')
                
                results.append(
                    f"Result {i}:\n"
                    f"Title: {title}\n"
                    f"Summary: {body}\n"
                    f"Source: {href}\n"
                )
        
        print(f"-> Retrieved {len(results)} result(s)")
        
        if not results:
            return "No search results found."
        
        return "\n" + "="*50 + "\n".join(results)
        
    except Exception as e:
        error_msg = f"Error performing web search: {str(e)}"
        print(f"-> {error_msg}")
        return error_msg

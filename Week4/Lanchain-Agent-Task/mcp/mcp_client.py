"""
MCP Client Module for Google Docs MCP Server
"""
import requests
import config_loader

class MCPClient:
    def __init__(self, timeout=30):
        """Initialize MCP Client"""
        self.base_url = f"http://{config_loader.MCP_SERVER_HOST}:{config_loader.MCP_SERVER_PORT}"
        self.timeout = timeout
    
    def check_health(self):
        """Check if MCP server is running"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=2)
            return response.status_code == 200
        except Exception:
            return False

    def invoke_tool(self, tool_name: str, arguments: dict):
        """Invoke a tool on the MCP server with given arguments"""
        payload = {
            "tool": tool_name,
            "arguments": arguments
        }

        response = requests.post(
            f"{self.base_url}/invoke",
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()


# Tool function to search Google Docs via MCP Client
def search_google_docs(query: str) -> str:
    """
    LangChain-compatible tool function to search Google Docs.
    
    Args:
        query: Search query string
    
    Returns:
        str: Formatted search results
    """
    try:
        _mcp_client = MCPClient()
        
        # Check if server is running
        if not _mcp_client.check_health():
            return (
                "MCP Server is not running."
            )
        
        # Invoke Google Docs Search tool
        result = _mcp_client.invoke_tool(
            tool_name="Google_Docs_Search",
            arguments={"query": query}
        )
        
        # Check for errors
        if 'error' in result:
            return f"Error: {result['error']}\nDetails: {result.get('details', 'N/A')}"
        
        # Format results
        total = result.get('total_results', 0)
        
        if total == 0:
            return f"No documents found for query: '{query}' in folder '{result.get('folder', 'N/A')}'"
        
        # Build formatted response
        response = f"Found {total} document(s) for '{query}' in folder '{result.get('folder')}':\n"
        
        for i, doc in enumerate(result.get('documents', []), 1):
            response += f"📄 Document {i}: {doc.get('title', 'Untitled')}\n"
            response += f"   ID: {doc.get('id', 'N/A')}\n"
            response += f"   Modified: {doc.get('modified', 'N/A')}\n"
            response += f"\n   Content:\n   {doc.get('content', 'No content')}\n"
            response += "\n" + "-" * 70 + "\n\n"
        
        return response
    
    except Exception as e:
        return f"Error searching Google Docs: {str(e)}"
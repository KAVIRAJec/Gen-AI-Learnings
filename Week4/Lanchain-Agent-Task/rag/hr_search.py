"""
Simple RAG Search Module for HR Policy Documents
"""

from pathlib import Path
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# CONFIGURATION
MODULE_DIR = Path(__file__).parent
VECTOR_DB_FOLDER = MODULE_DIR / "vector_db"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
TOP_K_RESULTS = 4

# Global variable to store vector database
_vector_db = None

def load_vector_database():
    """
    Load the ChromaDB vector database
    
    This function is called automatically when needed.
    The database is loaded only once and reused.
    
    Returns:
        Chroma or None: Vector database if successful, None if not found
    """
    global _vector_db
    
    # Return existing database if already loaded
    if _vector_db is not None:
        return _vector_db
    
    if not VECTOR_DB_FOLDER.exists():
        print(f"Vector database not found at: {VECTOR_DB_FOLDER}")
        return None
    
    try:
        embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Load the vector database
        _vector_db = Chroma(
            persist_directory=str(VECTOR_DB_FOLDER),
            embedding_function=embeddings,
            collection_name="hr_policies"
        )
        
        print(f"Loaded vector database with {_vector_db._collection.count()} vectors")
        return _vector_db
        
    except Exception as e:
        print(f"Error loading vector database: {e}")
        return None

# SEARCH FUNCTION (Used by LangChain Agent)
def search_hr_policies(query: str) -> str:
    """
    Search HR policy documents using semantic similarity
    How it works:
    1. Converts query to vector embedding
    2. Finds most similar document chunks in database
    3. Returns formatted results with source information
    
    Args:
        query (str): User's search question
    
    Returns:
        str: Formatted search results with source documents
    """
    vector_db = load_vector_database()
    
    try:
        # Perform semantic similarity search
        results = vector_db.similarity_search(query, k=TOP_K_RESULTS)
        
        if not results:
            return f"No HR policy information found for: '{query}'"
        
        # Format the results
        response = f"Found {len(results)} relevant HR policy section(s) for '{query}':\n\n"
        
        for i, doc in enumerate(results, 1):
            source_file = Path(doc.metadata.get('source', 'Unknown')).name
            page_num = doc.metadata.get('page', 'N/A')
            
            # Get content
            content = doc.page_content.strip()
            
            # Build formatted response
            response += f"{'='*70}\n"
            response += f"RESULT {i} - {source_file} (Page {page_num})\n"
            response += f"{'='*70}\n"
            response += f"{content}\n\n"
        
        return response
        
    except Exception as e:
        return f"Error searching HR policies: {str(e)}"

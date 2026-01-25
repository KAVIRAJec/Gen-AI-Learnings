"""
Finance Document Search Tool (RAG)

Provides semantic search over vectorized Finance documents.
"""
import sys
import os
from pathlib import Path
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# CONFIGURATION
SCRIPT_DIR = Path(__file__).parent
VECTOR_DB_FOLDER = SCRIPT_DIR / "finance_vector_db"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
TOP_K_RESULTS = 3

# Global variable to store loaded vector database
_vectorstore = None


def load_vector_database():
    """
    Load the Finance vector database (singleton pattern)
    
    Returns:
        Chroma: The loaded vector database
    """
    global _vectorstore
    
    if _vectorstore is None:
        print("-> Loading Finance vector database...")
        
        # Check if vector database exists
        if not VECTOR_DB_FOLDER.exists():
            error_msg = f"Finance vector database not found at {VECTOR_DB_FOLDER}. Run vectorize_finance_docs.py first."
            print(f"-> ERROR: {error_msg}")
            raise FileNotFoundError(error_msg)
        
        # Initialize embeddings (must match the embeddings used during vectorization)
        embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Load the vector database
        _vectorstore = Chroma(
            persist_directory=str(VECTOR_DB_FOLDER),
            embedding_function=embeddings
        )
        
        # Get collection info
        collection = _vectorstore._collection
        count = collection.count()
        print(f"-> Loaded Finance vector database with {count} vectors")
    
    return _vectorstore


def search_finance_documents(query: str) -> str:
    """
    Search Finance documents using semantic similarity
    
    Args:
        query (str): The search query
        
    Returns:
        str: Formatted search results with source information
    """
    try:
        # Load vector database
        vectorstore = load_vector_database()
        
        # Perform similarity search
        results = vectorstore.similarity_search(
            query=query,
            k=TOP_K_RESULTS
        )
        
        print(f"-> Retrieved {len(results)} result(s)")
        
        if not results:
            return "No relevant information found in Finance documents."
        
        # Format results
        formatted_results = []
        for i, doc in enumerate(results, 1):
            source = Path(doc.metadata.get('source', 'Unknown')).name
            page = doc.metadata.get('page', 'Unknown')
            content = doc.page_content.strip()
            
            formatted_results.append(
                f"Result {i} (Source: {source}, Page: {page}):\n{content}"
            )
        
        return "\n\n" + "="*50 + "\n\n".join(formatted_results)
        
    except Exception as e:
        error_msg = f"Error searching Finance documents: {str(e)}"
        print(f"-> {error_msg}")
        return error_msg

"""
RAG Search Module for IT Documents
"""

import sys
import os
from pathlib import Path

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# CONFIGURATION
MODULE_DIR = Path(__file__).parent
VECTOR_DB_FOLDER = MODULE_DIR / "it_vector_db"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
TOP_K_RESULTS = 3

# Global variable to store vector database
_vector_db = None

def load_vector_database():
    """
    Load the ChromaDB vector database for IT documents.
    
    Returns:
        Chroma or None: Vector database if successful, None if not found
    """
    global _vector_db
    
    # Return existing database if already loaded
    if _vector_db is not None:
        return _vector_db
    
    if not VECTOR_DB_FOLDER.exists():
        print(f"-> Vector database not found at: {VECTOR_DB_FOLDER}")
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
            embedding_function=embeddings
        )
        
        print(f"-> Loaded IT vector database with {_vector_db._collection.count()} vectors")
        return _vector_db
        
    except Exception as e:
        print(f"-> Error loading vector database: {e}")
        return None


def search_it_documents(query: str) -> str:
    """
    Search IT documents using semantic similarity
    
    This function is used by the IT Agent to search through
    IT policy and documentation PDFs.
    
    Args:
        query (str): User's search question
    
    Returns:
        str: Formatted search results with source documents
    """
    vector_db = load_vector_database()
    
    if vector_db is None:
        return "IT document database not available."
    
    try:
        results = vector_db.similarity_search(query, k=TOP_K_RESULTS)
        if not results:
            return "No relevant IT documents found for your query."
        
        formatted_results = []
        formatted_results.append(f"Found {len(results)} relevant IT document(s):\n")
        
        for i, doc in enumerate(results, 1):
            source = doc.metadata.get('source', 'Unknown')
            page = doc.metadata.get('page', '?')
            
            # Get filename from source path
            source_file = Path(source).name if source != 'Unknown' else 'Unknown'
            
            # Format each result
            formatted_results.append(f"\n[Result {i}]")
            formatted_results.append(f"Source: {source_file} (Page {page})")
            formatted_results.append(f"Content:\n{doc.page_content.strip()}")
            formatted_results.append("-" * 50)
        
        return "\n".join(formatted_results)
        
    except Exception as e:
        return f"Error searching IT documents: {str(e)}"

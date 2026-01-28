"""
RAG Document Search Tool
"""
from pathlib import Path
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# Configuration
SCRIPT_DIR = Path(__file__).parent
VECTOR_DB_FOLDER = SCRIPT_DIR / "vector_db"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
TOP_K_RESULTS = 3

# Global vector store
_vectorstore = None

def load_vector_database():
    """Load the vector database (singleton pattern)"""
    global _vectorstore
    
    if _vectorstore is None:
        print("-> Loading document vector database...")
        
        if not VECTOR_DB_FOLDER.exists():
            print(f"-> WARNING: Vector database not found at {VECTOR_DB_FOLDER}")
            return None
        
        embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        _vectorstore = Chroma(
            persist_directory=str(VECTOR_DB_FOLDER),
            embedding_function=embeddings
        )
        
        collection = _vectorstore._collection
        count = collection.count()
        
        print(f"-> Loaded vector database with {count} vectors")
    
    return _vectorstore

def search_documents(query: str) -> str:
    """
    Search documents using semantic similarity
    
    Args:
        query: Search query
    Returns:
        Formatted search results
    """
    try:
        vectorstore = load_vector_database()
        
        if vectorstore is None:
            return "RAG search unavailable. Vector database not found."
        
        results = vectorstore.similarity_search(query=query, k=TOP_K_RESULTS)
        print(f"-> Retrieved {len(results)} document(s)")
        
        if not results:
            return "No relevant information found in documents."
        
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
        error_msg = f"Error searching documents: {str(e)}"
        print(f"-> {error_msg}")
        return error_msg

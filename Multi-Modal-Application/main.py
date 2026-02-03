"""
Multi-Modal RAG System - Main Application
"""

import os
from vector_store import VectorStore
from rag_query import RAGQuery

# CONSTANTS
CHROMA_DB_PATH = "chroma_db"

def initialize_rag_system():
    """Initialize the RAG system components"""
    print("=" * 60)
    print("Multi-Modal RAG System - Query Interface")
    print("=" * 60)
    
    # Check if documents are indexed
    if not os.path.exists(CHROMA_DB_PATH) or not os.listdir(CHROMA_DB_PATH):
        print("\n[ERROR] No indexed documents found!")
        return None, None
    
    # Initialize components
    print("\n[INFO] Loading vector store...")
    vector_store = VectorStore(CHROMA_DB_PATH)
    
    if not vector_store.is_indexed():
        print("\n[ERROR] Vector store is empty!")
        print("Please add some documents and run the indexing script first.")
        return None, None
    
    stats = vector_store.get_stats()
    print(f"[SUCCESS] Loaded {stats['total_chunks']} indexed chunks")
    
    rag_query = RAGQuery(vector_store)
    
    return vector_store, rag_query

def run_query_loop(rag_query):
    """Run the interactive query loop"""
    print("\n" + "=" * 60)
    print("RAG System Ready - You can now query your documents!")
    print("=" * 60)
    
    while True:
        try:
            print("\n" + "=" * 60)
            query = input("\nYour Question: ").strip()
            
            if not query:
                continue
            
            if query.lower() in ['exit', 'quit']:
                print("\nGoodbye!")
                break
            
            if query.lower() == 'clear':
                os.system('clear' if os.name != 'nt' else 'cls')
                continue
            
            print("\n[INFO] Searching documents...\n")
            
            # Get RAG response
            response = rag_query.query(query)
            
            print("=" * 60)
            print("Answer:\n")
            print(response['answer'])
            print("\n" + "=" * 60)
            
            # Show sources
            if response['sources']:
                print("\nSources:")
                for i, source in enumerate(response['sources'], 1):
                    print(f"  {i}. {source['filename']} (Relevance: {source['score']:.2f})")
        
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\n[ERROR] {str(e)}")

def main():
    """Main entry point"""
    try:
        # Initialize system
        vector_store, rag_query = initialize_rag_system()
        
        if not vector_store or not rag_query:
            print("\n[ERROR] RAG System initialization failed.")
            return
        
        # Run query loop
        run_query_loop(rag_query)
        
    except Exception as e:
        print(f"\n[ERROR] Fatal Error: {str(e)}")
        raise

if __name__ == "__main__":
    main()

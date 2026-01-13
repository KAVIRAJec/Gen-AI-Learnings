"""
RAG Chatbot - Interactive Terminal Version
Chat with your documents using AI!
"""

from dotenv import load_dotenv
from rag_core import SimpleRAG
from pathlib import Path

# Load environment
load_dotenv()

def chat_with_rag():
    """Interactive chat with RAG system"""
    # Step 1: Initialize
    print("\n Initializing RAG...")
    rag = SimpleRAG()
    
    # Step 2: Load documents
    print("\n Initializing documents from /documents folder...")
    documents_folder = Path(__file__).parent / "documents"
    
    if not documents_folder.exists():
        print("Documents folder not found!")
        return
    
    results = rag.add_documents_from_folder(str(documents_folder))
    for result in results:
        print(f"  {result}")
    
    # Step 3: Check stats
    stats = rag.get_stats()
    print(f"\n Loaded {stats['total_chunks']} chunks from your documents")
    
    if stats['total_chunks'] == 0:
        print("\n No documents loaded! Add .txt, .docx, or text-based .pdf files to /documents folder")
        return
    
    print("\n" + "="*70)
    print("Ask anything about your documents\n")
    print("Type 'exit' or 'quit' to stop\n")
    print("="*70)
    
    # Step 4: Interactive chat loop
    while True:
        # Get question from user
        question = input("\nEnter prompt: ").strip()
        
        if question.lower() in ['exit']:
            print("\nThanks for chatting!")
            break
        
        # Skip empty questions
        if not question:
            continue
        
        # Get answer with memory (remembers conversation)
        try:
            answer, sources = rag.ask_with_memory(question)
            
            print(f"\nBot: {answer}")
            print(f"\n📄 Sources: {', '.join(set(sources))}")
            print("-"*70)
            
        except Exception as e:
            print(f"\nError: {e}")

if __name__ == "__main__":
    try:
        chat_with_rag()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\nError: {e}")

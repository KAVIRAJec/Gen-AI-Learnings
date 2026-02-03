"""
Document Indexing Script
Run this first to process and index documents before querying
"""

import os
from document_processor import DocumentProcessor
from vector_store import VectorStore

# CONSTANTS
DOCUMENTS_FOLDER = "documents"
CHROMA_DB_PATH = "chroma_db"

def index_documents():
    """Index all documents in the documents folder"""
    print("=" * 60)
    print("Multi-Modal RAG - Document Indexing")
    print("=" * 60)
    
    print("\n[INFO] Checking documents folder...")
    
    if not os.path.exists(DOCUMENTS_FOLDER):
        os.makedirs(DOCUMENTS_FOLDER)
        print(f"[SUCCESS] Created {DOCUMENTS_FOLDER} folder")
        print("[WARNING] Please add your PDF and image files to the 'documents' folder")
        return False
    
    files = [f for f in os.listdir(DOCUMENTS_FOLDER) 
             if f.endswith(('.pdf', '.png', '.jpg', '.jpeg'))]
    
    if not files:
        print(f"[WARNING] No documents found in {DOCUMENTS_FOLDER} folder")
        print("Supported formats: PDF, PNG, JPG, JPEG")
        return False
    
    print(f"[SUCCESS] Found {len(files)} document(s)")
    for i, f in enumerate(files, 1):
        print(f"{i}. {f}")
    
    # Initialize components
    print("\n[INFO] Initializing components...")
    doc_processor = DocumentProcessor()
    vector_store = VectorStore(CHROMA_DB_PATH)
    
    # Check if already indexed
    if vector_store.is_indexed():
        stats = vector_store.get_stats()
        print(f"\n[WARNING] Vector store already contains {stats['total_chunks']} chunks")
        reindex = input("Re-index all documents? (y/n): ").lower()
        if reindex != 'y':
            print("[INFO] Keeping existing index")
            return True
        print("\n[INFO] Clearing existing index...")
        vector_store.clear()
    
    print("\n[INFO] Processing and indexing documents...")
    
    total_chunks = 0
    
    for i, filename in enumerate(files, 1):
        file_path = os.path.join(DOCUMENTS_FOLDER, filename)
        print(f"\n[{i}/{len(files)}] Processing: {filename}")
        
        try:
            # Process document (extract text, images, tables)
            chunks = doc_processor.process_document(file_path)
            
            # Add to vector store
            vector_store.add_documents(chunks, filename)
            
            total_chunks += len(chunks)
            print(f"[SUCCESS] Indexed {len(chunks)} chunks")
            
        except Exception as e:
            print(f"[ERROR] {str(e)}")
            continue
    
    print("\n" + "=" * 60)
    print("[SUCCESS] Indexing complete!")
    print(f"Total chunks indexed: {total_chunks}")
    print(f"Vector store: {CHROMA_DB_PATH}")
    print("=" * 60)
    return True

def main():
    """Main entry point"""
    try:
        success = index_documents()
        if not success:
            print("\n[WARNING] Add documents to the 'documents' folder and run again")
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        raise

if __name__ == "__main__":
    main()

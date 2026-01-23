"""
Simple RAG Vectorization Script for HR Policy Documents

This script reads PDF documents from the 'documents' folder and creates
a vector database that can be searched semantically.

Steps:
1. Load PDF documents
2. Split them into smaller chunks
3. Create embeddings (vector representations)
4. Store in ChromaDB for fast retrieval
"""
from pathlib import Path
import traceback
import PyPDF2

# LangChain imports for document processing
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document

# CONFIGURATION
SCRIPT_DIR = Path(__file__).parent
DOCUMENTS_FOLDER = SCRIPT_DIR / "documents"
VECTOR_DB_FOLDER = SCRIPT_DIR / "vector_db"

CHUNK_SIZE = 700
CHUNK_OVERLAP = 150
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# STEP 1: LOAD DOCUMENTS
def load_pdf_documents():
    """
    Load all PDF files from the documents folder
    
    Returns:
        list: List of Document objects with content and metadata
    """
    print("="*70)
    print("LOADING DOCUMENTS")
    print("="*70)
    
    # Check if documents folder exists
    if not DOCUMENTS_FOLDER.exists():
        raise FileNotFoundError(
            f"Documents folder not found: {DOCUMENTS_FOLDER}\n"
            f"Please create it and add your PDF files."
        )
    
    # Find all PDF files
    pdf_files = list(DOCUMENTS_FOLDER.glob("*.pdf"))
    
    if not pdf_files:
        raise FileNotFoundError(
            f"No PDF files found in {DOCUMENTS_FOLDER}\n"
            f"Please add your HR policy PDF files."
        )
    
    print(f"-> Found {len(pdf_files)} PDF file(s)\n")
    
    # Load each PDF file
    all_documents = []
    for pdf_file in pdf_files:
        print(f"  Loading: {pdf_file.name}")
        try:
            # Open PDF file
            with open(pdf_file, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                
                # Extract text from each page
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    
                    # Create Document object for each page
                    if text.strip():  # Only add if page has text
                        doc = Document(
                            page_content=text,
                            metadata={
                                'source': str(pdf_file),
                                'page': page_num + 1,
                                'total_pages': num_pages
                            }
                        )
                        all_documents.append(doc)
                
                print(f"Loaded {num_pages} page(s)")
                
        except Exception as e:
            print(f"    ✗ Error loading {pdf_file.name}: {e}")
            continue
    
    print(f"\n-> Total pages loaded: {len(all_documents)}")
    
    # Show summary statistics
    total_words = sum(len(doc.page_content.split()) for doc in all_documents)
    print(f"-> Total words: {total_words:,}")
    
    return all_documents

# STEP 2: SPLIT INTO CHUNKS
def split_into_chunks(documents):
    """
    Split documents into smaller chunks for better retrieval

    Args:
        documents: List of Document objects
    
    Returns:
        list: List of smaller document chunks
    """
    print("\n" + "="*70)
    print("SPLITTING INTO CHUNKS")
    print("="*70)
    print(f"Chunk size: {CHUNK_SIZE} characters")
    print(f"Chunk overlap: {CHUNK_OVERLAP} characters\n")
    
    # Create text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]  # Try to split on paragraphs first
    )
    chunks = text_splitter.split_documents(documents)
    
    print(f"-> Created {len(chunks)} chunks from {len(documents)} document(s)\n")
    return chunks

# STEP 3: CREATE EMBEDDINGS
def initialize_embeddings():
    """
    Initialize the embedding model
    Embeddings convert text into vector representations (arrays of numbers).
    Similar texts will have similar vectors.

    Returns:
        HuggingFaceEmbeddings: Initialized embedding model
    """
    print("\n" + "="*70)
    print("INITIALIZING EMBEDDING MODEL")
    print("="*70)
    print(f"Model: {EMBEDDING_MODEL}\n")
    
    # Initialize embeddings with sentence-transformers
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    print("-> Embedding model initialized\n")
    return embeddings

# STEP 4: CREATE VECTOR DATABASE
def create_vector_database(chunks, embeddings):
    """
    Create ChromaDB vector database from document chunks
    ChromaDB stores:
    - Text chunks
    - Their vector embeddings
    - Metadata (source file, page number, etc.)
    
    Args:
        chunks: List of document chunks
        embeddings: Embedding model
    
    Returns:
        Chroma: Vector database instance
    """
    print("\n" + "="*70)
    print("CREATING VECTOR DATABASE")
    print("="*70)
    print(f"Database location: {VECTOR_DB_FOLDER}\n")
    
    # Delete existing database if it exists
    if VECTOR_DB_FOLDER.exists():
        import shutil
        shutil.rmtree(VECTOR_DB_FOLDER)
        print("Existing database deleted\n")
    
    # Create new vector database
    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(VECTOR_DB_FOLDER),
        collection_name="hr_policies"
    )
    
    # Get count of stored vectors
    vector_count = vector_db._collection.count()
    print(f"-> Database created with {vector_count} vectors\n")
    return vector_db

# MAIN EXECUTION
def main():
    """
    Main function that runs the complete vectorization process
    """
    print("\n" + "="*70)
    print("  HR POLICY VECTORIZATION SYSTEM")
    print("="*70)

    try:
        # Run all steps
        documents = load_pdf_documents()
        chunks = split_into_chunks(documents)
        embeddings = initialize_embeddings()
        create_vector_database(chunks, embeddings)
        
        # Success message
        print("="*70)
        print("-> VECTORIZATION COMPLETE!")
        print("="*70)
        print(f"-> Documents processed: {len(documents)}")
        print(f"-> Chunks created: {len(chunks)}")
        print(f"-> Database location: {VECTOR_DB_FOLDER}")
        print("\n")
        
    except Exception as e:
        print(f"Error during vectorization: {e}")
        
        traceback.print_exc()

# Run the script
if __name__ == "__main__":
    main()

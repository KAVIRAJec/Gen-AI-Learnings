"""
RAG Vectorization Script for IT Documents
"""
import sys
import os
from pathlib import Path
import PyPDF2

# LangChain imports for document processing
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.schema import Document

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# CONFIGURATION
SCRIPT_DIR = Path(__file__).parent
DOCUMENTS_FOLDER = SCRIPT_DIR.parent.parent / "docs" / "it"
VECTOR_DB_FOLDER = SCRIPT_DIR / "it_vector_db"

CHUNK_SIZE = 700
CHUNK_OVERLAP = 150
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# STEP 1: LOAD DOCUMENTS
def load_pdf_documents() -> list[Document]:
    """
    Load all PDF files from the IT documents folder
    """
    print("="*70)
    print("LOADING IT DOCUMENTS")
    print("="*70)
    
    # Find all PDF files
    pdf_files = list(DOCUMENTS_FOLDER.glob("*.pdf"))
    if not pdf_files:
        print(f"No PDF files found in {DOCUMENTS_FOLDER}\n")
    
    print(f"-> Found {len(pdf_files)} PDF file(s)\n")
    
    # Load each PDF file
    all_documents = []
    for pdf_file in pdf_files:
        print(f"-> Loading: {pdf_file.name}")
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
                
                print(f"-> Loaded {num_pages} page(s)")
                
        except Exception as e:
            print(f"-> Error loading {pdf_file.name}: {e}")
            continue
    
    print(f"\n-> Total pages loaded: {len(all_documents)}")
    
    total_words = sum(len(doc.page_content.split()) for doc in all_documents)
    print(f"-> Total words: {total_words:,}")
    return all_documents


# STEP 2: SPLIT DOCUMENTS INTO CHUNKS
def split_documents(documents: list[Document]) -> list[Document]:
    """
    Split documents into smaller chunks for better retrieval
    """
    print("\n" + "="*70)
    print("SPLITTING DOCUMENTS INTO CHUNKS")
    print("="*70)
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    
    chunks = text_splitter.split_documents(documents)
    
    print(f"-> Created {len(chunks)} chunks")
    print(f"-> Chunk size: {CHUNK_SIZE} characters")
    print(f"-> Chunk overlap: {CHUNK_OVERLAP} characters")
    return chunks


# STEP 3: CREATE EMBEDDINGS AND VECTOR STORE
def create_vector_store(chunks: list[Document]) -> Chroma:
    """
    Create embeddings and store in ChromaDB
    """
    print("\n" + "="*70)
    print("CREATING VECTOR DATABASE")
    print("="*70)
    
    # Initialize embedding model
    print(f"-> Loading embedding model: {EMBEDDING_MODEL}")
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={'device': 'cpu'}
    )
    
    # Create or update vector store
    print(f"-> Creating vector database at: {VECTOR_DB_FOLDER}")
    
    # Delete existing vector store if it exists
    if VECTOR_DB_FOLDER.exists():
        import shutil
        shutil.rmtree(VECTOR_DB_FOLDER)
        print("-> Deleted existing vector database")
    
    # Create new vector store
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(VECTOR_DB_FOLDER)
    )
    
    print(f"-> Stored {len(chunks)} document chunks in vector database")
    return vector_store


# MAIN FUNCTION
def main():
    """
    Main function to orchestrate the vectorization process
    """
    try:
        print("\n" + "="*70)
        print("IT DOCUMENT VECTORIZATION")
        print("="*70)
        
        # Step 1: Load documents
        documents = load_pdf_documents()
        
        if not documents:
            print("\n-> No documents loaded. Exiting.")
            return
        
        # Step 2: Split into chunks
        chunks = split_documents(documents)
        
        # Step 3: Create vector store
        create_vector_store(chunks)
        print("\n-> IT document vectorization completed successfully.")
    except Exception as e:
        print(f"\nError during vectorization: {e}")

if __name__ == "__main__":
    main()

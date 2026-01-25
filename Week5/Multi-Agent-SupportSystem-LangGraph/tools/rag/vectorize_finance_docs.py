""" 
RAG Vectorization Script for Finance Documents
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
DOCUMENTS_FOLDER = SCRIPT_DIR.parent.parent / "docs" / "finance"
VECTOR_DB_FOLDER = SCRIPT_DIR / "finance_vector_db"

CHUNK_SIZE = 700
CHUNK_OVERLAP = 150
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# STEP 1: LOAD DOCUMENTS
def load_pdf_documents() -> list[Document]:
    """
    Load all PDF files from the Finance documents folder
    """
    print("="*70)
    print("LOADING FINANCE DOCUMENTS")
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
    
    avg_chunk_size = sum(len(chunk.page_content) for chunk in chunks) / len(chunks)
    print(f"-> Average chunk size: {avg_chunk_size:.0f} characters")
    
    return chunks


# STEP 3: CREATE VECTOR DATABASE
def create_vector_store(chunks: list[Document]):
    """
    Create a vector database from document chunks
    """
    print("\n" + "="*70)
    print("CREATING VECTOR DATABASE")
    print("="*70)
    
    print(f"-> Using embedding model: {EMBEDDING_MODEL}")
    
    # Initialize embeddings model
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    
    print("-> Embedding dimension: 384")
    
    # Create vector store folder if it doesn't exist
    VECTOR_DB_FOLDER.mkdir(parents=True, exist_ok=True)
    
    print(f"-> Saving to: {VECTOR_DB_FOLDER}")
    print(f"-> Vectorizing {len(chunks)} chunks...")
    
    # Create Chroma vector database
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(VECTOR_DB_FOLDER)
    )
    
    print("-> Vector database created successfully")
    print(f"-> Collection contains {len(chunks)} vectors")
    
    return vectorstore

# MAIN FUNCTION
def main():
    """
    Main function to orchestrate the vectorization process
    """
    try:
        print("\n" + "="*70)
        print("STARTING FINANCE DOCUMENT VECTORIZATION")
        print("="*70)
        
        # Load documents
        documents = load_pdf_documents()
        
        if not documents:
            print("No documents to process. Exiting.")
            return
        
        # Split documents into chunks
        chunks = split_documents(documents)
        
        # Create vector store
        create_vector_store(chunks)
        print("FINANCE DOCUMENT VECTORIZATION COMPLETED SUCCESSFULLY")
        
    except Exception as e:
        print(f"-> Error during vectorization process: {e}")
if __name__ == "__main__":
    main()

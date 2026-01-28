"""
Document Vectorization Script
(Reuse from Week4 if available, or create custom based on your documents)
"""
import sys
from pathlib import Path
import PyPDF2

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.schema import Document

# Configuration
DOCS_FOLDER = Path(__file__).parent / "docs"
VECTOR_DB_FOLDER = Path(__file__).parent / "vector_db"
CHUNK_SIZE = 700
CHUNK_OVERLAP = 150
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


def load_pdf_documents():
    """Load all PDF files from docs folder"""
    print("="*70)
    print("LOADING DOCUMENTS")
    print("="*70)
    
    pdf_files = list(DOCS_FOLDER.glob("*.pdf"))
    if not pdf_files:
        print(f"No PDF files found in {DOCS_FOLDER}")
        print("Place your documents in docs/ folder")
        sys.exit(1)
    
    print(f"-> Found {len(pdf_files)} PDF file(s)\n")
    
    all_documents = []
    for pdf_file in pdf_files:
        print(f"-> Loading: {pdf_file.name}")
        try:
            with open(pdf_file, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    
                    if text.strip():
                        doc = Document(
                            page_content=text,
                            metadata={
                                'source': str(pdf_file),
                                'page': page_num + 1,
                                'total_pages': num_pages
                            }
                        )
                        all_documents.append(doc)
                
                print(f"   Loaded {num_pages} page(s)")
                
        except Exception as e:
            print(f"   Error: {e}")
            continue
    
    print(f"\n-> Total pages loaded: {len(all_documents)}")
    return all_documents


def split_documents(documents):
    """Split documents into chunks"""
    print("\n" + "="*70)
    print("SPLITTING INTO CHUNKS")
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
    print(f"-> Overlap: {CHUNK_OVERLAP} characters")
    
    return chunks


def create_vector_store(chunks):
    """Create vector database"""
    print("\n" + "="*70)
    print("CREATING VECTOR DATABASE")
    print("="*70)
    
    print(f"-> Using model: {EMBEDDING_MODEL}")
    
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    
    VECTOR_DB_FOLDER.mkdir(parents=True, exist_ok=True)
    
    print(f"-> Saving to: {VECTOR_DB_FOLDER}")
    print(f"-> Vectorizing {len(chunks)} chunks...")
    
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(VECTOR_DB_FOLDER)
    )
    
    print("-> Vector database created successfully")
    print(f"-> Contains {len(chunks)} vectors")
    
    return vectorstore


if __name__ == "__main__":
    print("#"*70)
    print("#"*20 + "DOCUMENT VECTORIZATION" + "#"*20)
    print("#"*70)
    
    documents = load_pdf_documents()
    chunks = split_documents(documents)
    vectorstore = create_vector_store(chunks)
    
    print("\n" + "="*70)
    print("VECTORIZATION COMPLETE")
    print("="*70)
    print(f"-> Vector database: {VECTOR_DB_FOLDER}")

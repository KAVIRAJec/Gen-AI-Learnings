"""
Simple RAG System - Core Functions
Easy to understand, no complex stuff!
"""

import os
from pathlib import Path
from typing import List, Dict, Tuple
import chromadb
from chromadb.utils import embedding_functions
import boto3
import json

# For reading different document types
import PyPDF2
import docx

# STEP 1: READ DOCUMENTS

def read_pdf(file_path: str) -> str:
    """Read text from PDF file"""
    text = ""
    with open(file_path, 'rb') as file:
        pdf = PyPDF2.PdfReader(file)
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def read_docx(file_path: str) -> str:
    """Read text from Word document"""
    doc = docx.Document(file_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

def read_txt(file_path: str) -> str:
    """Read text from text file"""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def read_document(file_path: str) -> str:
    """Read any document type"""
    extension = Path(file_path).suffix.lower()
    
    if not extension:
        raise ValueError("File has no extension (might be hidden or system file)")
    
    if extension == '.pdf':
        return read_pdf(file_path)
    elif extension == '.docx':
        return read_docx(file_path)
    elif extension == '.txt':
        return read_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type: {extension}. Use .pdf, .docx, or .txt files")

# STEP 2: SPLIT INTO CHUNKS

def split_into_chunks(text: str, chunk_size: int = 500) -> List[str]:
    """
    Split text into smaller chunks
    """
    text = text.strip()
    if not text:
        return []
    
    if len(text) <= chunk_size:
        return [text]
    
    # Split by sentences
    sentences = text.replace('\n', ' ').split('. ')
    chunks = []
    current_chunk = []
    current_size = 0
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        
        if not sentence.endswith('.'):
            sentence += '.'
        
        sentence_length = len(sentence)
        
        if current_size + sentence_length > chunk_size and current_chunk:
            chunks.append(' '.join(current_chunk))
            current_chunk = [sentence]
            current_size = sentence_length
        else:
            current_chunk.append(sentence)
            current_size += sentence_length
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

# STEP 3: VECTOR DATABASE SETUP

class VectorDatabase:
    """Simple wrapper around ChromaDB"""
    
    def __init__(self):
        """Initialize the vector database"""
        # Create ChromaDB client
        self.client = chromadb.PersistentClient(path="./chroma_db")
        
        # Setup embedding function (converts text to numbers)
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="documents",
            embedding_function=self.embedding_function
        )
    
    def add_documents(self, texts: List[str], source_file: str):
        """Add documents to the database"""
        if not texts:
            return
        
        # Create unique IDs
        ids = [f"{source_file}_chunk_{i}" for i in range(len(texts))]
        
        # Create metadata
        metadatas = [{"source": source_file, "chunk": i} for i in range(len(texts))]
        
        # Add to database
        self.collection.add(
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
    
    def search(self, query: str, top_k_results: int = 3) -> Dict:
        """Search for relevant documents"""
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k_results
        )
        return results
    
    def get_count(self) -> int:
        """Get total number of documents"""
        return self.collection.count()

# STEP 4: CLAUDE LLM CLIENT

class ClaudeClient:
    """Simple Claude LLM client"""
    
    def __init__(self):
        """Initialize Claude client"""
        self.client = boto3.client(
            service_name='bedrock-runtime',
            region_name=os.getenv('AWS_REGION', 'us-east-1'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        self.model_id = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
    
    def generate(self, prompt: str, max_tokens: int = 1000) -> str:
        """Generate response from Claude"""
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": 0.3,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        try:
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body)
            )
            
            response_body = json.loads(response['body'].read())
            return response_body['content'][0]['text']
        
        except Exception as e:
            return f"Error: {str(e)}"

# STEP 5: BUILD RAG SYSTEM

class SimpleRAG:
    """Simple RAG system - easy to understand!"""
    
    def __init__(self):
        """Initialize RAG system"""
        self.vector_db = VectorDatabase()
        self.llm = ClaudeClient()
        self.conversation_history = []
    
    def add_document(self, file_path: str) -> str:
        """Add a document to the system"""
        filename = Path(file_path).name
        
        try:
            text = read_document(file_path)
            if not text or len(text.strip()) == 0:
                return f"{filename}: No text extracted (PDF might be image-based)"
            
            # Split into chunks
            chunks = split_into_chunks(text)
            if len(chunks) == 0:
                return f"{filename}: No chunks created (text too short or formatting issue)"
            
            # Add to vector database
            self.vector_db.add_documents(chunks, filename)
            
            return f"Added {filename} ({len(chunks)} chunks)"
        
        except Exception as e:
            return f"{filename}: {str(e)}"
    
    def add_documents_from_folder(self, folder_path: str) -> List[str]:
        """Add all documents from a folder"""
        results = []
        folder = Path(folder_path)
        
        for file_path in folder.glob("*"):
            if file_path.is_file():
                result = self.add_document(str(file_path))
                results.append(result)
        
        return results
    
    def ask(self, question: str, n_chunks: int = 3) -> Tuple[str, List[str]]:
        """
        Ask a question and get an answer!
        Returns: (answer, sources)
        """
        # Step 1: Find relevant chunks
        search_results = self.vector_db.search(question, n_chunks)
        
        # Step 2: Get the context
        relevant_texts = search_results['documents'][0]
        sources = [meta['source'] for meta in search_results['metadatas'][0]]
        
        # Combine into context
        context = "\n\n".join(relevant_texts)
        
        # Step 3: Create prompt
        prompt = f"""Based on the following context, answer the question.
                If you can't find the answer in the context, say "I don't have enough information to answer that."

                Context:
                {context}

                Question: {question}

                Answer:"""
        
        # Step 4: Get answer from Claude
        answer = self.llm.generate(prompt)
        
        # Step 5: Save to history
        self.conversation_history.append({
            "question": question,
            "answer": answer,
            "sources": sources
        })
        
        return answer, sources
    
    def ask_with_memory(self, question: str, n_chunks: int = 3) -> Tuple[str, List[str]]:
        """
        Ask a question with conversation memory, for follow-up questions
        """
        # If there's history, contextualize the question
        if self.conversation_history:
            # Get last 3 exchanges
            recent_history = self.conversation_history[-3:]
            history_text = "\n".join([
                f"Q: {h['question']}\nA: {h['answer']}" 
                for h in recent_history
            ])
            
            # Make the question standalone
            contextualize_prompt = f"""Given this conversation history, rewrite the user's question to be standalone.

                                    Conversation History:
                                    {history_text}

                                    New Question: {question}

                                    Standalone Question:"""
            
            standalone_question = self.llm.generate(contextualize_prompt, max_tokens=200)
        else:
            standalone_question = question
        
        # Find relevant chunks using standalone question
        search_results = self.vector_db.search(standalone_question, n_chunks)
        relevant_texts = search_results['documents'][0]
        sources = [meta['source'] for meta in search_results['metadatas'][0]]
        context = "\n\n".join(relevant_texts)
        
        # Create prompt with history
        if self.conversation_history:
            prompt = f"""Based on the following context, answer the question.
                    If you can't find the answer in the context, say "I don't have enough information to answer that."

                    Context from documents:
                    {context}

                    Previous conversation:
                    {history_text}

                    Current question: {standalone_question}

                    Answer:"""
        else:
            prompt = f"""Based on the following context, answer the question.
                    If you can't find the answer in the context, say "I don't have enough information to answer that."

                    Context:
                    {context}

                    Question: {standalone_question}

                    Answer:"""
        
        # Step 4: Get answer
        answer = self.llm.generate(prompt)
        
        # Step 5: Save to history
        self.conversation_history.append({
            "question": question,
            "answer": answer,
            "sources": sources
        })
        
        return answer, sources

    def get_stats(self) -> Dict:
        """Get system statistics"""
        return {
            "total_chunks": self.vector_db.get_count(),
            "conversation_length": len(self.conversation_history)
        }

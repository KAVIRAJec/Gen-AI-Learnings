"""
Vector Store using ChromaDB with LangChain
Stores and retrieves document embeddings
"""

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document

class VectorStore:
    """LangChain ChromaDB vector store for document chunks"""
    
    def __init__(self, db_path="chroma_db"):
        """Initialize LangChain ChromaDB vector store"""
        self.db_path = db_path

        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2"
        )

        self.vectorstore = Chroma(
            collection_name="multimodal_documents",
            embedding_function=self.embeddings,
            persist_directory=db_path
        )
        
        print(f"[SUCCESS] Vector store initialized: {db_path}")
    
    def is_indexed(self):
        """Check if documents are already indexed"""
        try:
            # Try to get collection count
            collection = self.vectorstore._collection
            return collection.count() > 0
        except Exception:
            return False
    
    def clear(self):
        """Clear all documents from the collection"""
        try:
            self.vectorstore.delete_collection()
            self.vectorstore = Chroma(
                collection_name="multimodal_documents",
                embedding_function=self.embeddings,
                persist_directory=self.db_path
            )
            print("[SUCCESS] Vector store cleared")
        except Exception as e:
            print(f"[WARNING] Error clearing vector store: {str(e)}")
    
    def add_documents(self, chunks, filename):
        """Add document chunks to the vector store"""
        if not chunks:
            return
        
        # Prepare documents for LangChain
        documents = []
        ids = []
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"{filename}_page{chunk['page_num']}_chunk{i}"
            
            doc = Document(
                page_content=chunk['content'],
                metadata={
                    'filename': chunk['filename'],
                    'page_num': chunk['page_num'],
                    'has_images': chunk['has_images'],
                    'id': chunk_id
                }
            )
            
            documents.append(doc)
            ids.append(chunk_id)
        
        # Add to vector store
        try:
            self.vectorstore.add_documents(documents=documents, ids=ids)
        except Exception as e:
            raise Exception(f"Error adding to vector store: {str(e)}")
    
    def search(self, query, n_results=3):
        """Search for relevant documents using LangChain similarity search"""
        try:
            results = self.vectorstore.similarity_search_with_score(
                query=query,
                k=n_results
            )
            
            # Format results
            formatted_results = []
            
            for doc, score in results:
                formatted_results.append({
                    'id': doc.metadata.get('id', ''),
                    'content': doc.page_content,
                    'metadata': {
                        'filename': doc.metadata.get('filename', ''),
                        'page_num': doc.metadata.get('page_num', 0),
                        'has_images': doc.metadata.get('has_images', False)
                    },
                    'distance': score
                })
            return formatted_results
            
        except Exception as e:
            raise Exception(f"Error searching vector store: {str(e)}")
    
    def get_stats(self):
        """Get statistics about the vector store"""
        try:
            collection = self.vectorstore._collection
            return {
                'total_chunks': collection.count(),
                'collection_name': collection.name
            }
        except Exception:
            return {
                'total_chunks': 0,
                'collection_name': 'multimodal_documents'
            }
    
    def as_retriever(self, **kwargs):
        """Get LangChain retriever for use in chains"""
        return self.vectorstore.as_retriever(**kwargs)

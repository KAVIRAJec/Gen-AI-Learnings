"""
RAG Query Handler using LangChain
Retrieves relevant context and generates answers using Claude
"""

from langchain_aws import ChatBedrock
from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate

# AWS Configuration
AWS_REGION = "us-east-1"
CLAUDE_MODEL = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"

class RAGQuery:
    """Handle RAG queries with context retrieval and answer generation using LangChain"""
    
    def __init__(self, vector_store):
        """Initialize RAG query handler with LangChain components"""
        self.vector_store = vector_store
        
        # Initialize LangChain ChatBedrock
        self.llm = ChatBedrock(
            model_id=CLAUDE_MODEL,
            region_name=AWS_REGION,
            model_kwargs={
                "max_tokens": 3000,
                "temperature": 0.3
            }
        )
        
        # Create custom prompt template
        self.prompt_template = PromptTemplate(
            template="""You are a helpful AI assistant that answers questions based on provided document context.
            **Context from Documents:**
            {context}

            **User Question:**
            {question}

            **Instructions:**
            - Answer the question using ONLY the information from the provided context
            - If the context contains images, tables, or charts analysis, reference them in your answer
            - Be specific and cite which document/page the information comes from
            - If the context doesn't contain enough information to answer, say so clearly
            - Provide a comprehensive but concise answer

            **Answer:**""",
            input_variables=["context", "question"]
        )
        
        # Create RetrievalQA chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(search_kwargs={"k": 3}),
            return_source_documents=True,
            chain_type_kwargs={"prompt": self.prompt_template}
        )
    
    def query(self, question):
        """
        Process a query using LangChain RAG chain
        1. Retrieve relevant context from vector store
        2. Generate answer using Claude with context
        """
        
        try:
            # Use LangChain RetrievalQA chain
            result = self.qa_chain.invoke({"query": question})
            
            # Extract answer and source documents
            answer = result['result']
            source_docs = result.get('source_documents', [])
            
            # Format sources
            sources = self._format_sources_from_docs(source_docs)
            
            # Build context string for reference
            context = self._build_context_from_docs(source_docs)
            
            return {
                'answer': answer,
                'sources': sources,
                'context': context
            }
            
        except Exception as e:
            return {
                'answer': f"Error processing query: {str(e)}",
                'sources': [],
                'context': ""
            }
    
    def _build_context_from_docs(self, docs):
        """Build context string from LangChain documents"""
        context_parts = []
        
        for i, doc in enumerate(docs, 1):
            metadata = doc.metadata
            content = doc.page_content
            
            context_parts.append(f"""
            --- Source {i}: {metadata.get('filename', 'Unknown')} (Page {metadata.get('page_num', 'N/A')}) ---
            {content}
            """)
        return "\n".join(context_parts)
    
    def _format_sources_from_docs(self, docs):
        """Format source information from LangChain documents for display"""
        sources = []
        
        for doc in docs:
            metadata = doc.metadata
            sources.append({
                'filename': metadata.get('filename', 'Unknown'),
                'page_num': metadata.get('page_num', 0),
                'has_images': metadata.get('has_images', False),
                'score': 0.9  # LangChain doesn't always expose scores in this flow
            })
        
        return sources

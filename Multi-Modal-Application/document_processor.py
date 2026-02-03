"""
Document Processor for Multi-Modal Content
Handles PDFs with images, text, and tables using AWS Bedrock Claude via LangChain
"""

import os
import base64
import fitz  # PyMuPDF
from langchain_aws import ChatBedrock

# AWS Configuration
AWS_REGION = "us-east-1"
CLAUDE_MODEL = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
MAX_TOKENS = 3000

class DocumentProcessor:
    """Process multi-modal documents (PDFs with images, text, tables)"""
    
    def __init__(self):
        """Initialize document processor with LangChain ChatBedrock"""
        self.llm = ChatBedrock(
            model_id=CLAUDE_MODEL,
            region_name=AWS_REGION,
            model_kwargs={
                "max_tokens": MAX_TOKENS,
                "temperature": 0.3
            }
        )
        self.max_tokens = MAX_TOKENS
    
    def process_document(self, file_path):
        """
        Process a document and extract multi-modal content
        Returns: List of chunks with metadata
        """
        filename = os.path.basename(file_path)
        file_ext = filename.lower().split('.')[-1]
        
        if file_ext == 'pdf':
            return self._process_pdf(file_path, filename)
        elif file_ext in ['png', 'jpg', 'jpeg']:
            return self._process_image(file_path, filename)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")
    
    def _process_pdf(self, pdf_path, filename):
        """Process PDF with multi-modal content extraction"""
        chunks = []
        
        try:
            doc = fitz.open(pdf_path)
            
            print(f"[INFO] PDF has {len(doc)} page(s)")
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Extract text
                text = page.get_text().strip()
                
                # Extract images from page
                page_images = self._extract_page_images(page, page_num)
                
                # Use Claude to analyze the page (text + images)
                analysis = self._analyze_page_with_claude(text, page_images, page_num + 1)
                
                # Create chunk
                chunk = {
                    'text': text,
                    'analysis': analysis,
                    'page_num': page_num + 1,
                    'has_images': len(page_images) > 0,
                    'filename': filename,
                    'content': f"Page {page_num + 1} of {filename}\n\n{text}\n\n--- AI Analysis ---\n{analysis}"
                }
                
                chunks.append(chunk)
            
            doc.close()
            
        except Exception as e:
            raise Exception(f"Error processing PDF: {str(e)}")
        
        return chunks
    
    def _extract_page_images(self, page, page_num):
        """Extract images from a PDF page"""
        images = []
        
        try:
            # Get page as image
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            img_data = pix.tobytes()
            
            # Convert to base64
            img_base64 = base64.b64encode(img_data).decode('utf-8')
            
            images.append({
                'type': 'page_render',
                'data': img_base64,
                'format': 'png'
            })
            
        except Exception as e:
            print(f"[WARNING] Could not extract image from page {page_num + 1}: {str(e)}")
        
        return images
    
    def _analyze_page_with_claude(self, text, images, page_num):
        """Use Claude to analyze page content including images and tables"""
        
        # Build multi-modal content for LangChain
        from langchain_core.messages import HumanMessage
        
        content = []
        
        # Add images first
        for img in images[:1]:  # Use first image (page render)
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{img['data']}"
                }
            })
        
        # Add analysis prompt
        prompt = f"""Analyze this page {page_num} content comprehensively:

        1. **Text Content**: Summarize the main text
        2. **Images/Diagrams**: Describe any images, charts, or diagrams visible
        3. **Tables**: Identify and describe any tables with their key data
        4. **Structure**: Note headings, sections, or important formatting

        Extracted Text:
        {text[:2000] if text else "[No text extracted]"}

        Provide a detailed analysis that captures all information for RAG retrieval."""

        content.append({
            "type": "text",
            "text": prompt
        })
        
        # Call Claude via LangChain
        try:
            message = HumanMessage(content=content)
            response = self.llm.invoke([message])
            analysis = response.content
            
            return analysis
            
        except Exception as e:
            print(f"       [WARNING] Claude analysis failed for page {page_num}: {str(e)}")
            return text[:1000] if text else ""
    
    def _process_image(self, image_path, filename):
        """Process standalone image file"""
        
        try:
            from langchain_core.messages import HumanMessage
            
            # Read and encode image
            with open(image_path, 'rb') as img_file:
                img_data = img_file.read()
                img_base64 = base64.b64encode(img_data).decode('utf-8')
            
            # Determine image format
            ext = filename.lower().split('.')[-1]
            media_type = f"image/{ext if ext != 'jpg' else 'jpeg'}"
            
            # Build content for LangChain
            content = [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{media_type};base64,{img_base64}"
                    }
                },
                {
                    "type": "text",
                    "text": """Analyze this image comprehensively:

                    1. **Main Subject**: What is the primary focus of this image?
                    2. **Details**: Describe key elements, objects, or features visible
                    3. **Text/Labels**: If any text, labels, or annotations are present, transcribe them
                    4. **Context**: What might this image be used for or represent?

                    Provide a detailed analysis for RAG retrieval."""
                }
            ]
            
            # Call Claude via LangChain
            message = HumanMessage(content=content)
            response = self.llm.invoke([message])
            analysis = response.content
            
            # Create chunk
            chunk = {
                'text': '',
                'analysis': analysis,
                'page_num': 1,
                'has_images': True,
                'filename': filename,
                'content': f"Image: {filename}\n\n--- AI Analysis ---\n{analysis}"
            }
            
            return [chunk]
            
        except Exception as e:
            raise Exception(f"Error processing image: {str(e)}")

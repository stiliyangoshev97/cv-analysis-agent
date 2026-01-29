"""
PDF Processing Service.
Handles extraction of text content from PDF files using pdfplumber.
"""

import pdfplumber
import io
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class PDFService:
    """Service for processing PDF files and extracting text content."""
    
    @staticmethod
    def extract_text_from_bytes(pdf_bytes: bytes) -> str:
        """
        Extract all text content from a PDF file given as bytes.
        
        Args:
            pdf_bytes: Raw bytes of the PDF file
            
        Returns:
            Extracted text content as a single string
            
        Raises:
            ValueError: If the PDF cannot be processed
        """
        try:
            # Open PDF from bytes using io.BytesIO
            pdf_file = io.BytesIO(pdf_bytes)
            
            text_content: list[str] = []
            
            with pdfplumber.open(pdf_file) as pdf:
                # Iterate through all pages and extract text
                for page in pdf.pages:
                    page_text = page.extract_text()
                    
                    if page_text and page_text.strip():
                        text_content.append(page_text)
            
            # Join all pages with double newlines
            full_text = "\n\n".join(text_content)
            
            if not full_text.strip():
                raise ValueError("No text content could be extracted from the PDF")
                
            logger.info(f"Successfully extracted {len(full_text)} characters from PDF")
            return full_text
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise ValueError(f"Failed to process PDF: {e}")
    
    @staticmethod
    def validate_pdf(pdf_bytes: bytes) -> tuple[bool, Optional[str]]:
        """
        Validate that the provided bytes represent a valid PDF.
        
        Args:
            pdf_bytes: Raw bytes to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            pdf_file = io.BytesIO(pdf_bytes)
            
            with pdfplumber.open(pdf_file) as pdf:
                page_count = len(pdf.pages)
                
                if page_count == 0:
                    return False, "PDF has no pages"
                    
            return True, None
            
        except Exception as e:
            return False, f"Invalid PDF file: {e}"

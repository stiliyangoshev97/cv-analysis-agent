"""PDF Processing Service for CV text extraction.

This module provides functionality to extract text content from PDF files
using the pdfplumber library. It handles both single and multi-page PDFs.

Classes:
    PDFService: Static service class for PDF operations.

Example:
    Extracting text from uploaded file::
    
        pdf_bytes = await file.read()
        text = PDFService.extract_text_from_bytes(pdf_bytes)
        print(f"Extracted {len(text)} characters")

Note:
    Supports standard PDF formats. May not handle scanned documents
    (image-only PDFs) - consider adding OCR in future.
"""

import pdfplumber
import io
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class PDFService:
    """Service for processing PDF files and extracting text content.
    
    Provides static methods for PDF validation and text extraction.
    Uses pdfplumber for reliable text extraction from PDF documents.
    
    Example:
        >>> is_valid, error = PDFService.validate_pdf(pdf_bytes)
        >>> if is_valid:
        ...     text = PDFService.extract_text_from_bytes(pdf_bytes)
    
    Note:
        All methods are static - no instance needed.
    """
    
    @staticmethod
    def extract_text_from_bytes(pdf_bytes: bytes) -> str:
        """Extract all text content from a PDF file.
        
        Processes each page of the PDF and concatenates the extracted
        text with double newlines between pages.
        
        Args:
            pdf_bytes: Raw bytes of the PDF file (e.g., from file upload).
        
        Returns:
            Extracted text content as a single string with pages
            separated by double newlines.
        
        Raises:
            ValueError: If the PDF cannot be processed or contains
                no extractable text.
        
        Example:
            >>> with open("resume.pdf", "rb") as f:
            ...     pdf_bytes = f.read()
            >>> text = PDFService.extract_text_from_bytes(pdf_bytes)
            >>> print(text[:100])  # First 100 characters
        
        Note:
            Empty pages are skipped. If all pages are empty (e.g.,
            scanned document), raises ValueError.
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
        """Validate that bytes represent a valid PDF file.
        
        Attempts to open the PDF and verify it has at least one page.
        
        Args:
            pdf_bytes: Raw bytes to validate.
        
        Returns:
            Tuple of (is_valid, error_message):
                - (True, None) if valid PDF
                - (False, "error description") if invalid
        
        Example:
            >>> is_valid, error = PDFService.validate_pdf(pdf_bytes)
            >>> if not is_valid:
            ...     return {"error": error}
        
        Note:
            This only validates PDF structure, not content quality.
            A valid PDF may still have no extractable text.
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

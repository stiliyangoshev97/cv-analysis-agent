"""
Document Processing

Handles loading and chunking of CV documents (PDF, DOCX).
Uses LangChain document loaders and text splitters.
"""

import tempfile
from pathlib import Path
from typing import BinaryIO

from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


# Default chunking parameters optimized for CV content
DEFAULT_CHUNK_SIZE = 500  # Characters per chunk
DEFAULT_CHUNK_OVERLAP = 50  # Overlap between chunks for context


def get_text_splitter(
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> RecursiveCharacterTextSplitter:
    """
    Get a configured text splitter for chunking documents.
    
    Uses RecursiveCharacterTextSplitter which tries to split on natural
    boundaries (paragraphs, sentences, words) before resorting to character-level splits.
    
    Args:
        chunk_size: Maximum characters per chunk.
        chunk_overlap: Number of characters to overlap between chunks.
    
    Returns:
        Configured RecursiveCharacterTextSplitter.
    
    Example:
        ```python
        splitter = get_text_splitter(chunk_size=1000)
        chunks = splitter.split_text(long_text)
        ```
    """
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )


async def load_pdf(file_path: str | Path) -> list[Document]:
    """
    Load a PDF file and return LangChain Document objects.
    
    Args:
        file_path: Path to the PDF file.
    
    Returns:
        List of Document objects (one per page).
    
    Example:
        ```python
        documents = await load_pdf("/path/to/cv.pdf")
        for doc in documents:
            print(doc.page_content)
            print(doc.metadata)  # {"source": "/path/to/cv.pdf", "page": 0}
        ```
    """
    loader = PyPDFLoader(str(file_path))
    return loader.load()


async def load_docx(file_path: str | Path) -> list[Document]:
    """
    Load a DOCX file and return LangChain Document objects.
    
    Args:
        file_path: Path to the DOCX file.
    
    Returns:
        List containing a single Document with the full text.
    
    Example:
        ```python
        documents = await load_docx("/path/to/cv.docx")
        print(documents[0].page_content)
        ```
    """
    loader = Docx2txtLoader(str(file_path))
    return loader.load()


async def load_document(file_path: str | Path) -> list[Document]:
    """
    Load a document (PDF or DOCX) based on file extension.
    
    Args:
        file_path: Path to the document file.
    
    Returns:
        List of Document objects.
    
    Raises:
        ValueError: If file extension is not supported.
    
    Example:
        ```python
        documents = await load_document("/path/to/cv.pdf")
        # or
        documents = await load_document("/path/to/cv.docx")
        ```
    """
    path = Path(file_path)
    extension = path.suffix.lower()
    
    if extension == ".pdf":
        return await load_pdf(path)
    elif extension in (".docx", ".doc"):
        return await load_docx(path)
    else:
        raise ValueError(f"Unsupported file extension: {extension}. Supported: .pdf, .docx")


async def load_document_from_bytes(
    file_content: bytes,
    filename: str,
) -> list[Document]:
    """
    Load a document from bytes (e.g., from file upload).
    
    Writes content to a temporary file, loads it, then cleans up.
    
    Args:
        file_content: Raw bytes of the document.
        filename: Original filename (used to determine file type).
    
    Returns:
        List of Document objects.
    
    Raises:
        ValueError: If file extension is not supported.
    
    Example:
        ```python
        # From FastAPI UploadFile
        content = await upload_file.read()
        documents = await load_document_from_bytes(content, upload_file.filename)
        ```
    """
    extension = Path(filename).suffix.lower()
    
    if extension not in (".pdf", ".docx", ".doc"):
        raise ValueError(f"Unsupported file extension: {extension}. Supported: .pdf, .docx")
    
    # Write to temp file
    with tempfile.NamedTemporaryFile(suffix=extension, delete=False) as tmp:
        tmp.write(file_content)
        tmp_path = tmp.name
    
    try:
        return await load_document(tmp_path)
    finally:
        # Clean up temp file
        Path(tmp_path).unlink(missing_ok=True)


def process_documents(
    documents: list[Document],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[Document]:
    """
    Split documents into smaller chunks for embedding.
    
    Args:
        documents: List of Document objects to split.
        chunk_size: Maximum characters per chunk.
        chunk_overlap: Number of characters to overlap between chunks.
    
    Returns:
        List of chunked Document objects with preserved metadata.
    
    Example:
        ```python
        documents = await load_pdf("/path/to/cv.pdf")
        chunks = process_documents(documents, chunk_size=500)
        
        for i, chunk in enumerate(chunks):
            print(f"Chunk {i}: {chunk.page_content[:100]}...")
        ```
    """
    splitter = get_text_splitter(chunk_size, chunk_overlap)
    return splitter.split_documents(documents)


def extract_full_text(documents: list[Document]) -> str:
    """
    Extract and concatenate full text from documents.
    
    Useful when you need the complete CV text for evaluation
    rather than individual chunks.
    
    Args:
        documents: List of Document objects.
    
    Returns:
        Concatenated text from all documents.
    
    Example:
        ```python
        documents = await load_pdf("/path/to/cv.pdf")
        full_text = extract_full_text(documents)
        evaluation = await evaluate_cv(full_text, criteria)
        ```
    """
    return "\n\n".join(doc.page_content for doc in documents)


class DocumentProcessor:
    """
    High-level document processor that handles the complete pipeline.
    
    Combines document loading, text extraction, and chunking into
    a single interface.
    
    Example:
        ```python
        processor = DocumentProcessor(chunk_size=500)
        
        # From file path
        result = await processor.process_file("/path/to/cv.pdf")
        
        # From uploaded bytes
        result = await processor.process_upload(content, "cv.pdf")
        
        # Access results
        print(result.full_text)
        print(f"Generated {len(result.chunks)} chunks")
        ```
    """
    
    def __init__(
        self,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    ):
        """
        Initialize the document processor.
        
        Args:
            chunk_size: Maximum characters per chunk.
            chunk_overlap: Number of characters to overlap between chunks.
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    async def process_file(self, file_path: str | Path) -> "ProcessedDocument":
        """
        Process a document file and return structured result.
        
        Args:
            file_path: Path to the document file.
        
        Returns:
            ProcessedDocument with full_text, chunks, and metadata.
        """
        documents = await load_document(file_path)
        return self._process_documents(documents, str(file_path))
    
    async def process_upload(
        self,
        file_content: bytes,
        filename: str,
    ) -> "ProcessedDocument":
        """
        Process an uploaded document and return structured result.
        
        Args:
            file_content: Raw bytes of the document.
            filename: Original filename.
        
        Returns:
            ProcessedDocument with full_text, chunks, and metadata.
        """
        documents = await load_document_from_bytes(file_content, filename)
        return self._process_documents(documents, filename)
    
    def _process_documents(
        self,
        documents: list[Document],
        source: str,
    ) -> "ProcessedDocument":
        """Internal method to process loaded documents."""
        full_text = extract_full_text(documents)
        chunks = process_documents(
            documents,
            self.chunk_size,
            self.chunk_overlap,
        )
        
        return ProcessedDocument(
            full_text=full_text,
            chunks=chunks,
            source=source,
            page_count=len(documents),
            chunk_count=len(chunks),
        )


class ProcessedDocument:
    """
    Result of document processing.
    
    Attributes:
        full_text: Complete text extracted from the document.
        chunks: List of Document chunks for embedding.
        source: Original file path or filename.
        page_count: Number of pages in the original document.
        chunk_count: Number of chunks generated.
    """
    
    def __init__(
        self,
        full_text: str,
        chunks: list[Document],
        source: str,
        page_count: int,
        chunk_count: int,
    ):
        self.full_text = full_text
        self.chunks = chunks
        self.source = source
        self.page_count = page_count
        self.chunk_count = chunk_count
    
    def get_chunk_texts(self) -> list[str]:
        """Get just the text content from each chunk."""
        return [chunk.page_content for chunk in self.chunks]
    
    def __repr__(self) -> str:
        return (
            f"ProcessedDocument(source='{self.source}', "
            f"pages={self.page_count}, chunks={self.chunk_count})"
        )

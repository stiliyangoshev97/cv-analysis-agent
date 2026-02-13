"""Parser Agent for document processing.

This agent handles document parsing tasks including PDF and DOCX
extraction, text chunking, and initial validation.

Tasks:
    PARSE_DOCUMENT: Parse a file and extract text with chunks.
    EXTRACT_TEXT: Extract raw text from a document.

Example:
    Using the parser agent::
    
        agent = ParserAgent(context)
        result = await agent.execute(AgentMessage(
            task_type=TaskType.PARSE_DOCUMENT,
            payload={"file_content": bytes, "filename": "resume.pdf"}
        ))
        # result.data contains: full_text, chunks, chunk_count
"""

import logging
from typing import Set

from .base import BaseAgent, AgentContext
from .messages import AgentMessage, AgentResult, TaskType
from .tools import validate_file, extract_candidate_name, DocumentTools

logger = logging.getLogger(__name__)


class ParserAgent(BaseAgent):
    """Agent for document parsing and text extraction.
    
    Handles PDF and DOCX files, extracting structured text and
    creating chunks for embedding generation.
    
    Supported Tasks:
        - PARSE_DOCUMENT: Full parsing with chunking
        - EXTRACT_TEXT: Simple text extraction
    
    Payload Requirements:
        - file_content (bytes): Raw file bytes
        - filename (str): Original filename
    
    Result Data:
        - full_text (str): Complete extracted text
        - chunks (List[str]): Text chunks for embeddings
        - chunk_count (int): Number of chunks
        - candidate_name (str|None): Extracted candidate name
    
    Example:
        >>> agent = ParserAgent(context)
        >>> msg = AgentMessage(
        ...     task_type=TaskType.PARSE_DOCUMENT,
        ...     payload={"file_content": pdf_bytes, "filename": "resume.pdf"}
        ... )
        >>> result = await agent.execute(msg)
        >>> print(f"Extracted {result.data['chunk_count']} chunks")
    """
    
    name = "parser_agent"
    supported_tasks: Set[TaskType] = {
        TaskType.PARSE_DOCUMENT,
        TaskType.EXTRACT_TEXT,
    }
    
    def __init__(self, context: AgentContext) -> None:
        """Initialize parser agent.
        
        Args:
            context: Shared AgentContext with repositories.
        """
        super().__init__(context)
        self.document_tools = DocumentTools()
    
    async def process(self, message: AgentMessage) -> AgentResult:
        """Process a document parsing task.
        
        Routes to appropriate handler based on task type.
        
        Args:
            message: AgentMessage with file content and filename.
        
        Returns:
            AgentResult with extracted text and chunks.
        """
        if message.task_type == TaskType.PARSE_DOCUMENT:
            return await self._parse_document(message)
        elif message.task_type == TaskType.EXTRACT_TEXT:
            return await self._extract_text(message)
        else:
            return AgentResult.fail(
                f"Unknown task type: {message.task_type}",
                agent_name=self.name,
            )
    
    async def _parse_document(self, message: AgentMessage) -> AgentResult:
        """Parse a document with full processing.
        
        1. Validates file type and content
        2. Extracts text using LangChain loaders
        3. Chunks text for embedding generation
        4. Attempts to extract candidate name
        
        Args:
            message: AgentMessage with file_content and filename.
        
        Returns:
            AgentResult with text, chunks, and metadata.
        """
        # Extract payload
        file_content = message.payload.get("file_content")
        filename = message.payload.get("filename")
        
        # Validate inputs
        if not file_content:
            return AgentResult.fail("Missing file_content in payload", self.name)
        if not filename:
            return AgentResult.fail("Missing filename in payload", self.name)
        
        # Validate file
        is_valid, error = validate_file(file_content, filename)
        if not is_valid:
            return AgentResult.fail(error, self.name)
        
        self._logger.info(f"Parsing document: {filename}")
        
        # Process document with LangChain
        try:
            processed = await self.document_tools.process(file_content, filename)
        except Exception as e:
            self._logger.error(f"Document processing failed: {e}")
            return AgentResult.fail(f"Failed to parse document: {e}", self.name)
        
        # Extract candidate name
        candidate_name = extract_candidate_name(processed.full_text)
        
        self._logger.info(
            f"Parsed document: {len(processed.full_text)} chars, "
            f"{processed.chunk_count} chunks, candidate: {candidate_name}"
        )
        
        return AgentResult.ok(
            data={
                "full_text": processed.full_text,
                "chunks": processed.chunks,
                "chunk_count": processed.chunk_count,
                "candidate_name": candidate_name,
                "filename": filename,
            },
            agent_name=self.name,
            next_task=TaskType.EVALUATE_CV,  # Chain to scoring
        )
    
    async def _extract_text(self, message: AgentMessage) -> AgentResult:
        """Extract raw text from a document.
        
        Simpler version of parse_document that only extracts text
        without chunking or additional processing.
        
        Args:
            message: AgentMessage with file_content and filename.
        
        Returns:
            AgentResult with extracted text.
        """
        # Extract payload
        file_content = message.payload.get("file_content")
        filename = message.payload.get("filename")
        
        # Validate inputs
        if not file_content:
            return AgentResult.fail("Missing file_content in payload", self.name)
        if not filename:
            return AgentResult.fail("Missing filename in payload", self.name)
        
        # Validate file
        is_valid, error = validate_file(file_content, filename)
        if not is_valid:
            return AgentResult.fail(error, self.name)
        
        # Process document
        try:
            processed = await self.document_tools.process(file_content, filename)
        except Exception as e:
            return AgentResult.fail(f"Failed to extract text: {e}", self.name)
        
        return AgentResult.ok(
            data={
                "full_text": processed.full_text,
                "filename": filename,
            },
            agent_name=self.name,
        )

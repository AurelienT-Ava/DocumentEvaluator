"""Document parser for Word documents with chunking support."""

from dataclasses import dataclass
from pathlib import Path
from typing import List
import tiktoken
from docx import Document


@dataclass
class DocumentChunk:
    """Represents a chunk of document text."""
    
    text: str
    token_count: int
    chunk_index: int
    total_chunks: int


class DocumentParser:
    """Parser for Word documents with automatic chunking."""
    
    def __init__(self, max_tokens_per_chunk: int = 4000, encoding_name: str = "cl100k_base"):
        """
        Initialize document parser.
        
        Args:
            max_tokens_per_chunk: Maximum number of tokens per chunk
            encoding_name: Tokenizer encoding name (cl100k_base for GPT-4/GPT-3.5-turbo)
        """
        self.max_tokens_per_chunk = max_tokens_per_chunk
        self.encoding = tiktoken.get_encoding(encoding_name)
    
    def extract_text(self, file_path: Path) -> str:
        """
        Extract text from a Word document.
        
        Args:
            file_path: Path to the .docx file
        
        Returns:
            Extracted text from the document
        
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is not a valid .docx file
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if file_path.suffix.lower() != '.docx':
            raise ValueError(f"File must be a .docx file: {file_path}")
        
        try:
            doc = Document(file_path)
            paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
            return '\n\n'.join(paragraphs)
        except Exception as e:
            raise ValueError(f"Failed to parse Word document: {e}")
    
    def count_tokens(self, text: str) -> int:
        """
        Count the number of tokens in a text.
        
        Args:
            text: Text to count tokens for
        
        Returns:
            Number of tokens
        """
        return len(self.encoding.encode(text))
    
    def chunk_text(self, text: str) -> List[DocumentChunk]:
        """
        Split text into chunks based on token limits.
        
        Attempts to split on paragraph boundaries when possible.
        
        Args:
            text: Text to chunk
        
        Returns:
            List of DocumentChunk objects
        """
        total_tokens = self.count_tokens(text)
        
        # If text fits in one chunk, return it as is
        if total_tokens <= self.max_tokens_per_chunk:
            return [DocumentChunk(
                text=text,
                token_count=total_tokens,
                chunk_index=0,
                total_chunks=1
            )]
        
        # Split into chunks at paragraph boundaries
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = []
        current_tokens = 0
        
        for para in paragraphs:
            para_tokens = self.count_tokens(para)
            
            # If a single paragraph exceeds max tokens, split it further
            if para_tokens > self.max_tokens_per_chunk:
                # Save current chunk if any
                if current_chunk:
                    chunk_text = '\n\n'.join(current_chunk)
                    chunks.append(chunk_text)
                    current_chunk = []
                    current_tokens = 0
                
                # Split long paragraph by sentences
                sentences = para.split('. ')
                for sentence in sentences:
                    sentence = sentence.strip()
                    if not sentence:
                        continue
                    
                    sentence_tokens = self.count_tokens(sentence)
                    
                    if current_tokens + sentence_tokens > self.max_tokens_per_chunk:
                        if current_chunk:
                            chunk_text = '. '.join(current_chunk) + '.'
                            chunks.append(chunk_text)
                            current_chunk = []
                            current_tokens = 0
                    
                    current_chunk.append(sentence)
                    current_tokens += sentence_tokens
            else:
                # Check if adding this paragraph exceeds limit
                if current_tokens + para_tokens > self.max_tokens_per_chunk:
                    # Save current chunk
                    if current_chunk:
                        chunk_text = '\n\n'.join(current_chunk)
                        chunks.append(chunk_text)
                        current_chunk = []
                        current_tokens = 0
                
                current_chunk.append(para)
                current_tokens += para_tokens
        
        # Add remaining text as final chunk
        if current_chunk:
            chunk_text = '\n\n'.join(current_chunk) if isinstance(current_chunk[0], str) and '\n' not in current_chunk[0] else '. '.join(current_chunk)
            chunks.append(chunk_text)
        
        # Convert to DocumentChunk objects
        total_chunks = len(chunks)
        return [
            DocumentChunk(
                text=chunk_text,
                token_count=self.count_tokens(chunk_text),
                chunk_index=i,
                total_chunks=total_chunks
            )
            for i, chunk_text in enumerate(chunks)
        ]
    
    def parse(self, file_path: Path) -> List[DocumentChunk]:
        """
        Parse a Word document and return chunks.
        
        Args:
            file_path: Path to the .docx file
        
        Returns:
            List of DocumentChunk objects
        
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is not valid or parsing fails
        """
        text = self.extract_text(file_path)
        return self.chunk_text(text)

"""File scanner for discovering Word documents."""

from pathlib import Path
from typing import List


class DocumentScanner:
    """Scanner for finding Word documents in filesystem."""
    
    def __init__(self, extensions: List[str] = None):
        """
        Initialize document scanner.
        
        Args:
            extensions: List of file extensions to scan for (default: ['.docx'])
        """
        self.extensions = extensions or ['.docx']
    
    def scan_file(self, file_path: Path) -> List[Path]:
        """
        Validate and return a single file if it matches criteria.
        
        Args:
            file_path: Path to file
        
        Returns:
            List containing the file path if valid, empty list otherwise
        
        Raises:
            FileNotFoundError: If file doesn't exist
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not file_path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")
        
        if file_path.suffix.lower() in self.extensions:
            return [file_path]
        else:
            raise ValueError(f"File must have one of these extensions: {', '.join(self.extensions)}")
    
    def scan_directory(self, directory_path: Path, recursive: bool = False) -> List[Path]:
        """
        Scan directory for Word documents.
        
        Args:
            directory_path: Path to directory
            recursive: Whether to scan subdirectories recursively
        
        Returns:
            List of paths to Word documents found
        
        Raises:
            FileNotFoundError: If directory doesn't exist
            ValueError: If path is not a directory
        """
        if not directory_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        if not directory_path.is_dir():
            raise ValueError(f"Path is not a directory: {directory_path}")
        
        documents = []
        
        if recursive:
            # Recursive scan
            for ext in self.extensions:
                documents.extend(directory_path.rglob(f'*{ext}'))
        else:
            # Non-recursive scan (only immediate children)
            for ext in self.extensions:
                documents.extend(directory_path.glob(f'*{ext}'))
        
        # Sort for consistent ordering
        return sorted(documents)
    
    def scan(self, path: Path, recursive: bool = False) -> List[Path]:
        """
        Scan a path (file or directory) for Word documents.
        
        Args:
            path: Path to file or directory
            recursive: Whether to scan subdirectories recursively (only for directories)
        
        Returns:
            List of paths to Word documents found
        
        Raises:
            FileNotFoundError: If path doesn't exist
        """
        path = Path(path)
        
        if path.is_file():
            return self.scan_file(path)
        elif path.is_dir():
            return self.scan_directory(path, recursive=recursive)
        else:
            raise FileNotFoundError(f"Path not found: {path}")

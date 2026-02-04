import fitz  # PyMuPDF
from fastapi import UploadFile
import logging
import io

logger = logging.getLogger(__name__)

class FileParser:
    """
    Parses uploaded files to extract text content.
    Supports: .pdf, .md, .txt
    """

    @staticmethod
    async def parse_file(file: UploadFile) -> str:
        """
        Extract text from an uploaded file.
        
        Args:
            file: FastAPI UploadFile object
            
        Returns:
            Extracted text string
        """
        filename = file.filename.lower() if file.filename else ""
        content = await file.read()
        
        # Reset cursor for safety/re-use if needed, though usually read once
        await file.seek(0)
        
        try:
            if filename.endswith(".pdf"):
                return FileParser._parse_pdf(content)
            elif filename.endswith(".md") or filename.endswith(".txt"):
                return FileParser._parse_text(content)
            else:
                # Fallback for now: try decoding as text
                return FileParser._parse_text(content)
        except Exception as e:
            logger.error(f"Failed to parse file {filename}: {e}")
            raise ValueError(f"Could not parse file: {str(e)}")

    @staticmethod
    def _parse_pdf(content: bytes) -> str:
        """Extract text from PDF bytes using PyMuPDF."""
        text = ""
        with fitz.open(stream=content, filetype="pdf") as doc:
            for page in doc:
                text += page.get_text() + "\n"
        return text.strip()

    @staticmethod
    def _parse_text(content: bytes) -> str:
        """Decode bytes to string assuming UTF-8."""
        return content.decode("utf-8")

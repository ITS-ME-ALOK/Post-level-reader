"""
Service for reading PDF files.
"""
import pdfplumber
from typing import Callable, Optional
from utils.logger import logger

class PDFReader:
    """
    Class responsible for extracting text and data from PDF files.
    """
    def __init__(self):
        logger.info("Initializing PDFReader")

    def read_pdf(self, file_path: str, progress_callback: Optional[Callable[[int, int], None]] = None) -> str:
        """
        Reads the specified PDF file.
        """
        logger.debug(f"Reading PDF from: {file_path}")
        return self.extract_text(file_path, progress_callback)

    def extract_text(self, file_path: str, progress_callback: Optional[Callable[[int, int], None]] = None) -> str:
        """
        Extracts raw text from all pages of the given PDF file.
        """
        logger.info(f"Extracting text from: {file_path}")
        extracted_text = []
        try:
            with pdfplumber.open(file_path) as pdf:
                total_pages = len(pdf.pages)
                logger.info(f"PDF has {total_pages} pages.")
                
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text:
                        extracted_text.append(text)
                    
                    if progress_callback:
                        progress_callback(i + 1, total_pages)
                        
                    logger.debug(f"Extracted page {i+1}/{total_pages}")
            
            combined_text = "\n---PAGE_BREAK---\n".join(extracted_text)
            logger.info("Successfully extracted text from all pages.")
            return combined_text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}", exc_info=True)
            raise e

"""
Input Validation Module
Validates files before processing to fail fast with clear messages
"""
import io
from typing import Tuple, Optional
from fastapi import UploadFile, HTTPException
import pypdf

# Try to import magic, but handle gracefully if not available
try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False

from error_handling import ErrorCatalog, create_error_response


# Configuration
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MIN_TEXT_LENGTH = 100  # Minimum 100 characters
MAX_TEXT_LENGTH = 100000  # 100K characters before truncation warning
SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.txt'}
SUPPORTED_MIME_TYPES = {
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'text/plain',
    'application/msword'
}


class ValidationResult:
    """Result of file validation"""
    def __init__(self, valid: bool, error: Optional[dict] = None, warnings: Optional[list] = None):
        self.valid = valid
        self.error = error
        self.warnings = warnings or []


async def validate_upload(file: UploadFile) -> ValidationResult:
    """
    Comprehensive validation of uploaded file
    Returns ValidationResult with detailed error/warning information
    """
    
    # Read file content
    content = await file.read()
    await file.seek(0)  # Reset for later reading
    
    # 1. Check file is not empty
    if len(content) == 0:
        return ValidationResult(
            valid=False,
            error=create_error_response(ErrorCatalog.FILE_EMPTY)
        )
    
    # 2. Check file size
    if len(content) > MAX_FILE_SIZE:
        size_mb = len(content) / (1024 * 1024)
        error = create_error_response(
            ErrorCatalog.FILE_TOO_LARGE,
            technical_detail=f"File size: {size_mb:.1f}MB (limit: 10MB)"
        )
        return ValidationResult(valid=False, error=error)
    
    # 3. Check file extension
    filename = file.filename.lower()
    file_ext = None
    for ext in SUPPORTED_EXTENSIONS:
        if filename.endswith(ext):
            file_ext = ext
            break
    
    if not file_ext:
        return ValidationResult(
            valid=False,
            error=create_error_response(
                ErrorCatalog.UNSUPPORTED_FILE_TYPE,
                technical_detail=f"File: {file.filename}"
            )
        )
    
    # 4. Validate file content matches extension
    try:
        mime = magic.from_buffer(content[:2048], mime=True)
        if mime not in SUPPORTED_MIME_TYPES:
            # File extension doesn't match content
            return ValidationResult(
                valid=False,
                error=create_error_response(
                    ErrorCatalog.UNSUPPORTED_FILE_TYPE,
                    technical_detail=f"File claims to be {file_ext} but contains {mime}"
                )
            )
    except:
        # magic library not available, skip MIME check
        pass
    
    # 5. PDF-specific validation
    if file_ext == '.pdf':
        pdf_validation = validate_pdf(content)
        if not pdf_validation.valid:
            return pdf_validation
    
    # All validations passed
    return ValidationResult(valid=True)


def validate_pdf(content: bytes) -> ValidationResult:
    """
    PDF-specific validation
    """
    try:
        pdf_reader = pypdf.PdfReader(io.BytesIO(content))
        
        # Check if password protected
        if pdf_reader.is_encrypted:
            return ValidationResult(
                valid=False,
                error=create_error_response(ErrorCatalog.PASSWORD_PROTECTED)
            )
        
        # Check if PDF has pages
        if len(pdf_reader.pages) == 0:
            return ValidationResult(
                valid=False,
                error=create_error_response(
                    ErrorCatalog.TEXT_TOO_SHORT,
                    technical_detail="PDF has 0 pages"
                )
            )
        
        return ValidationResult(valid=True)
        
    except Exception as e:
        # PDF is corrupted or unreadable
        return ValidationResult(
            valid=False,
            error=create_error_response(
                ErrorCatalog.TEXT_EXTRACTION_FAILED,
                technical_detail=f"PDF validation failed: {str(e)}"
            )
        )


def validate_extracted_text(text: str, filename: str) -> ValidationResult:
    """
    Validate extracted text content
    """
    warnings = []
    
    # Check minimum length
    if len(text) < MIN_TEXT_LENGTH:
        return ValidationResult(
            valid=False,
            error=create_error_response(
                ErrorCatalog.TEXT_TOO_SHORT,
                technical_detail=f"Extracted {len(text)} chars from {filename}"
            )
        )
    
    # Check for truncation warning
    if len(text) > MAX_TEXT_LENGTH:
        warnings.append(create_error_response(
            ErrorCatalog.DOCUMENT_TRUNCATED,
            technical_detail=f"Document has {len(text)} chars, will use first {MAX_TEXT_LENGTH}"
        ))
    
    # Check if text seems like gibberish (high ratio of special chars)
    special_char_ratio = sum(1 for c in text if not c.isalnum() and not c.isspace()) / len(text)
    if special_char_ratio > 0.5:
        return ValidationResult(
            valid=False,
            error=create_error_response(
                ErrorCatalog.TEXT_EXTRACTION_FAILED,
                technical_detail=f"Text appears corrupted (50%+ special characters)"
            )
        )
    
    return ValidationResult(valid=True, warnings=warnings)


def create_validation_response(result: ValidationResult) -> HTTPException:
    """
    Convert ValidationResult to HTTPException with proper status code
    """
    if not result.valid:
        error = result.error
        
        # Map error categories to HTTP status codes
        status_code_map = {
            "input_validation": 400,  # Bad Request
            "processing": 422,  # Unprocessable Entity
            "system": 500,  # Internal Server Error
            "rate_limit": 429  # Too Many Requests
        }
        
        status_code = status_code_map.get(error["category"], 500)
        
        return HTTPException(
            status_code=status_code,
            detail=error
        )
    
    return None  # Valid, no exception

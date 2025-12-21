"""
Error Handling System for SuperHumanly
Provides clear, actionable error messages for users
"""
from enum import Enum
from typing import Optional, List, Dict
from pydantic import BaseModel


class ErrorCategory(str, Enum):
    """Error categories for classification"""
    INPUT_VALIDATION = "input_validation"  # User can fix
    PROCESSING = "processing"  # Temporary, user can retry
    SYSTEM = "system"  # We need to fix
    RATE_LIMIT = "rate_limit"  # User needs to wait


class ErrorSeverity(str, Enum):
    """How urgent/serious is this error"""
    INFO = "info"  # Just FYI
    WARNING = "warning"  # Might cause issues
    ERROR = "error"  # Something failed
    CRITICAL = "critical"  # System-level failure


class UserFacingError(BaseModel):
    """
    A user-friendly error with actionable information
    """
    code: str  # e.g., "FILE_TOO_LARGE"
    title: str  # e.g., "File Size Exceeds Limit"
    message: str  # Clear explanation
    category: ErrorCategory
    severity: ErrorSeverity
    actions: List[str]  # What user can do
    technical_detail: Optional[str] = None  # For debugging
    retry_available: bool = False
    support_contact: bool = False


# Define all our error types
class ErrorCatalog:
    """Catalog of all possible errors with user-friendly messages"""
    
    # ==================== INPUT VALIDATION ERRORS ====================
    
    FILE_EMPTY = UserFacingError(
        code="FILE_EMPTY",
        title="Empty File",
        message="The uploaded file appears to be empty (0 bytes).",
        category=ErrorCategory.INPUT_VALIDATION,
        severity=ErrorSeverity.ERROR,
        actions=[
            "Check that you selected the correct file",
            "Try opening the file on your computer to verify it has content",
            "Try uploading a different file"
        ],
        retry_available=False
    )
    
    FILE_TOO_LARGE = UserFacingError(
        code="FILE_TOO_LARGE",
        title="File Size Exceeds Limit",
        message="Your file is larger than our 10MB limit.",
        category=ErrorCategory.INPUT_VALIDATION,
        severity=ErrorSeverity.ERROR,
        actions=[
            "Try splitting your document into smaller sections",
            "Compress your PDF using online tools",
            "Remove unnecessary images from the document",
            "Contact support for enterprise options with larger file limits"
        ],
        retry_available=False,
        support_contact=True
    )
    
    UNSUPPORTED_FILE_TYPE = UserFacingError(
        code="UNSUPPORTED_FILE_TYPE",
        title="Unsupported File Format",
        message="We currently support PDF, DOCX, and TXT files only.",
        category=ErrorCategory.INPUT_VALIDATION,
        severity=ErrorSeverity.ERROR,
        actions=[
            "Convert your file to PDF format",
            "Save as DOCX if using Word",
            "Export as PDF from your application"
        ],
        retry_available=False
    )
    
    PASSWORD_PROTECTED = UserFacingError(
        code="PASSWORD_PROTECTED",
        title="Password-Protected Document",
        message="Your PDF is password-protected and cannot be processed.",
        category=ErrorCategory.INPUT_VALIDATION,
        severity=ErrorSeverity.ERROR,
        actions=[
            "Remove password protection from your PDF",
            "In Adobe: File → Properties → Security → No Security",
            "Save an unprotected copy and upload that"
        ],
        retry_available=False
    )
    
    # ==================== TEXT EXTRACTION ERRORS ====================
    
    TEXT_EXTRACTION_FAILED = UserFacingError(
        code="TEXT_EXTRACTION_FAILED",
        title="Unable to Extract Text",
        message="We couldn't extract readable text from your document.",
        category=ErrorCategory.PROCESSING,
        severity=ErrorSeverity.ERROR,
        actions=[
            "Ensure your PDF contains actual text (not just images)",
            "Try converting scanned documents to searchable PDFs",
            "Save your document in a different format (try DOCX)",
            "Contact support for manual processing"
        ],
        retry_available=True,
        support_contact=True
    )
    
    TEXT_TOO_SHORT = UserFacingError(
        code="TEXT_TOO_SHORT",
        title="Insufficient Content",
        message="We extracted less than 100 characters from your document. It may be empty or unreadable.",
        category=ErrorCategory.PROCESSING,
        severity=ErrorSeverity.ERROR,
        actions=[
            "Check that your document contains text content",
            "Verify the file opens correctly on your computer",
            "Try a different document",
            "If document has images only, try converting to text first"
        ],
        retry_available=False
    )
    
    DOCUMENT_TRUNCATED = UserFacingError(
        code="DOCUMENT_TRUNCATED",
        title="Document Exceeds Processing Limit",
        message="Your document is very long. We can only process the first ~40 pages (100,000 characters).",
        category=ErrorCategory.PROCESSING,
        severity=ErrorSeverity.WARNING,
        actions=[
            "Click 'Continue' to process the first 40 pages",
            "Or split your document into smaller sections",
            "Contact support for enterprise options with larger limits"
        ],
        retry_available=False,
        support_contact=True
    )
    
    OCR_FAILED = UserFacingError(
        code="OCR_FAILED",
        title="Scanned Document Processing Failed",
        message="Your PDF appears to be scanned or image-based, and our OCR (text recognition) failed.",
        category=ErrorCategory.PROCESSING,
        severity=ErrorSeverity.ERROR,
        actions=[
            "Use a text-based PDF instead of a scanned copy",
            "Try using Adobe Acrobat to OCR the document first",
            "Convert to text using Google Drive (Upload → Open with Google Docs)",
            "Contact support for manual processing"
        ],
        retry_available=True,
        support_contact=True
    )
    
    # ==================== AI PROCESSING ERRORS ====================
    
    AI_TIMEOUT = UserFacingError(
        code="AI_TIMEOUT",
        title="Processing Timeout",
        message="Your document is taking longer than expected to process (>60 seconds).",
        category=ErrorCategory.PROCESSING,
        severity=ErrorSeverity.WARNING,
        actions=[
            "Try again - it may work on second attempt",
            "Try a shorter or simpler document",
            "Try during off-peak hours (fewer users)",
            "Contact support if issue persists"
        ],
        retry_available=True,
        support_contact=True
    )
    
    AI_INVALID_RESPONSE = UserFacingError(
        code="AI_INVALID_RESPONSE",
        title="Processing Error",
        message="We couldn't generate a valid flowchart from your document. The AI returned an invalid response.",
        category=ErrorCategory.PROCESSING,
        severity=ErrorSeverity.ERROR,
        actions=[
            "Try again - occasional AI errors can happen",
            "Ensure your document is a structured process/SOP",
            "Try simplifying the document",
            "Contact support if issue persists"
        ],
        retry_available=True,
        support_contact=True
    )
    
    RATE_LIMIT_EXCEEDED = UserFacingError(
        code="RATE_LIMIT_EXCEEDED",
        title="Too Many Requests",
        message="You've processed too many documents recently. Please wait a moment.",
        category=ErrorCategory.RATE_LIMIT,
        severity=ErrorSeverity.WARNING,
        actions=[
            "Wait 1-2 minutes and try again",
            "Upgrade to Pro for higher limits",
            "Contact support for enterprise options"
        ],
        retry_available=True
    )
    
    # ==================== SYSTEM ERRORS ====================
    
    DATABASE_ERROR = UserFacingError(
        code="DATABASE_ERROR",
        title="System Error",
        message="We're experiencing database issues. Our team has been notified.",
        category=ErrorCategory.SYSTEM,
        severity=ErrorSeverity.CRITICAL,
        actions=[
            "Please try again in 5-10 minutes",
            "Check our status page for updates",
            "Contact support if issue persists beyond 1 hour"
        ],
        retry_available=True,
        support_contact=True
    )
    
    API_KEY_MISSING = UserFacingError(
        code="API_KEY_MISSING",
        title="System Configuration Error",
        message="AI service is temporarily unavailable due to configuration issues.",
        category=ErrorCategory.SYSTEM,
        severity=ErrorSeverity.CRITICAL,
        actions=[
            "Please try again in a few minutes",
            "Contact support immediately if urgent"
        ],
        retry_available=True,
        support_contact=True
    )
    
    UNKNOWN_ERROR = UserFacingError(
        code="UNKNOWN_ERROR",
        title="Unexpected Error",
        message="Something unexpected went wrong. We've logged this error and will investigate.",
        category=ErrorCategory.SYSTEM,
        severity=ErrorSeverity.ERROR,
        actions=[
            "Try again in a few minutes",
            "Contact support with error details if issue persists"
        ],
        retry_available=True,
        support_contact=True
    )


def create_error_response(error: UserFacingError, technical_detail: Optional[str] = None) -> Dict:
    """
    Create a standardized error response for API
    """
    response = error.dict()
    if technical_detail:
        response["technical_detail"] = technical_detail
    return response


def get_support_info() -> Dict:
    """Get support contact information"""
    return {
        "email": "support@superhumanly.ai",
        "docs": "https://docs.superhumanly.ai",
        "status": "https://status.superhumanly.ai"
    }

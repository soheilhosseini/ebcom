"""
Base exception classes for the application.

All feature-specific exceptions should inherit from these base classes.
"""


class AppError(Exception):
    """
    Base exception for all application errors.
    
    Contains a user-friendly message that is safe to display.
    Never contains technical details or sensitive information.
    """
    
    def __init__(self, message: str, code: str = "APP_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)
    
    def to_dict(self) -> dict:
        """Convert exception to dictionary for API responses."""
        return {
            "error": True,
            "code": self.code,
            "message": self.message
        }


class ValidationError(AppError):
    """Raised when input validation fails."""
    
    def __init__(self, message: str):
        super().__init__(message, code="VALIDATION_ERROR")


class ServiceError(AppError):
    """Raised when an external service fails."""
    
    def __init__(self, message: str, service_name: str = "unknown"):
        self.service_name = service_name
        super().__init__(message, code="SERVICE_ERROR")

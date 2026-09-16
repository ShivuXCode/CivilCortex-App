class CivilCortexError(Exception):
    """Base exception for all domain errors."""
    def __init__(self, message: str, code: str):
        super().__init__(message)
        self.code = code
        self.message = message

class ValidationError(CivilCortexError):
    def __init__(self, message: str):
        super().__init__(message, "VALIDATION_ERROR")

class AuthenticationError(CivilCortexError):
    def __init__(self, message: str):
        super().__init__(message, "AUTHENTICATION_ERROR")

class AuthorizationError(CivilCortexError):
    def __init__(self, message: str):
        super().__init__(message, "AUTHORIZATION_ERROR")

class NotFoundError(CivilCortexError):
    def __init__(self, message: str):
        super().__init__(message, "NOT_FOUND")

class StorageError(CivilCortexError):
    def __init__(self, message: str):
        super().__init__(message, "STORAGE_ERROR")

class ImageProcessingError(CivilCortexError):
    def __init__(self, message: str):
        super().__init__(message, "IMAGE_PROCESSING_ERROR")

class CVInferenceError(CivilCortexError):
    def __init__(self, message: str):
        super().__init__(message, "CV_INFERENCE_ERROR")

class RAGError(CivilCortexError):
    def __init__(self, message: str):
        super().__init__(message, "RAG_ERROR")

class LLMError(CivilCortexError):
    def __init__(self, message: str):
        super().__init__(message, "LLM_ERROR")

class DatabaseError(CivilCortexError):
    def __init__(self, message: str):
        super().__init__(message, "DATABASE_ERROR")

class QueueError(CivilCortexError):
    def __init__(self, message: str):
        super().__init__(message, "QUEUE_ERROR")

class InternalError(CivilCortexError):
    def __init__(self, message: str = "Internal server error"):
        super().__init__(message, "INTERNAL_ERROR")

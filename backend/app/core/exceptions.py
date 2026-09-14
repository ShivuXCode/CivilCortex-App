from fastapi import HTTPException, status

class BaseAPIException(HTTPException):
    def __init__(self, status_code: int, detail: str, error_code: str = "UNKNOWN_ERROR"):
        super().__init__(status_code=status_code, detail={"message": detail, "code": error_code})

class ResourceNotFoundException(BaseAPIException):
    def __init__(self, resource: str, resource_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} with id {resource_id} not found.",
            error_code="RESOURCE_NOT_FOUND"
        )

class StateTransitionException(BaseAPIException):
    def __init__(self, resource: str, current_state: str, target_state: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Invalid state transition for {resource} from {current_state} to {target_state}.",
            error_code="INVALID_STATE_TRANSITION"
        )

class ValidationException(BaseAPIException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code="VALIDATION_ERROR"
        )

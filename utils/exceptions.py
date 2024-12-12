from typing import Optional, Dict, Any
from pydantic import BaseModel
from fastapi import HTTPException

class ErrorResponse(BaseModel):
    status_code: int
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None
class FinancialPlannerException(HTTPException):
    def __init__(
        self,
        status_code: int,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict] = None
    ):
        super().__init__(status_code=status_code, detail=message)
        self.status_code = status_code
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details
class ValidationError(FinancialPlannerException):
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(
            status_code=400,
            message=message,
            error_code="VALIDATION_ERROR",
            details=details
        )



"""Custom application exceptions."""


class AppException(Exception):
    def __init__(self, message: str, code: str, status_code: int = 500) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code


class NotFoundError(AppException):
    def __init__(self, resource: str = "Resource") -> None:
        super().__init__(f"{resource} not found", "NOT_FOUND", 404)


class ConflictError(AppException):
    def __init__(self, message: str = "Resource conflict") -> None:
        super().__init__(message, "CONFLICT", 409)


class InsufficientStockError(AppException):
    def __init__(self, message: str = "Insufficient stock") -> None:
        super().__init__(message, "INSUFFICIENT_STOCK", 409)


class ValidationFailedError(AppException):
    def __init__(self, message: str = "Validation failed") -> None:
        super().__init__(message, "VALIDATION_ERROR", 422)


class UnauthorizedError(AppException):
    def __init__(self, message: str = "Not authenticated") -> None:
        super().__init__(message, "UNAUTHORIZED", 401)


class ForbiddenError(AppException):
    def __init__(self, message: str = "Not enough permissions") -> None:
        super().__init__(message, "FORBIDDEN", 403)


class FileUploadError(AppException):
    def __init__(self, message: str = "Invalid file upload") -> None:
        super().__init__(message, "FILE_UPLOAD_ERROR", 400)

from __future__ import annotations


class AppError(Exception):
    status_code = 500
    error_type = "app_error"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class ConfigurationError(AppError):
    status_code = 500
    error_type = "configuration_error"


class ExternalServiceError(AppError):
    status_code = 502
    error_type = "external_service_error"


class InputValidationError(AppError):
    status_code = 400
    error_type = "input_validation_error"

import re


class AIServiceError(Exception):
    def __init__(self, message: str, status_code: int = 502) -> None:
        super().__init__(message)
        self.status_code = status_code


def sanitize_provider_error(message: str) -> str:
    # Redact query-string API keys like ?key=AIza... to avoid leaking secrets in API responses.
    return re.sub(r"([?&]key=)[^\s'\"]+", r"\1***", message)

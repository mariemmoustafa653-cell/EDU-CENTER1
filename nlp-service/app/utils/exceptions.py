class SummarizationError(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ProviderError(SummarizationError):
    def __init__(self, provider: str, message: str):
        super().__init__(
            message=f"Provider '{provider}' error: {message}",
            status_code=502,
        )
        self.provider = provider


class ValidationError(SummarizationError):
    def __init__(self, message: str):
        super().__init__(message=message, status_code=400)


class TextTooLongError(SummarizationError):
    def __init__(self, length: int, max_length: int):
        super().__init__(
            message=f"Text length ({length}) exceeds maximum ({max_length})",
            status_code=413,
        )

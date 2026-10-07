class BaseTTSException(Exception):
    pass


class TTSException(BaseTTSException):
    pass


class TTSInvalidRequest(TTSException):
    """The backend cannot synthesize this input (including no phoneme)."""


class TTSBackendUnavailable(TTSException):
    """A temporary backend or network failure."""


class TTSBackendError(TTSException):
    """An unexpected backend response."""

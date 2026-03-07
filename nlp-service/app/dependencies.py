from app.application.interfaces import SummarizationProvider
from app.application.use_cases import SummarizeTextUseCase
from app.infrastructure.providers.factory import create_provider

_provider: SummarizationProvider | None = None
_use_case: SummarizeTextUseCase | None = None


async def initialize_dependencies():
    global _provider, _use_case
    _provider = create_provider()

    if hasattr(_provider, "load_model"):
        await _provider.load_model()

    _use_case = SummarizeTextUseCase(provider=_provider)


def get_use_case() -> SummarizeTextUseCase:
    if not _use_case:
        raise RuntimeError("Dependencies not initialized")
    return _use_case


def get_provider() -> SummarizationProvider:
    if not _provider:
        raise RuntimeError("Dependencies not initialized")
    return _provider

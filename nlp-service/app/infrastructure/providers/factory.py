from app.application.interfaces import SummarizationProvider
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


def create_provider() -> SummarizationProvider:
    provider_name = settings.summarization_provider.lower()

    if provider_name == "huggingface":
        from app.infrastructure.providers.huggingface_provider import HuggingFaceProvider
        logger.info("Using HuggingFace provider")
        return HuggingFaceProvider(model_name=settings.huggingface_model)

    if provider_name == "openai":
        from app.infrastructure.providers.openai_provider import OpenAIProvider
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required for OpenAI provider")
        logger.info("Using OpenAI provider")
        return OpenAIProvider(api_key=settings.openai_api_key)

    raise ValueError(f"Unknown provider: {provider_name}")

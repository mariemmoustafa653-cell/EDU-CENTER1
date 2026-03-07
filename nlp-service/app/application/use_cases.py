from app.application.interfaces import SummarizationProvider
from app.domain.entities import SummarizationResponse
from app.utils.logger import get_logger

logger = get_logger(__name__)


class SummarizeTextUseCase:
    def __init__(self, provider: SummarizationProvider):
        self._provider = provider

    async def execute(self, text: str, request_id: str | None = None) -> SummarizationResponse:
        original_length = len(text)

        logger.info(
            "Starting summarization",
            extra={"request_id": request_id or "unknown"},
        )

        summary_text = await self._provider.summarize(text)
        summary_length = len(summary_text)
        compression_ratio = round(1 - (summary_length / original_length), 4) if original_length > 0 else 0.0

        logger.info(
            "Summarization complete",
            extra={"request_id": request_id or "unknown"},
        )

        return SummarizationResponse(
            original_length=original_length,
            summary_length=summary_length,
            compression_ratio=compression_ratio,
            summary_text=summary_text,
        )

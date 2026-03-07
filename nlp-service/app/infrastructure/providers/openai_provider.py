import asyncio
from openai import AsyncOpenAI
from app.application.interfaces import SummarizationProvider
from app.utils.exceptions import ProviderError
from app.utils.logger import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = (
    "You are a professional text summarizer. "
    "Produce a concise, coherent summary that captures all key points. "
    "Do not add any information not present in the original text."
)


class OpenAIProvider(SummarizationProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self._client = AsyncOpenAI(api_key=api_key)
        self._model = model

    async def summarize(self, text: str) -> str:
        max_retries = 3
        for attempt in range(1, max_retries + 1):
            try:
                response = await asyncio.wait_for(
                    self._client.chat.completions.create(
                        model=self._model,
                        messages=[
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": f"Summarize:\n\n{text}"},
                        ],
                        temperature=0.3,
                        max_tokens=1024,
                    ),
                    timeout=25.0,
                )
                return response.choices[0].message.content.strip()

            except asyncio.TimeoutError:
                logger.warning(f"OpenAI timeout, attempt {attempt}/{max_retries}")
                if attempt == max_retries:
                    raise ProviderError("openai", "Request timed out after retries")

            except Exception as e:
                logger.warning(f"OpenAI error attempt {attempt}/{max_retries}: {e}")
                if attempt == max_retries:
                    raise ProviderError("openai", str(e))

                await asyncio.sleep(1 * attempt)

    async def health_check(self) -> dict:
        return {
            "provider": "openai",
            "model": self._model,
            "status": "ready",
        }

import asyncio
import time
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from app.application.interfaces import SummarizationProvider
from app.infrastructure.text_processor import chunk_text
from app.utils.exceptions import ProviderError
from app.utils.logger import get_logger

logger = get_logger(__name__)


class HuggingFaceProvider(SummarizationProvider):
    def __init__(self, model_name: str = "facebook/bart-large-cnn"):
        self._model_name = model_name
        self._model = None
        self._tokenizer = None

    async def load_model(self):
        logger.info(f"Loading HuggingFace model: {self._model_name}")
        start = time.time()

        loop = asyncio.get_event_loop()
        self._tokenizer, self._model = await loop.run_in_executor(
            None,
            self._load,
        )

        duration = round(time.time() - start, 2)
        logger.info(f"Model loaded in {duration}s")

    def _load(self):
        tokenizer = AutoTokenizer.from_pretrained(self._model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(self._model_name)
        model.eval()
        return tokenizer, model

    async def summarize(self, text: str) -> str:
        if not self._model or not self._tokenizer:
            raise ProviderError("huggingface", "Model not loaded")

        try:
            chunks = chunk_text(text)
            loop = asyncio.get_event_loop()

            summaries = []
            for chunk in chunks:
                summary = await loop.run_in_executor(
                    None,
                    self._summarize_chunk,
                    chunk,
                )
                summaries.append(summary)

            return " ".join(summaries)

        except ProviderError:
            raise
        except Exception as e:
            raise ProviderError("huggingface", str(e))

    def _summarize_chunk(self, text: str) -> str:
        inputs = self._tokenizer(
            text,
            return_tensors="pt",
            max_length=1024,
            truncation=True,
        )
        summary_ids = self._model.generate(
            inputs["input_ids"],
            max_length=150,
            min_length=40,
            num_beams=4,
            length_penalty=2.0,
            early_stopping=True,
        )
        return self._tokenizer.decode(summary_ids[0], skip_special_tokens=True)

    async def health_check(self) -> dict:
        return {
            "provider": "huggingface",
            "model": self._model_name,
            "status": "ready" if self._model else "not_loaded",
        }

from fastapi import APIRouter
from app.domain.entities import SummarizationRequest, SummarizationResponse
from app.dependencies import get_use_case
from app.config import settings
from app.utils.exceptions import TextTooLongError

router = APIRouter(prefix="/api/v1", tags=["summarization"])


@router.post("/summarize", response_model=SummarizationResponse)
async def summarize(request: SummarizationRequest):
    if len(request.text) > settings.max_input_length:
        raise TextTooLongError(
            length=len(request.text),
            max_length=settings.max_input_length,
        )

    use_case = get_use_case()
    return await use_case.execute(
        text=request.text,
        request_id=request.request_id,
    )

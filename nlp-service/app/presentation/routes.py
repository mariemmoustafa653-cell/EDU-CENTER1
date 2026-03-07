from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from app.domain.entities import SummarizationResponse
from app.dependencies import get_use_case
from app.config import settings
from app.utils.exceptions import TextTooLongError
from app.utils.document_extractor import extract_text_from_file

router = APIRouter(prefix="/api/v1", tags=["summarization"])


@router.post("/summarize", response_model=SummarizationResponse)
async def summarize(
    file: UploadFile = File(..., description="Document file to summarize"),
    request_id: str | None = Form(None, description="Request tracing ID")
):
    content = await file.read()
    
    try:
        text = await extract_text_from_file(content, file.filename)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    
    if len(text) > settings.max_input_length:
        raise TextTooLongError(
            length=len(text),
            max_length=settings.max_input_length,
        )

    use_case = get_use_case()
    return await use_case.execute(
        text=text,
        request_id=request_id,
    )

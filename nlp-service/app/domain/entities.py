from pydantic import BaseModel, Field


class SummarizationRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Text to summarize")
    request_id: str | None = Field(None, description="Request tracing ID")


class SummarizationResponse(BaseModel):
    status: str = "success"
    original_length: int
    summary_length: int
    compression_ratio: float
    summary_text: str

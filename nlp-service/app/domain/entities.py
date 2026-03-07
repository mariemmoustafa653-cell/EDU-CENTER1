from pydantic import BaseModel

class SummarizationResponse(BaseModel):
    status: str = "success"
    original_length: int
    summary_length: int
    compression_ratio: float
    summary_text: str

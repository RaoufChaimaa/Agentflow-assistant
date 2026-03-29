from pydantic import BaseModel
from typing import Literal


class AnalyzeRequest(BaseModel):
    page_text: str
    mode: Literal["summary", "qa", "tasks"]
    question: str = ""


class AnalyzeResponse(BaseModel):
    result: str
    mode: str
    latency_ms: int
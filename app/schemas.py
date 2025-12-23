# app/schema.py

from pydantic import BaseModel
from typing import Optional, List

class AnalyzeRequest(BaseModel):
    sql: str
    explain_text: Optional[str] = None
    add_ai_explanations: bool = False

class Issue(BaseModel):
    type: str
    severity: str
    message: str
    suggestion: str
    confidence: int
    ai_explanation: Optional[str] = None


class AnalyzeResponse(BaseModel):
    score: Optional[int] = None
    issues: List[Issue]
    rewritten_sql: str


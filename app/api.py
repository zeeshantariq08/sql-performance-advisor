from fastapi import FastAPI
from pydantic import BaseModel
from sqlglot import parse_one
from analyzer.advisor import analyze_with_explain

app = FastAPI(title="SQL Query Optimizer")

class AnalyzeRequest(BaseModel):
    sql: str
    explain_text: str | None = None
    add_ai_explanations: bool = False

@app.post("/analyze")
def analyze_sql(req: AnalyzeRequest):
    try:
        expression = parse_one(req.sql)
    except Exception as e:
        return {"error": f"Invalid SQL: {e}"}

    result = analyze_with_explain(
        expression,
        explain_text=req.explain_text,
        add_ai_explanations=req.add_ai_explanations
    )

    return {
        "score": result["score"],
        "issues": result["issues"],
        "rewritten_sql": result["rewritten_sql"],
    }

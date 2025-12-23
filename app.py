from fastapi import FastAPI
from pydantic import BaseModel
from sqlglot import parse_one
from analyzer.advisor import analyze
from dotenv import load_dotenv

load_dotenv()  # Load GEMINI_API_KEY from .env

app = FastAPI(title="SQL Query Optimizer with Gemini AI")

class QueryRequest(BaseModel):
    query: str
    ai: bool = True  # Enable AI explanations by default

@app.post("/analyze")
def analyze_query(req: QueryRequest):
    try:
        expression = parse_one(req.query)
    except Exception as e:
        return {"error": f"Invalid SQL: {e}"}

    issues, rewritten_sql = analyze(expression, add_ai_explanations=req.ai)
    return {
        "issues": issues,
        "rewritten_sql": rewritten_sql
    }

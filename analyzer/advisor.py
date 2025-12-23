import os
import re
from dotenv import load_dotenv
from sqlglot import expressions as exp
from analyzer.confidence import calculate_confidence
from analyzer.score import calculate_overall_score



from analyzer.explain_analyzer import analyze_explain_analyze
from analyzer.rules import (
    detect_select_star,
    detect_missing_where,
    detect_joins,
    suggest_indexes,
    detect_non_sargable_patterns,
    get_from_table,
    generate_optimized_condition,
    rewrite_query
)

load_dotenv()

# ---------------- Gemini AI setup (OPTIONAL) ----------------
try:
    from google import genai
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None
except Exception:
    client = None


# ---------------- AI explanation helper (SAFE &_toggleable) ----------------
def generate_ai_explanation(issue_text: str, enabled: bool = False) -> str | None:
    """
    Optional AI explanation (1 sentence max).
    Completely skipped if disabled or client missing.
    """
    if not enabled or not client:
        return None

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=(
                "Explain this SQL performance issue in one short sentence:\n"
                + issue_text
            ),
        )
        return response.text.strip()
    except Exception:
        return None


# ---------------- Main SQL analyzer ----------------
def analyze(expression, add_ai_explanations=False):
    issues = []
    main_table = get_from_table(expression)

    # 1️⃣ SELECT *
    if detect_select_star(expression):
        msg = "Query uses SELECT *"
        issues.append({
            "type": "OVER_FETCHING",
            "severity": "MEDIUM",
            "message": msg,
            "suggestion": "Select only required columns instead of SELECT *",
            "confidence": calculate_confidence("OVER_FETCHING", "MEDIUM"),
            "ai_explanation": generate_ai_explanation(msg, add_ai_explanations)
        })

    # 2️⃣ Missing WHERE
    if detect_missing_where(expression):
        msg = "Query has no WHERE clause"
        issues.append({
            "type": "FULL_TABLE_SCAN",
            "severity": "HIGH",
            "message": msg,
            "suggestion": "Add filtering conditions to reduce scanned rows",
            "confidence": calculate_confidence("FULL_TABLE_SCAN", "HIGH"),
            "ai_explanation": generate_ai_explanation(msg, add_ai_explanations)
        })


    # 3️⃣ JOIN risk
    join_count = detect_joins(expression)
    if join_count > 0:
        msg = f"Query contains {join_count} JOIN(s)"
        issues.append({
            "type": "JOIN_EXPLOSION_RISK",
            "severity": "MEDIUM",
            "message": msg,
            "suggestion": "Ensure joins use indexed columns and correct cardinality",
            "confidence": calculate_confidence("JOIN_EXPLOSION_RISK", "MEDIUM"),
            "ai_explanation": generate_ai_explanation(msg, add_ai_explanations)
        })


    # 4️⃣ Index suggestions
    index_candidates = suggest_indexes(expression, default_table=main_table)
    for idx in index_candidates:
        table = idx.get("table", "unknown_table")
        col = idx.get("column", "unknown_column")

        msg = f"Consider adding an index on {table}.{col}"
        issues.append({
            "type": "INDEX_SUGGESTION",
            "severity": "LOW",
            "message": msg,
            "suggestion": f"CREATE INDEX idx_{table}_{col} ON {table}({col});",
            "confidence": calculate_confidence("INDEX_SUGGESTION", "LOW"),
            "ai_explanation": generate_ai_explanation(msg, add_ai_explanations)
        })


    # 5️⃣ Non-SARGable conditions
    non_sargable = detect_non_sargable_patterns(expression, default_table=main_table)
    for item in non_sargable:
        table = item.get("table")
        col = item.get("column")
        pattern = item.get("pattern")

        optimized_sql = generate_optimized_condition(item)
        msg = f"Non-SARGable condition on {table}.{col}"

        issues.append({
            "type": "NON_SARGABLE_CONDITION",
            "severity": "MEDIUM",
            "message": msg,
            "suggestion": optimized_sql or "Rewrite condition to be index-friendly",
            "confidence": calculate_confidence("NON_SARGABLE_CONDITION", "MEDIUM"),
            "ai_explanation": generate_ai_explanation(msg, add_ai_explanations)
        })



    rewritten_sql = rewrite_query(expression, non_sargable)

    return issues, rewritten_sql


# ---------------- SQL + EXPLAIN Analyzer ----------------
def analyze_with_explain(expression, explain_text=None, add_ai_explanations=False):
    issues, rewritten_sql = analyze(expression, add_ai_explanations)

    score = None
    if explain_text:
        score, explain_issues = analyze_explain_analyze(explain_text)
        issues.extend(explain_issues)

    overall_score = calculate_overall_score(issues)

    return {
        "score": overall_score,
        "issues": issues,
        "rewritten_sql": rewritten_sql
    }

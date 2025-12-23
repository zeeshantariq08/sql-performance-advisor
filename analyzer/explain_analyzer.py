# analyzer/explain_analyzer.py
import re

def analyze_explain_analyze(explain_text: str):
    """
    Analyze PostgreSQL EXPLAIN ANALYZE output
    Returns: (score:int, findings:list)
    """
    score = 100
    findings = []

    if not explain_text:
        return score, findings

    text = explain_text.upper()

    # 1️⃣ Sequential Scan
    if "SEQ SCAN" in text:
        score -= 25
        findings.append({
            "type": "SEQ_SCAN",
            "severity": "HIGH",
            "message": "Sequential scan detected",
            "suggestion": "Add an index or improve WHERE clause selectivity",
            "ai_explanation": None
        })

    # 2️⃣ Execution time
    time_match = re.search(r"EXECUTION TIME:\s*([\d\.]+)\s*MS", text)
    if time_match:
        exec_time = float(time_match.group(1))
        if exec_time > 500:
            score -= 20
            findings.append({
                "type": "SLOW_QUERY",
                "severity": "HIGH",
                "message": f"Execution time is {exec_time} ms",
                "suggestion": "Optimize query or add proper indexes",
                "ai_explanation": None
            })

    # 3️⃣ Bad row estimates
    planned = re.findall(r"ROWS=(\d+)", text)
    actual = re.findall(r"ACTUAL ROWS=(\d+)", text)

    if planned and actual:
        try:
            if int(actual[-1]) > int(planned[-1]) * 5:
                score -= 20
                findings.append({
                    "type": "BAD_ESTIMATE",
                    "severity": "MEDIUM",
                    "message": "Actual rows far exceed planner estimate",
                    "suggestion": "Run ANALYZE or improve statistics",
                    "ai_explanation": None
                })
        except:
            pass

    # 4️⃣ Nested Loop
    if "NESTED LOOP" in text:
        score -= 15
        findings.append({
            "type": "NESTED_LOOP",
            "severity": "MEDIUM",
            "message": "Nested Loop detected",
            "suggestion": "Consider indexes or hash joins",
            "ai_explanation": None
        })

    return max(score, 0), findings

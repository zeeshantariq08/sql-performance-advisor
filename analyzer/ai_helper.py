import os
from openai import OpenAI

gemini_client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

def explain_issue_with_gemini(issue):
    """
    Generate a human-friendly explanation using Gemini
    """
    prompt = f"""
You are an SQL optimization assistant.
Explain why this SQL issue is important and how to fix it in simple terms.
Issue type: {issue.get('type')}
Severity: {issue.get('severity')}
Message: {issue.get('message')}
Suggestion: {issue.get('suggestion')}
"""
    try:
        response = gemini_client.chat.completions.create(
            model="gemini-2.5-flash",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"AI explanation error: {e}"

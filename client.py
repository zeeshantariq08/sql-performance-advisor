import os
import requests
from colorama import init, Fore
from dotenv import load_dotenv

load_dotenv()
API_URL = os.getenv("SQL_ANALYZER_API_URL", "http://127.0.0.1:8000/analyze")

def pretty_print_issue(issue):
    print(f"\n{Fore.YELLOW}⚠ {issue.get('type')}")
    print(f"{Fore.RED}Severity: {issue.get('severity')}")
    print(f"{Fore.CYAN}Why: {issue.get('message')}")
    print(f"{Fore.GREEN}Fix: {issue.get('suggestion')}")
    ai_expl = issue.get("ai_explanation")
    if ai_expl:
        print(f"{Fore.MAGENTA}AI Explanation: {ai_expl}")

def main():
    init(autoreset=True)
    print("Paste your SQL query (end with a blank line):")
    lines = []
    while True:
        line = input()
        if not line.strip():
            break
        lines.append(line)
    sql_query = "\n".join(lines)

    if not sql_query.strip():
        print(Fore.RED + "No SQL query provided!")
        return

    try:
        response = requests.post(API_URL, json={"query": sql_query, "ai": True}, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        print(Fore.RED + f"API request failed: {e}")
        return

    issues = data.get("issues", [])
    rewritten_sql = data.get("rewritten_sql", "")

    if not issues:
        print(Fore.GREEN + "No issues detected ✅")
        return

    print(f"\nDetected {len(issues)} issue(s):")
    for issue in issues:
        pretty_print_issue(issue)

    if rewritten_sql:
        print(f"\n{Fore.CYAN}--- Rewritten SQL ---")
        print(rewritten_sql)

if __name__ == "__main__":
    main()

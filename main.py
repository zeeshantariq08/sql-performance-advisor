from colorama import init, Fore
from sqlglot import parse_one
from analyzer.advisor import analyze_with_explain
from utils.diff import sql_diff

# 🔥 Force ANSI colors on Windows
init(autoreset=True, strip=False, convert=False)


def pretty_print_issue(issue):
    print("\n" + Fore.YELLOW + "⚠ " + issue.get("type", "UNKNOWN"))
    print(Fore.RED + f"Severity: {issue.get('severity', 'N/A')}")

    confidence = issue.get("confidence")
    if confidence is not None:
        print(Fore.CYAN + f"Confidence: {confidence}%")

    print(Fore.WHITE + f"Why: {issue.get('message', '')}")
    print(Fore.GREEN + f"Fix: {issue.get('suggestion', '')}")

    if issue.get("ai_explanation"):
        print(Fore.MAGENTA + "AI Explanation: " + issue["ai_explanation"])


def main():
    print(Fore.CYAN + "Paste your SQL query (end with a blank line):")

    sql_lines = []
    while True:
        line = input()
        if not line.strip():
            break
        sql_lines.append(line)

    sql_query = "\n".join(sql_lines)

    if not sql_query.strip():
        print(Fore.RED + "No SQL query provided!")
        return

    # Optional EXPLAIN ANALYZE
    explain_text = None
    if input("Paste EXPLAIN ANALYZE output? (y/N): ").strip().lower() == "y":
        print(Fore.CYAN + "Paste EXPLAIN ANALYZE output (end with blank line):")
        explain_lines = []
        while True:
            line = input()
            if not line.strip():
                break
            explain_lines.append(line)
        explain_text = "\n".join(explain_lines)

    use_ai = input("Include AI explanations? (y/N): ").strip().lower() == "y"

    try:
        expression = parse_one(sql_query)
    except Exception as e:
        print(Fore.RED + f"Invalid SQL: {e}")
        return

    result = analyze_with_explain(
        expression,
        explain_text=explain_text,
        add_ai_explanations=use_ai
    )

    # 🔥 OVERALL SCORE
    score = result.get("score")
    if score is not None:
        color = (
            Fore.GREEN if score >= 85
            else Fore.YELLOW if score >= 60
            else Fore.RED
        )
        print(color + f"\nOverall Query Score: {score}/100")

    issues = result.get("issues", [])
    print(Fore.CYAN + f"\nDetected {len(issues)} issue(s):")

    for issue in issues:
        pretty_print_issue(issue)

    optimized_sql = result.get("rewritten_sql")
    if optimized_sql and optimized_sql.strip() != sql_query.strip():
        print(Fore.CYAN + "\nQuery Diff (Original -> Optimized):")
        print(Fore.WHITE + sql_diff(sql_query, optimized_sql))

        print(Fore.GREEN + "\nSuggested Optimized SQL:")
        print(Fore.GREEN + optimized_sql)


if __name__ == "__main__":
    main()

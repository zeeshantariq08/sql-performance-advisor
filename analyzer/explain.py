def explain_issues(issues):
    for issue in issues:
        print(f"\n⚠ {issue['type']}")
        print(f"Why: {issue['message']}")
        print(f"Fix: {issue['suggestion']}")

def calculate_overall_score(issues: list[dict]) -> int:
    """
    Calculate overall query score (0–100)
    """
    score = 100

    severity_penalty = {
        "HIGH": 25,
        "MEDIUM": 15,
        "LOW": 5,
    }

    for issue in issues:
        severity = issue.get("severity", "LOW")
        confidence = issue.get("confidence", 60)

        base_penalty = severity_penalty.get(severity, 5)

        # Confidence-weighted penalty
        weighted_penalty = base_penalty * (confidence / 100)

        score -= weighted_penalty

    return max(int(score), 0)

def calculate_confidence(issue_type: str, severity: str) -> int:
    """
    Returns confidence score (0–100) for a recommendation
    """
    base = {
        "HIGH": 85,
        "MEDIUM": 70,
        "LOW": 55,
    }.get(severity, 60)

    boosts = {
        "FULL_TABLE_SCAN": 10,
        "NON_SARGABLE_CONDITION": 10,
        "SEQ_SCAN": 15,
        "SLOW_QUERY": 15,
        "BAD_ESTIMATE": 10,
        "JOIN_EXPLOSION_RISK": 5,
        "INDEX_SUGGESTION": 0,
        "OVER_FETCHING": 0,
    }

    return min(100, base + boosts.get(issue_type, 0))

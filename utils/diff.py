import difflib

def sql_diff(original_sql: str, optimized_sql: str) -> str:
    original = original_sql.splitlines()
    optimized = optimized_sql.splitlines()

    diff = difflib.unified_diff(
        original,
        optimized,
        fromfile="Original",
        tofile="Optimized",
        lineterm=""
    )

    return "\n".join(diff)

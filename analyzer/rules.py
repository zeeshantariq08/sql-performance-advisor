from sqlglot import exp
from datetime import datetime

def detect_select_star(expression):
    return expression and expression.sql().upper().startswith("SELECT *")

def detect_missing_where(expression):
    return "WHERE" not in expression.sql().upper()

def detect_joins(expression):
    if not expression:
        return 0
    joins = list(expression.find_all(exp.Join))
    return len(joins)

def suggest_indexes(expression, default_table=None):
    if not expression:
        return []
    index_candidates = []

    # WHERE columns
    for where in expression.find_all(exp.Where):
        for column in where.find_all(exp.Column):
            table = column.table or default_table or "unknown_table"
            col_name = column.name
            index_candidates.append({
                "table": table,
                "column": col_name,
                "reason": "Used in WHERE clause"
            })

    # JOIN columns
    for join in expression.find_all(exp.Join):
        on_expr = join.args.get("on")
        if on_expr:
            for column in on_expr.find_all(exp.Column):
                table = column.table or default_table or "unknown_table"
                col_name = column.name
                index_candidates.append({
                    "table": table,
                    "column": col_name,
                    "reason": "Used in JOIN condition"
                })

    return index_candidates

def detect_non_sargable_patterns(expression, default_table=None):
    """
    Detect common non-SARGable patterns like DATE(col), YEAR(col), UPPER(col)
    Returns list of dicts: {table, column, pattern, value}
    """
    if not expression:
        return []

    issues = []

    for where in expression.find_all(exp.Where):
        for func in where.find_all(exp.Func):
            col = func.this
            col_name = getattr(col, "name", None)
            table_name = getattr(col, "table", None) or default_table or "unknown_table"

            # Try to extract comparison value if exists
            val = None
            parent = getattr(func, "parent", None)
            if parent and hasattr(parent, "args"):
                val_expr = parent.args.get("expression")
                if val_expr:
                    val = val_expr.sql().strip("'")

            if col_name:
                issues.append({
                    "table": table_name,
                    "column": col_name,
                    "pattern": func.name.upper(),
                    "value": val
                })
    return issues

def generate_optimized_condition(pattern_info):
    """
    Given pattern info {pattern, column, value}, returns an optimized SQL snippet
    """
    pattern = pattern_info.get("pattern")
    col = pattern_info.get("column")
    val = pattern_info.get("value")

    if not col or not val:
        return None

    try:
        if pattern == "DATE":
            dt = datetime.strptime(val, "%Y-%m-%d")
            start = dt.strftime("%Y-%m-%d 00:00:00")
            end = dt.strftime("%Y-%m-%d 23:59:59")
            return f"{col} BETWEEN '{start}' AND '{end}'"
        elif pattern == "YEAR":
            year = int(val)
            return f"{col} BETWEEN '{year}-01-01 00:00:00' AND '{year}-12-31 23:59:59'"
        elif pattern == "UPPER":
            return f"{col} ILIKE '{val}'"
    except:
        return None

def get_from_table(expression):
    """Return the main table from FROM clause"""
    for from_clause in expression.find_all(exp.From):
        for table in from_clause.find_all(exp.Table):
            return table.name
    return "unknown_table"

def rewrite_query(expression, non_sargable_patterns):
    """
    Returns a rewritten SQL string where non-SARGable conditions are replaced
    by optimized forms (range-based or ILIKE for UPPER).
    """
    sql = expression.sql()

    # Replace patterns in the SQL string
    for pattern_info in non_sargable_patterns:
        pattern = pattern_info.get("pattern")
        col = pattern_info.get("column")
        val = pattern_info.get("value")

        if not col or not val:
            continue

        optimized = generate_optimized_condition(pattern_info)
        if not optimized:
            continue

        # Pattern matching replacement (simplified)
        if pattern == "DATE":
            sql = sql.replace(f"DATE({col}) = '{val}'", optimized)
        elif pattern == "YEAR":
            sql = sql.replace(f"YEAR({col}) = {val}", optimized)
        elif pattern == "UPPER":
            sql = sql.replace(f"UPPER({col}) = '{val}'", optimized)

    return sql

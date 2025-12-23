import sqlglot

def parse_sql(sql: str):
    try:
        return sqlglot.parse_one(sql)
    except Exception:
        return None

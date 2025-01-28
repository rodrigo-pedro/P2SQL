import sqlparse

def detect_dml_query(query):
    """
    Detects if a query is a DML query.
    """
    # use sqlglot to parse the query
    parsed = sqlparse.parse(query)
    for p in parsed:
        if p.get_type() in ("DROP", "ALTER", "TRUNCATE", "DELETE", "INSERT", "UPDATE"):
            raise Exception("DML query detected!")

    return query

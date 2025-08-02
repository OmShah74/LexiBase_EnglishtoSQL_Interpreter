# query_interface/core_nlp/sql_interpreter.py

import sqlglot
from django.db import connection
# --- CHANGE 1: Removed DCL from this import line ---
from sqlglot.expressions import DML, DDL

def execute_query(sql_string: str):
    """Parses, validates, and safely executes a SQL query string."""
    try:
        if not sql_string:
            raise ValueError("The generated query was empty.")
            
        parsed_queries = sqlglot.parse(sql_string, read="sqlite")
        
        if len(parsed_queries) > 1:
            raise ValueError("Execution of multiple SQL statements is forbidden.")
            
        parsed_query = parsed_queries[0]

        # --- CHANGE 2: Removed DCL from this validation check ---
        if any(expr for expr in parsed_query.find_all(DML, DDL)):
            raise ValueError("Query contains forbidden commands (e.g., UPDATE, DELETE, DROP). Only SELECT is permitted.")

        if not isinstance(parsed_query, sqlglot.exp.Select):
            raise ValueError("Only SELECT queries are allowed.")

        with connection.cursor() as cursor:
            cursor.execute(sql_string)
            columns = [col[0] for col in cursor.description]
            results = cursor.fetchall()
        
        return {"columns": columns, "results": results, "error": None}

    except Exception as e:
        return {"columns": [], "results": [], "error": f"Interpreter Error: {str(e)}"}
# query_interface/core_nlp/sql_interpreter.py
import sqlglot
import sqlite3
from sqlglot.expressions import DML, DDL

def execute_query(sql_string: str, db_path: str):
    print(f"DEBUG: [Interpreter] Received SQL to execute: '{sql_string}'")
    try:
        if not sql_string:
            raise ValueError("The generated query was empty.")
        if not db_path:
            raise ValueError("Database path not found. Please upload a database first.")

        print("DEBUG: [Interpreter] Parsing SQL string...")
        parsed_queries = sqlglot.parse(sql_string, read="sqlite")
        
        if not parsed_queries:
            raise ValueError("SQL string could not be parsed.")
        if len(parsed_queries) > 1:
            raise ValueError("Execution of multiple SQL statements is forbidden.")
        
        parsed_query = parsed_queries[0]
        print("DEBUG: [Interpreter] SQL parsing successful.")

        print("DEBUG: [Interpreter] Running security validation...")
        if any(expr for expr in parsed_query.find_all(DML, DDL)):
            raise ValueError("Query contains forbidden commands (e.g., UPDATE, DELETE, DROP). Only SELECT is permitted.")
        if not isinstance(parsed_query, sqlglot.exp.Select):
            raise ValueError("Only SELECT queries are allowed.")
        print("DEBUG: [Interpreter] Security validation passed.")

        print(f"DEBUG: [Interpreter] Connecting to user DB at {db_path} and executing query...")
        con = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)
        cursor = con.cursor()
        cursor.execute(sql_string)
        
        columns = [description[0] for description in cursor.description]
        results = cursor.fetchall()
        con.close()
        print(f"DEBUG: [Interpreter] Execution successful. Found {len(results)} rows.")
        return {"columns": columns, "results": results, "error": None}

    except Exception as e:
        print(f"ERROR: [Interpreter] An error occurred: {str(e)}")
        return {"columns": [], "results": [], "error": f"Interpreter Error: {str(e)}"}
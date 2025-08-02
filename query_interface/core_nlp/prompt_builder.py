# query_interface/core_nlp/prompt_builder.py
import sqlite3

def get_schema_representation(db_path: str) -> str:
    print(f"DEBUG: [Prompt Builder] Reading schema from DB at: {db_path}")
    if not db_path:
        return "-- No database provided --"
    try:
        con = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)
        cursor = con.cursor()
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table';")
        create_statements = cursor.fetchall()
        con.close()
        schema_sql = "\n".join([statement[0] for statement in create_statements if statement[0]])
        print("DEBUG: [Prompt Builder] Schema generation successful.")
        return schema_sql
    except Exception as e:
        print(f"ERROR: [Prompt Builder] Failed to read schema: {e}")
        return f"-- Error reading database schema: {e} --"

def create_text_to_sql_prompt(user_query: str, db_path: str) -> str:
    print("DEBUG: [Prompt Builder] Creating advanced prompt...")
    schema = get_schema_representation(db_path)
    prompt = f"""<|system|>
You are an expert SQLite data analyst. Your task is to convert a user's question into a single, valid, and efficient SQLite query.

**Instructions:**
1.  **Analyze the question:** First, understand the user's intent. If the question is complex, break it down into smaller, logical steps.
2.  **Use Common Table Expressions (CTEs):** For any query that requires intermediate steps (like finding a value to use in another part of the query), you MUST use a CTE (`WITH ... AS (...)`). This is crucial for clarity and correctness.
3.  **Output Only SQL:** Your final output must be ONLY the raw SQL query. Do not include any explanations, comments, or markdown.

**Example of a Complex Query:**
*   **Question:** "Show me the title of films that have the same length as the film 'ALIEN CENTER'."
*   **Your Thought Process (internal):**
    1.  First, I need to find the length of the film 'ALIEN CENTER'.
    2.  Then, I need to find all other films that have that same length.
    3.  I will use a CTE to store the length from the first step.
*   **Your Output (the raw SQL):**
    `WITH film_length AS (SELECT length FROM film WHERE title = 'ALIEN CENTER') SELECT title FROM film, film_length WHERE film.length = film_length.length AND film.title != 'ALIEN CENTER'`

---
**Database Schema:**
{schema}
---<|end|>
<|user|>
Here is the user's question: "{user_query}"<|end|>
<|assistant|>
"""
    print("DEBUG: [Prompt Builder] Advanced prompt created.")
    return prompt
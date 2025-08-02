# query_interface/core_nlp/prompt_builder.py

from django.apps import apps
from django.db import connection

def get_schema_representation():
    """
    Dynamically generates CREATE TABLE statements from all models
    in the 'query_interface' app for the prompt context.
    """
    app_models = apps.get_app_config('query_interface').get_models()
    if not app_models:
        return "-- No tables found in the database."

    with connection.schema_editor() as editor:
        schema_statements = []
        for model in app_models:
            # This generates the CREATE TABLE statement for a given model
            sql, _ = editor.table_sql(model)
            schema_statements.append(sql)
    return "\n".join(schema_statements)

def create_text_to_sql_prompt(user_query: str) -> str:
    """
    Constructs the full prompt for the LLM using the Phi-3 format.
    """
    schema = get_schema_representation()

    # Phi-3 requires a specific structured format for best results.
    prompt = f"""<|system|>
You are an expert SQLite data analyst. You must generate a single, valid SQLite query based on the provided schema and user question.
- Output only the raw SQL query.
- Do not add any explanations, comments, or markdown formatting like ```sql.

Database Schema:
---
{schema}
---<|end|>
<|user|>
{user_query}<|end|>
<|assistant|>
"""
    return prompt
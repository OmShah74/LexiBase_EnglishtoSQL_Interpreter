from llama_cpp import Llama
import os
import re
from django.conf import settings

llm_instance = None

def load_model():
    """Loads the GGUF model from the filesystem, ensuring it's a singleton."""
    global llm_instance
    if llm_instance is None:
        model_filename = "Phi-3-mini-4k-instruct-q4.gguf"
        model_path = os.path.join(settings.BASE_DIR, 'query_interface', 'llm_models', model_filename)

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"FATAL: Model file not found at {model_path}")
        
        print(f"DEBUG: Attempting to load model from: {model_path}")
        llm_instance = Llama(
            model_path=model_path,
            n_ctx=4096,
            n_gpu_layers=0,
            n_threads=-1,
            verbose=False
        )
        print("DEBUG: Model loading complete.")

def generate_sql_from_prompt(prompt: str) -> str:
    """Sends the prompt to the pre-loaded LLM and returns the cleaned SQL."""
    print("DEBUG: [LLM Handler] Received prompt. Generating SQL...")

    if llm_instance is None:
        raise Exception("LLM has not been loaded. Please restart the server.")
    
    response = llm_instance(
        prompt,
        max_tokens=512,
        stop=["<|end|>"],
        echo=False
    )

    raw_output = response['choices'][0]['text'].strip()
    print(f"DEBUG: [LLM Handler] Raw output from model: '{raw_output}'")

    # Remove markdown formatting
    cleaned_sql = re.sub(r'[`*_]+', '', raw_output)

    # Strip away thought processes, user questions, etc.
    # Keep only the SQL query (assuming it's the last code-like block)
    # Match multiline SQL with common patterns
    sql_blocks = re.findall(
        r'(WITH\s+[\s\S]+?SELECT[\s\S]+?)(?=(\n[A-Z ]+:|$))',  # for CTE or complex SQL
        cleaned_sql,
        re.IGNORECASE
    )

    if not sql_blocks:
        # Try fallback simple select statement extraction
        sql_blocks = re.findall(r'(SELECT[\s\S]+?)(?=(\n[A-Z ]+:|$))', cleaned_sql, re.IGNORECASE)

    if sql_blocks:
        final_sql = sql_blocks[-1][0].strip()
    else:
        # Fallback: remove leading explanation lines and return best guess
        lines = cleaned_sql.splitlines()
        query_lines = [line for line in lines if line.strip().lower().startswith(("select", "with"))]
        final_sql = '\n'.join(query_lines).strip()

    # Remove trailing semicolon if any
    if final_sql.endswith(";"):
        final_sql = final_sql[:-1]

    print(f"DEBUG: [LLM Handler] Final cleaned SQL: '{final_sql}'")
    return final_sql
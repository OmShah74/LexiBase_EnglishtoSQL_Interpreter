# query_interface/core_nlp/llm_handler.py

from llama_cpp import Llama
import os
from django.conf import settings

llm_instance = None

def load_model():
    """Loads the GGUF model from the filesystem, ensuring it's a singleton."""
    global llm_instance
    if llm_instance is None:
        model_filename = "Phi-3-mini-4k-instruct-q4.gguf"
        model_path = os.path.join(settings.BASE_DIR, 'query_interface', 'llm_models', model_filename)

        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Model file not found at {model_path}. "
                f"Please ensure '{model_filename}' is in the 'query_interface/llm_models/' directory."
            )
        
        llm_instance = Llama(
            model_path=model_path,
            n_ctx=4096,
            n_gpu_layers=0,
            verbose=False
        )
    return llm_instance

def generate_sql_from_prompt(prompt: str) -> str:
    """Sends the prompt to the CPU-loaded LLM and returns the cleaned SQL."""
    llm = load_model()
    
    response = llm(
        prompt,
        max_tokens=512,
        # --- CHANGE 1: Stricter stop conditions ---
        # Stop generating as soon as the model outputs a newline or semicolon.
        stop=["<|end|>", "\n", ";"],
        echo=False
    )
    
    # The raw output from the model
    raw_output = response['choices'][0]['text'].strip()
    
    # --- CHANGE 2: Defensive output cleaning ---
    # The model sometimes adds extra text on new lines.
    # We will split the output by the newline character and only take the first line.
    # This ensures any "support:" text or other junk on subsequent lines is discarded.
    cleaned_sql = raw_output.split('\n')[0].strip()

    return cleaned_sql
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

def clean_and_extract_sql(raw_text: str) -> str:
    """
    Extracts and cleans SQL query from LLM response.
    Handles various response formats and removes explanatory text.
    """
    
    # Remove markdown formatting
    cleaned_text = re.sub(r'[`*_]+', '', raw_text)
    
    # Split by common separators and look for SQL patterns
    sections = re.split(r'\n---\n|\n\*\*Output:\*\*|\n\*\*User\'s question:\*\*', cleaned_text)
    
    best_sql = ""
    
    for section in sections:
        section = section.strip()
        
        # Skip sections that are clearly explanatory text
        if any(phrase in section.lower() for phrase in [
            "thought process:", "user's question:", "after that,", "first, i", 
            "then, i'll", "convert", "understand", "identify"
        ]):
            continue
            
        # Look for SQL patterns in this section
        sql_candidates = []
        
        # Pattern 1: Complete WITH...SELECT statements
        with_select_pattern = r'(WITH\s+\w+\s+AS\s*\([^)]+\)\s*SELECT[^;]*?)(?=\s*(?:---|$|\n\s*\n))'
        with_matches = re.findall(with_select_pattern, section, re.IGNORECASE | re.DOTALL)
        sql_candidates.extend(with_matches)
        
        # Pattern 2: Simple SELECT statements
        select_pattern = r'(SELECT\s+[^;]*?(?:FROM|JOIN)[^;]*?)(?=\s*(?:---|$|\n\s*\n))'
        select_matches = re.findall(select_pattern, section, re.IGNORECASE | re.DOTALL)
        sql_candidates.extend(select_matches)
        
        # Pattern 3: Multi-line SQL blocks (more permissive)
        if not sql_candidates:
            lines = section.split('\n')
            sql_lines = []
            in_sql_block = False
            
            for line in lines:
                line_stripped = line.strip()
                
                # Start of SQL block
                if re.match(r'^\s*(WITH|SELECT)\s+', line_stripped, re.IGNORECASE):
                    in_sql_block = True
                    sql_lines = [line_stripped]
                    continue
                    
                # Continue SQL block
                if in_sql_block:
                    # Stop if we hit explanatory text
                    if any(phrase in line_stripped.lower() for phrase in [
                        "user's question:", "thought process:", "after that", "convert"
                    ]):
                        break
                        
                    # Stop if empty line followed by non-SQL content
                    if not line_stripped and sql_lines:
                        break
                        
                    # Add SQL line
                    if line_stripped:
                        sql_lines.append(line_stripped)
                        
            if sql_lines:
                candidate = ' '.join(sql_lines)
                if re.search(r'(SELECT|WITH).*?(FROM|JOIN)', candidate, re.IGNORECASE | re.DOTALL):
                    sql_candidates.append(candidate)
        
        # Choose the best candidate from this section
        for candidate in sql_candidates:
            candidate = candidate.strip()
            
            # Clean up the candidate
            candidate = re.sub(r'\s+', ' ', candidate)  # Normalize whitespace
            candidate = re.sub(r';\s*$', '', candidate)  # Remove trailing semicolon
            
            # Prefer more complete queries
            if len(candidate) > len(best_sql) and is_valid_sql_structure(candidate):
                best_sql = candidate
    
    # If no good SQL found, try one more fallback approach
    if not best_sql:
        # Look for any line that starts with WITH or SELECT
        lines = cleaned_text.split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            if re.match(r'^\s*(WITH|SELECT)\s+', line, re.IGNORECASE):
                # Collect this line and subsequent related lines
                sql_parts = [line]
                for j in range(i+1, len(lines)):
                    next_line = lines[j].strip()
                    if not next_line:
                        continue
                    if any(phrase in next_line.lower() for phrase in [
                        "user's question:", "thought process:", "convert", "---"
                    ]):
                        break
                    if re.search(r'(FROM|JOIN|WHERE|GROUP|ORDER|;)', next_line, re.IGNORECASE):
                        sql_parts.append(next_line)
                    elif len(sql_parts) > 1:  # Stop after we have a complete statement
                        break
                
                candidate = ' '.join(sql_parts)
                candidate = re.sub(r'\s+', ' ', candidate)
                candidate = re.sub(r';\s*$', '', candidate)
                
                if is_valid_sql_structure(candidate):
                    best_sql = candidate
                    break
    
    return best_sql.strip()

def is_valid_sql_structure(sql_text: str) -> bool:
    """
    Basic validation to check if the text looks like valid SQL structure.
    """
    sql_lower = sql_text.lower()
    
    # Must contain basic SQL keywords
    if not any(keyword in sql_lower for keyword in ['select', 'with']):
        return False
        
    # Should not contain obvious non-SQL content
    invalid_phrases = [
        "user's question:", "thought process:", "after that,", "convert", 
        "understand", "identify", "first, i", "then, i'll"
    ]
    
    for phrase in invalid_phrases:
        if phrase in sql_lower:
            return False
    
    # Basic structure check
    if 'select' in sql_lower:
        return 'from' in sql_lower or 'join' in sql_lower
    elif 'with' in sql_lower:
        return 'select' in sql_lower and ('from' in sql_lower or 'join' in sql_lower)
    
    return False

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

    # Extract and clean the SQL
    final_sql = clean_and_extract_sql(raw_output)
    
    if not final_sql:
        print("WARNING: [LLM Handler] No valid SQL found in response, attempting fallback...")
        # Last resort: try to find any SELECT statement
        lines = raw_output.split('\n')
        for line in lines:
            if re.match(r'^\s*(SELECT|WITH)', line.strip(), re.IGNORECASE):
                final_sql = line.strip()
                break
    
    print(f"DEBUG: [LLM Handler] Final cleaned SQL: '{final_sql}'")
    
    if not final_sql:
        raise Exception("Could not extract valid SQL from LLM response")
    
    return final_sql
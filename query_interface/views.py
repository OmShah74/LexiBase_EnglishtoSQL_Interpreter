# query_interface/views.py
from django.shortcuts import render
from django.conf import settings
import os
import uuid

from .forms import DatabaseQueryForm
from .core_nlp.prompt_builder import create_text_to_sql_prompt
from .core_nlp.llm_handler import generate_sql_from_prompt
from .core_nlp.sql_interpreter import execute_query

def query_view(request):
    print("\n--- [View] New request received ---")
    form = DatabaseQueryForm()
    context = {'form': form}

    if request.GET.get('new_session'):
        print("DEBUG: [View] 'new_session' parameter found. Clearing session data.")
        if 'db_path' in request.session:
            try:
                os.remove(request.session['db_path'])
                print(f"DEBUG: [View] Deleted temp DB file: {request.session['db_path']}")
            except OSError as e:
                print(f"ERROR: [View] Could not delete temp DB file: {e}")
            del request.session['db_path']
        if 'db_name' in request.session:
            del request.session['db_name']

    if request.method == 'POST':
        print("DEBUG: [View] Request method is POST.")
        form = DatabaseQueryForm(request.POST, request.FILES)
        if form.is_valid():
            print("DEBUG: [View] Form is valid.")
            user_query = form.cleaned_data['query']
            uploaded_file = request.FILES.get('db_file')
            db_path = request.session.get('db_path')

            if uploaded_file:
                print(f"DEBUG: [View] New file uploaded: {uploaded_file.name}")
                unique_filename = f"{uuid.uuid4()}_{uploaded_file.name}"
                db_path = os.path.join(settings.BASE_DIR, 'temp_uploads', unique_filename)
                
                with open(db_path, 'wb+') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)
                
                request.session['db_path'] = db_path
                request.session['db_name'] = uploaded_file.name
                print(f"DEBUG: [View] File saved to session. Path: {db_path}")

            context['user_query'] = user_query
            
            if db_path:
                print("DEBUG: [View] DB path found. Proceeding with NLP pipeline.")
                try:
                    prompt = create_text_to_sql_prompt(user_query, db_path)
                    sql_query = generate_sql_from_prompt(prompt)
                    context['sql_query'] = sql_query

                    results_data = execute_query(sql_query, db_path)
                    context['results_data'] = results_data
                except Exception as e:
                    print(f"ERROR: [View] Unhandled exception in NLP pipeline: {e}")
                    context['system_error'] = f"A system error occurred: {str(e)}"
            else:
                print("WARNING: [View] Query submitted but no database in session.")
                context['system_error'] = "You must upload a database file before making a query."
        else:
            print(f"ERROR: [View] Form is invalid. Errors: {form.errors}")
    
    context['db_name'] = request.session.get('db_name')
    print("DEBUG: [View] Rendering template...")
    return render(request, 'query_interface/index.html', context)
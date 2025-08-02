# query_interface/views.py

from django.shortcuts import render
from .forms import QueryForm
from .core_nlp.prompt_builder import create_text_to_sql_prompt
from .core_nlp.llm_handler import generate_sql_from_prompt
from .core_nlp.sql_interpreter import execute_query

def query_view(request):
    form = QueryForm()
    context = {'form': form}

    if request.method == 'POST':
        form = QueryForm(request.POST)
        if form.is_valid():
            user_query = form.cleaned_data['query']
            context['user_query'] = user_query
            try:
                prompt = create_text_to_sql_prompt(user_query)
                sql_query = generate_sql_from_prompt(prompt)
                context['sql_query'] = sql_query

                results_data = execute_query(sql_query)
                context['results_data'] = results_data
            
            except Exception as e:
                context['system_error'] = f"A system error occurred: {str(e)}"
    
    return render(request, 'query_interface/index.html', context)
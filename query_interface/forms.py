# query_interface/forms.py

from django import forms

class QueryForm(forms.Form):
    query = forms.CharField(
        label="Ask a question about our employees or products",
        required=True,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'class': 'form-control',
            'placeholder': 'e.g., "Show me the 5 highest paid employees" or "What are the 3 most expensive products?"'
        })
    )
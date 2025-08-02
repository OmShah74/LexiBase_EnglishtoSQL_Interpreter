# query_interface/forms.py
from django import forms

class DatabaseQueryForm(forms.Form):
    db_file = forms.FileField(
        label="Upload your SQLite Database (.db, .sqlite3)",
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'custom-file-input'})
    )
    query = forms.CharField(
        label="Ask a question about your data",
        required=True,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'class': 'form-control',
            'placeholder': 'e.g., "Which 5 actors appeared in the most films?"'
        })
    )
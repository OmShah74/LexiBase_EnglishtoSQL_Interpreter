# query_interface/apps.py
from django.apps import AppConfig

class QueryInterfaceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'query_interface'

    def ready(self):
        # This method runs once when the Django server starts.
        from .core_nlp import llm_handler
        print("---- [App Ready] Triggering NLP Model Pre-loading ----")
        llm_handler.load_model()
        print("---- [App Ready] NLP Model is pre-loaded and ready. ----")
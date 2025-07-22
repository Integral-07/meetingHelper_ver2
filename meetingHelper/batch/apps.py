from django.apps import AppConfig
import threading

class BatchConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'batch'

    def ready(self):
        from .ap_scheduler import start

        threading.Thread(target=start)
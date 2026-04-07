"""
Celery configuration for recruitment_platform project.
"""

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "recruitment_platform.settings")

app = Celery("recruitment_platform")

# Load config from Django settings, using the CELERY_ namespace.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Autodiscover tasks from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Diagnostic task that prints its own request info."""
    print(f"Request: {self.request!r}")

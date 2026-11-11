"""WSGI entry point. gunicorn serves `starter.wsgi:application`; the runtime
derives that target from manage.py's DJANGO_SETTINGS_MODULE."""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "starter.settings")

application = get_wsgi_application()

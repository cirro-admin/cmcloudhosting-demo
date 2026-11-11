"""ASGI entry point, for a customer who prefers an async worker class."""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "starter.settings")

application = get_asgi_application()

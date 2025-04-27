from django.apps import AppConfig
from django.conf import settings
import sys, os

class MailConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mail'

    def ready(self):
            # Only run under 'runserver'
            if len(sys.argv) < 2 or sys.argv[1] != "runserver":
                return

            # Under DEBUG, StatReloader spawns a watcher *and* a child.
            # Only the child has RUN_MAIN="true"
            if settings.DEBUG and os.environ.get("RUN_MAIN") != "true":
                return

            # Don’t start during manage.py migrate/makemigrations/shell
            if sys.argv[1] in ("migrate", "makemigrations", "shell"):
                return

            # At this point we know:
            # - We’re running 'manage.py runserver'
            # - We’re in the *child* process (not the watcher)
            from .scheduler import start
            from . import email
            start()
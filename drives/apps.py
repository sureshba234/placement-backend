from django.apps import AppConfig


class DrivesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'drives'

    def ready(self):
        import drives.signals  # noqa: F401

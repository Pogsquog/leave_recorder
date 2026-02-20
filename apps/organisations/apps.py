from django.apps import AppConfig


class OrganisationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.organisations"
    verbose_name = "Organisations"

    def ready(self):
        import apps.organisations.signals  # noqa

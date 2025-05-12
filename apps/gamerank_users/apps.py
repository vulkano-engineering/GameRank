from django.apps import AppConfig


class GamerankUsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.gamerank_users"

    def ready(self):
        import apps.gamerank_users.signals  # noqa

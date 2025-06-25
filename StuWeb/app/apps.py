from django.apps import AppConfig


class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'

    def ready(self):
        # from .views import release_overdue_seats
        # release_overdue_seats(repeat=60, repeat_until=None)
        pass

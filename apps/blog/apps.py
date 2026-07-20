from django.apps import AppConfig


class BlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.blog'

    # Avoids mis-referencing legacy/transitional models that may define
    # auth-related fields via lazy app labels.
    label = 'blog'

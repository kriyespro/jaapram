from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    # Site row for SITE_ID is ensured in migration accounts.0002_ensure_site_for_allauth
    # (avoid DB queries in ready() — Django warns and collectstatic imports apps early).

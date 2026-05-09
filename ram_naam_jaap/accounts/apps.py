from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        import logging

        from django.conf import settings
        from django.contrib.sites.models import Site
        from django.db import OperationalError
        from django.db.utils import ProgrammingError

        # django.contrib.sites: allauth calls get_current_site() on signup.
        # Missing row for SITE_ID → Site.DoesNotExist → 500.
        # Skip until DB tables exist (migrate / first connection).
        try:
            site_id = int(getattr(settings, 'SITE_ID', 1) or 1)
            domain = getattr(settings, 'SITE_DOMAIN', None) or 'localhost'
            name = getattr(settings, 'SITE_BRAND_NAME', None) or 'Ram Naam Jaap'
            if not Site.objects.filter(pk=site_id).exists():
                Site.objects.create(pk=site_id, domain=domain, name=name)
        except (ProgrammingError, OperationalError):
            pass
        except Exception:
            logging.getLogger(__name__).exception('accounts.apps: ensure Site failed')

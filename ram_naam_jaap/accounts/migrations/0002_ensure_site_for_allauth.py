from django.conf import settings
from django.db import migrations


def ensure_site_for_allauth(apps, schema_editor):
    """django.contrib.sites row for SITE_ID — required by allauth get_current_site()."""
    Site = apps.get_model('sites', 'Site')
    site_id = int(getattr(settings, 'SITE_ID', 1) or 1)
    domain = getattr(settings, 'SITE_DOMAIN', None) or 'localhost'
    name = getattr(settings, 'SITE_BRAND_NAME', None) or 'Ram Naam Jaap'
    if not Site.objects.filter(pk=site_id).exists():
        Site.objects.create(pk=site_id, domain=domain, name=name)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('sites', '0002_alter_domain_unique'),
    ]

    operations = [
        migrations.RunPython(ensure_site_for_allauth, noop_reverse),
    ]

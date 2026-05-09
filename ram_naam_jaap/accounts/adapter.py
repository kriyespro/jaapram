"""django-allauth adapter: resilient email + hooks."""

import logging

from django.conf import settings
from allauth.account.adapter import DefaultAccountAdapter

logger = logging.getLogger(__name__)


class RamJaapAccountAdapter(DefaultAccountAdapter):
    """
    Avoid 500s when SMTP is misconfigured: signup should still complete.
    Failed messages are logged; re-raised in DEBUG for visibility.
    """

    def send_mail(self, template_prefix, email, context):
        try:
            super().send_mail(template_prefix, email, context)
        except Exception as exc:
            logger.exception(
                "Allauth email failed (template=%s, to=%s): %s",
                template_prefix,
                email,
                exc,
            )
            if settings.DEBUG:
                raise

from django.conf import settings


def settings_context_processor(request):
    return {
        'SITE_NAME': settings.SITE_NAME,
        'SITE_DOMAIN': settings.SITE_DOMAIN,
        'SITE_URL': settings.SITE_URL,
        'SITE_DESCRIPTION': settings.SITE_DESCRIPTION,
        'GOOGLE_ANALYTICS_ID': settings.GOOGLE_ANALYTICS_ID
    }

from gui.models.settings import GeneralSettings
from django.conf import settings


def context(request):
    try:
        general = GeneralSettings.objects.get()

        return {
            "LAST_VERSION": general.last_version,
            "CURRENT_VERSION": settings.VERSION
        }
    except GeneralSettings.DoesNotExist:
        return {}

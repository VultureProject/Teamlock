#!/usr/bin/env python

import requests

from django.conf import settings
from gui.models.settings import GeneralSettings


def checkVersion():
    r = requests.get(
        'https://www.teamlock.io/api/version',
        proxies=settings.PROXY
    )

    version = r.json()['version']

    general_settings = GeneralSettings.objects.get()
    general_settings.last_version = version
    general_settings.save()

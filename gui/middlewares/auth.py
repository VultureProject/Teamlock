#!/usr/bin/python

"""This file is part of Teamlock.

Teamlock is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Teamlock is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Teamlock.  If not, see <http://www.gnu.org/licenses/>."""

__author__ = "Olivier de Régis"
__credits__ = []
__license__ = "GPLv3"
__version__ = "3.0.0"
__maintainer__ = "Teamlock Project"
__email__ = "contact@teamlock.io"
__doc__ = ''

import datetime

from gui.models.settings import SecuritySettings

from django.http import HttpResponseForbidden
from django.http import HttpResponseRedirect
from django.urls import resolve
from django.urls import reverse


def AuthenticationMiddleware(get_response):
    # One-time configuration and initialization.

    def middleware(request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        # if resolve(request.path_info).url_name == 'install':
                    # return get_response(request)

        user = request.user
        if resolve(request.path_info).url_name in (
                'install', 'configure_account', 'change_password') \
                or user.is_anonymous:
            return get_response(request)

        if not user.configure:
            return HttpResponseRedirect('/configure/{}'.format(user.id))

        if user.is_locked:
            return HttpResponseForbidden()

        try:
            settings_teamlock = SecuritySettings.objects.get()
        except SecuritySettings.DoesNotExist:
            return HttpResponseRedirect(reverse('gui:install'))
            settings_teamlock = SecuritySettings(password_change=100)

        try:
            delta = datetime.date.today() - user.last_change_passwd
            if delta.days > settings_teamlock.password_change:
                return HttpResponseRedirect(reverse('gui:change_password'))
        except AttributeError:
            return HttpResponseRedirect(reverse('gui:change_password'))

        return get_response(request)

    return middleware

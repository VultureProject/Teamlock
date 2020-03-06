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

from gui.models.settings import SecuritySettings
# from gui.models.workspace import Workspace, Shared
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.urls import resolve
import datetime


def AuthenticationMiddleware(get_response):
    # One-time configuration and initialization.

    def middleware(request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        # if resolve(request.path_info).url_name == 'install':
                    # return get_response(request)

        if 'api' in request.path_info:
            pass

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
            settings = SecuritySettings.objects.get()
        except SecuritySettings.DoesNotExist:
            return HttpResponseRedirect('/install')
            settings = SecuritySettings(password_change=100)

        try:
            date_last_change = datetime.datetime(
                user.last_change_passwd.year,
                user.last_change_passwd.month,
                user.last_change_passwd.day
            )

            if ((datetime.datetime.now() -
                 date_last_change).days >= settings.password_change):
                return HttpResponseRedirect('/changepassword')
        except AttributeError:
            return HttpResponseRedirect('/changepassword')

        return get_response(request)

    return middleware

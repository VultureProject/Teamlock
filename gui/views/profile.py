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

import hashlib
import json
import logging.config

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.translation import ugettext as _
from gui.models.settings import SecuritySettings
from gui.models.user import UserSession
from gui.models.workspace import Shared
from gui.models.workspace import Workspace
from teamlock_toolkit.tools import update_password_toolkit

logging.config.dictConfig(settings.LOG_SETTINGS)
logger = logging.getLogger('django')


@login_required()
def profile(request, success=False, error=False):
    if not request.is_ajax():
        return render(request, 'profile.html', {
            'success': success,
            'error': error
        })

    order_dir = {
        'asc': "-",
        'desc': ""
    }

    draw = request.GET.get('draw')
    start = request.GET.get("start")
    length = request.GET.get('length', 10)
    columns = json.loads(request.GET['columns'])
    order_0_dir = request.GET.get('order[0][dir]')
    order_0_col = request.GET.get('order[0][column]')

    order = f"{order_dir[order_0_dir]}{columns[int(order_0_col)]}"

    nb_data = UserSession.objects.filter(user=request.user).count()
    data = [model_to_dict(f) for f in UserSession.objects.filter(
        user=request.user).order_by(order)[int(start): int(length) + int(start)]]

    return JsonResponse({
        'draw': draw,
        'recordsTotal': nb_data,
        'recordsFiltered': nb_data,
        'data': data
    })


@login_required
def update_password(request):
    if not request.method == "POST":
        return profile(request)

    old_password = request.POST['old_password']
    new_password = request.POST['new_password']
    confirm_password = request.POST['confirm_password']

    if not request.user.check_password(old_password):
        return profile(request, error=_("Invalid password"))

    if new_password != confirm_password:
        return profile(request, error=_("Password mismatch"))

    try:
        settings = SecuritySettings.objects.get()
    except SecuritySettings.DoesNotExist:
        settings = SecuritySettings(length_password=8)

    if len(new_password) < settings.length_password:
        error = "The password must be at least {} characters long.".format(
            settings.length_password)
        return profile(request, error=error)

    # At least one letter and one non-letter
    first_isalpha = new_password[0].isalpha()
    if all(c.isalpha() == first_isalpha for c in new_password):
        error = _("The password must contain at least one letter and at least \
                     one digit or punctuation character.")
        return profile(request, error=error)

    if old_password == new_password:
        error = _("You must choose a new password")
        return profile(request, error=error)

    workspaces = Workspace.objects.filter(owner=request.user)
    shares = Shared.objects.filter(user=request.user)

    passphrase = hashlib.sha512(
        old_password.encode("utf-8")).hexdigest()
    new_passphrase = hashlib.sha512(
        new_password.encode('utf-8')).hexdigest()

    try:
        update_password_toolkit(
            request.user,
            workspaces,
            shares,
            passphrase,
            new_passphrase,
            new_password
        )
    except Exception as e:
        return profile(request, error=str(e))

    return profile(request, success=_("Password updated"))


@login_required()
def generate_recovery_view(request):
    try:
        data = request.user.generate_recovery_key(
            request.POST['passphrase'],
            request.session.get('key')
        )

        return JsonResponse(data)

    except Exception as e:
        logger.error(e, exc_info=1)
        return JsonResponse({
            'status': False,
            'error': _('An error has occured')
        })

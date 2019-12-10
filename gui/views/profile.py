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

from django.http import JsonResponse, HttpResponseRedirect
from teamlock_toolkit.tools import update_password_toolkit
from django.contrib.auth.decorators import login_required
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext as _
from gui.models.workspace import Workspace, Shared
from gui.models.settings import SecuritySettings
from gui.forms.mobile import MobileForm
from gui.models.mobile import Mobile
from gui.forms.user import UserForm
from django.shortcuts import render
from django.db import IntegrityError
from django.conf import settings
import logging.config
import hashlib

logging.config.dictConfig(settings.LOG_SETTINGS)
logger = logging.getLogger('django')


@login_required()
def profile(request, success=False, error=False):
    form_user = UserForm(instance=request.user)

    return render(request, 'profile.html', {
        'form_user': form_user,
        'success': success,
        'error': error
    })


@login_required()
def mobile_save(request):
    form_user = UserForm(instance=request.user)
    mobiles = Mobile.objects.filter(user=request.user)
    mobile_form = MobileForm(request.POST)

    if not mobile_form.is_valid():
        return render(request, 'profile.html', {
            'form_user': form_user,
            'form_mobile': mobile_form,
            'mobiles': mobiles
        })

    mobile = mobile_form.save(commit=False)

    mobile.user = request.user
    mobile.key = get_random_string(length=8)

    try:
        mobile.save()
        # mobile_form.save_m2m()
    except IntegrityError:
        return render(request, 'profile.html', {
            'form_user': form_user,
            'form_mobile': mobile_form,
            'mobiles': mobiles
        })

    return HttpResponseRedirect('/profile')


@login_required()
def mobile_del(request):
    try:
        mobile_id = request.POST['id']
    except KeyError:
        return JsonResponse({
            'status': False,
            'error': _("Mobile not found")
        })

    Mobile.objects.get(pk=mobile_id).delete()
    return JsonResponse({'status': True})


@login_required
def update_password(request):
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

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

from gui.forms.settings import (GeneralSettingsForm,
                                SecuritySettingsForm, MailSettingsForm)
from gui.models.settings import GeneralSettings, SecuritySettings, MailSettings
from teamlock_toolkit.workspace_utils import WorkspaceUtils
from django.http import HttpResponseRedirect, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import ugettext as _
from django.contrib.auth import get_user_model
from django.shortcuts import render
import hashlib
import datetime


@csrf_exempt
def install(request):
    # Check if installation have already be done
    if get_user_model().objects.count():
        return HttpResponseRedirect('/')

    mail_form = MailSettingsForm(instance=MailSettings())
    security_form = SecuritySettingsForm(instance=SecuritySettings())
    general_form = GeneralSettingsForm(instance=GeneralSettings())

    if request.method == "POST":
        User = get_user_model()
        secu_settings = SecuritySettings(
            password_change=int(request.POST['password_change']),
            length_password=int(request.POST['length_password']),
            key_size=int(request.POST['key_size']),
        )

        mail_settings = MailSettings(
            host=request.POST['host']
        )

        gen_settings = GeneralSettings(
            company_name=request.POST['company_name']
        )

        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        password = request.POST['password']
        password = request.POST['password']
        repassword = request.POST['repassword']

        backup_password = request.POST['backup_password']

        if password != repassword:
            error = _("Password mismatch")
            return JsonResponse({
                'status': False,
                'error': error
            })

        if len(password) < secu_settings.length_password:
            error = _("The password must be at least \
                {} characters long.".format(secu_settings.length_password))
            return JsonResponse({
                'status': False,
                'error': error
            })

        # At least one letter and one non-letter
        first_isalpha = password[0].isalpha()
        if all(c.isalpha() == first_isalpha for c in password):
            error = _(
                "The password must contain at least one letter and at \
                least one digit or punctuation character.")
            return JsonResponse({
                'status': False,
                'error': error
            })

        superuser = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            last_change_passwd=datetime.datetime.now(),
            configure=True,
            is_superuser=True
        )

        superuser.set_password(password)
        superuser.generate_keys(hashlib.sha512(
            password.encode('utf-8')).hexdigest())
        superuser.save()

        backup_user = User(
            first_name="Backup",
            last_name="Backup",
            email="backup@teamlock.io",
            last_change_passwd=datetime.datetime.now(),
            configure=True,
            is_superuser=False
        )

        backup_user.set_password(password)
        backup_user.generate_keys(hashlib.sha512(
            backup_password.encode('utf-8')).hexdigest())
        backup_user.save()

        secu_settings.save()
        try:
            mail_settings.save()
        except Exception:
            pass

        gen_settings.save()

        # Creating workspace
        workspace_utils = WorkspaceUtils(superuser)
        status, error = workspace_utils.create_workspace(name="Personal")

        return JsonResponse({'status': True})

    return render(request, 'install.html', {
        'security': security_form,
        'general': general_form,
        'mail': mail_form,
    })

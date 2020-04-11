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


from django.http import HttpResponseRedirect, JsonResponse
from gui.models.settings import GeneralSettings, SecuritySettings, MailSettings
from gui.forms.settings import (GeneralSettingsForm, SecuritySettingsForm, MailSettingsForm)
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import ugettext as _
from teamlock_toolkit.mail import send_mail_test
from gui.models.workspace import Workspace
from django.shortcuts import render
from django.conf import settings as django_settings
import logging

logging.config.dictConfig(django_settings.LOG_SETTINGS)
logger = logging.getLogger('django')


@user_passes_test(lambda u: u.is_superuser)
def settings(request, classe_name=None):
    if not request.user.is_superuser:
        return HttpResponseRedirect('/')

    try:
        mail = MailSettings.objects.get()
    except MailSettings.DoesNotExist:
        mail = MailSettings()

    try:
        security = SecuritySettings.objects.get()
    except SecuritySettings.DoesNotExist:
        security = SecuritySettings()

    try:
        general = GeneralSettings.objects.get()
    except GeneralSettings.DoesNotExist:
        general = GeneralSettings()

    mail_form = MailSettingsForm(instance=mail)
    security_form = SecuritySettingsForm(instance=security)
    general_form = GeneralSettingsForm(instance=general)

    if request.POST:
        if classe_name == 'mail':
            mail_form = MailSettingsForm(request.POST, instance=mail)
            if mail_form.is_valid():
                mail_form.save()

        elif classe_name == 'security':
            security_form = SecuritySettingsForm(
                request.POST, instance=security)
            if security_form.is_valid():
                security_form.save()

        elif classe_name == 'general':
            general_form = GeneralSettingsForm(request.POST, instance=general)
            if general_form.is_valid():
                general_form.save()

    return render(request, 'settings.html', {
        'nb_workspaces': Workspace.objects.count(),
        'security': security_form,
        'general': general_form,
        'mail': mail_form,
    })


@csrf_exempt
def test_send_mail(request):
    try:
        mail_configuration = {
            'host': request.POST['host'],
            'to': request.POST['to']
        }

    except KeyError:
        return JsonResponse({
            'status': False,
            'error': _("All data is needed.")
        })

    status, error = send_mail_test(mail_configuration)

    if not status:
        return JsonResponse({
            'status': False,
            'error': error
        })

    return JsonResponse({'status': True})

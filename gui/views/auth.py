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

from django.http import HttpResponseRedirect, HttpResponseForbidden, JsonResponse
from django.contrib.auth import authenticate, login, logout
from teamlock_toolkit.workspace_utils import WorkspaceUtils
from teamlock_toolkit.tools import update_password_toolkit
from django.contrib.auth.decorators import login_required
from teamlock_toolkit.crypto_utils import CryptoUtils
from django.utils.translation import ugettext as _
from gui.models.workspace import Workspace, Shared
from gui.models.settings import SecuritySettings
from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.conf import settings
from django.urls import reverse
import datetime
import logging
import hashlib
import base64

logging.config.dictConfig(settings.LOG_SETTINGS)
logger = logging.getLogger('auth')


@login_required()
def main(request):
    return HttpResponseRedirect(reverse("workspace"))


def log_in(request):
    """
    """
    if request.POST:
        email = request.POST['email']
        password = request.POST['password']

        user = authenticate(username=email, password=password)

        if user:
            last_seen = user.last_login
            login(request, user)

            # Encrypting password for workspace
            crypto_utils = CryptoUtils(user)
            request.session['key'] = crypto_utils.generate_sim()
            passphrase = hashlib.sha512(password.encode()).hexdigest()
            passphrase = crypto_utils.sym_encrypt(passphrase, request.session['key'])

            try:
                request.session['last_seen'] = last_seen.strftime(
                    '%d/%m/%Y %H:%M:%S')
            except (KeyError, AttributeError):
                request.session['last_seen'] = datetime.datetime.now(
                ).strftime('%d/%m/%Y %H:%M:%S')

            url_next = request.POST.get('next', '/')
            if url_next == "":
                url_next = "/"

            logger.info("User {} successfully authenticated".format(
                user.email
            ))

            return JsonResponse({
                'status': True,
                'passphrase': passphrase,
                'url_next': url_next
            })

        else:
            logger.info('User {} failed to authenticate'.format(email))

            return JsonResponse({
                'status': False,
                'error': _("Authentication failed")
            })

    url_next = request.GET.get('next', '/')
    message = None
    return render(request, 'logon.html', {
        'url_next': url_next,
        'message': message
    })


@login_required()
def log_out(request):
    """
    """
    logout(request)
    return HttpResponseRedirect('/login/')


def configure_account(request, user_id):
    model_user = get_user_model()

    try:
        user = model_user.objects.get(pk=user_id)
    except model_user.DoesNotExist:
        return HttpResponseForbidden('Not allowed')

    if user.configure:
        return HttpResponseRedirect('/')

    try:
        settings = SecuritySettings.objects.get()
    except SecuritySettings.DoesNotExist:
        settings = SecuritySettings(length_password=8)

    if request.method == "POST":
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        password = request.POST['password']
        password = request.POST['password']
        repassword = request.POST['repassword']

        if password != repassword:
            error = _("Password mismatch")
            return render(request, 'configure.html', {
                'user': user,
                'error': error
            })

        if len(password) < settings.length_password:
            error = "The password must be at least {} characters long.".format(
                settings.length_password)
            return render(request, 'configure.html', {
                'user': user,
                'error': error
            })

        # At least one letter and one non-letter
        first_isalpha = password[0].isalpha()
        if all(c.isalpha() == first_isalpha for c in password):
            error = _("The password must contain at least one letter and at least \
                         one digit or punctuation character.")
            return render(request, 'configure.html', {
                'user': user,
                'error': error
            })

        hashed_passwd = hashlib.sha512(password.encode('utf-8')).hexdigest()
        user.generate_keys(hashed_passwd)
        user.set_password(password)

        user.first_name = first_name
        user.last_name = last_name
        user.last_change_passwd = datetime.datetime.now()
        user.configure = True
        user.save()

        workspace_utils = WorkspaceUtils(user)
        workspace_utils.create_workspace("Personal")

        logger.info("User {} configured".format(user.email))
        return HttpResponseRedirect('/login')

    password_indication = "At least {} characters, with one letter and \
    one digit or punctuation".format(settings.length_password)

    return render(request, 'configure.html', {
        'user': user,
        'password_indication': password_indication,
    })


def recover_passphrase(request):
    if request.method == "GET":
        return render(request, "recover_passphrase.html")

    email = request.POST['email']
    new_password = request.POST['new_password']
    confirm_password = request.POST['confirm_password']

    if new_password != confirm_password:
        return render(request, 'recover_passphrase.html', {
            'error': _('Passwords mismatch')
        })

    try:
        settings = SecuritySettings.objects.get()
    except SecuritySettings.DoesNotExist:
        settings = SecuritySettings(length_password=8)

    if len(new_password) < settings.length_password:
        error = "The password must be at least {} characters long.".format(
            settings.length_password)
        return render(request, 'recover_passphrase.html', {
            'error': error
        })

    # At least one letter and one non-letter
    first_isalpha = new_password[0].isalpha()
    if all(c.isalpha() == first_isalpha for c in new_password):
        error = _("The password must contain at least one letter and at least \
                     one digit or punctuation character.")
        return render(request, 'recover_passphrase.html', {
            'error': error
        })

    try:
        recovery_file = request.FILES['recovery_file'].read()
        recovery_file = base64.b64decode(recovery_file).decode('utf-8')
    except KeyError:
        return render(request, 'recover_passphrase.html', {
            'error': _('No recovery file provided')
        })

    try:
        user = get_user_model().objects.get(email=email)
    except get_user_model().DoesNotExist:
        return render(request, 'recover_passphrase.html', {
            'error': _('No such user')
        })

    recovery_passphrase = user.recovery_passphrase
    crypto_utils = CryptoUtils()

    decrypted_recovery = crypto_utils.sym_decrypt(recovery_passphrase, recovery_file)

    workspaces = Workspace.objects.filter(owner=user)
    shares = Shared.objects.filter(user=user)

    new_passphrase = hashlib.sha512(
        new_password.encode('utf-8')).hexdigest()

    try:
        update_password_toolkit(
            user,
            workspaces,
            shares,
            decrypted_recovery,
            new_passphrase,
            new_password
        )
    except Exception as e:
        return render(request, 'recover_passphrase.html', {
            'error': str(e)
        })

    return render(request, 'logon.html', {
        'message': _("Password successfully updated")
    })

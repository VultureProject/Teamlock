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


from teamlock_toolkit.workspace_utils import WorkspaceUtils
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.conf import settings
from random import choice
import logging.config
import string


logging.config.dictConfig(settings.LOG_SETTINGS)
logger = logging.getLogger('workspace')
User = get_user_model()


def check_prev_char(password, char):
    if len(password):
        prev_char = password[len(password) - 1]
        return prev_char in char

    return False


def result(status, error):
    if not status:
        return JsonResponse({
            'status': False,
            'error': error
        })

    return JsonResponse({
        'status': True,
        'data': error
    })


@login_required()
def generatepass(request):
    length = int(request.POST['length'])

    char_set = {
        'chars': string.ascii_lowercase,
    }

    if request.POST.get('number', False) == 'true':
        char_set['number'] = string.digits
    if request.POST.get('symbols', False) == 'true':
        char_set['symbols'] = string.punctuation
    if request.POST.get('uppercase', False) == 'true':
        char_set['uppercase'] = string.ascii_uppercase

    password = []
    while len(password) < length:
        key = choice(list(char_set.keys()))
        a_char = choice(char_set[key])
        if not check_prev_char(password, char_set[key]):
            password.append(a_char)

    return JsonResponse({
        'password': ''.join(password)
    })


@login_required()
def getPassword(request):
    session_key = request.session['key']
    workspace_id = request.POST['workspace_id']
    key_id = request.POST['key_id']
    passphrase = request.POST['passphrase']
    folder_id = request.POST['folder_id']

    workspace_utils = WorkspaceUtils(
        request.user, workspace_id=workspace_id, session_key=session_key
    )

    status, error = workspace_utils.get_password(key_id, folder_id, passphrase)
    return result(status, error)


@login_required()
def moveKey(request):
    session_key = request.session['key']
    workspace_id = request.POST['workspace_id']
    passphrase = request.POST['passphrase']

    key_id = request.POST['key_id']
    folder_from = request.POST['folder_from']
    folder_to = request.POST['folder_to']

    workspace_utils = WorkspaceUtils(
        request.user, workspace_id=workspace_id, session_key=session_key)
    status, error = workspace_utils.move_key(key_id, folder_from, folder_to, passphrase)
    return result(status, error)


@login_required()
def saveKey(request):
    session_key = request.session['key']
    workspace_id = request.POST['workspace_id']
    passphrase = request.POST['passphrase']

    key = {
        "id": request.POST['id'],
        "name": request.POST['name'],
        "login": request.POST['login'],
        "password": request.POST['password'],
        "uri": request.POST['uri'],
        "ipv4": request.POST.get('ipv4'),
        "ipv6": request.POST.get('ipv6'),
        "informations": request.POST['informations'],
        "folder": request.POST['folder'],
    }

    workspace_utils = WorkspaceUtils(
        request.user, workspace_id=workspace_id, session_key=session_key)
    status, error = workspace_utils.save_key(key, passphrase)
    return result(status, error)


@login_required()
def delKey(request):
    session_key = request.session['key']
    key_id = request.POST['key_id']
    folder_id = request.POST['folder_id']
    workspace_id = request.POST['workspace_id']
    passphrase = request.POST['passphrase']

    workspace_utils = WorkspaceUtils(
        request.user, workspace_id=workspace_id, session_key=session_key)
    status, error = workspace_utils.del_key(key_id, folder_id, passphrase)
    return result(status, error)

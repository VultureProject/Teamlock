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
import logging.config


logging.config.dictConfig(settings.LOG_SETTINGS)
logger = logging.getLogger('debug')
User = get_user_model()


def result(status, error, folder=False):
    if not status:
        return JsonResponse({
            'status': False,
            'error': error
        })

    return JsonResponse({
        'status': True,
        'folder': folder
    })


@login_required()
def saveFolder(request):
    session_key = request.session['key']
    workspace_id = request.POST['workspace_id']
    passphrase = request.POST['passphrase']

    folder = {
        "id": request.POST['id'],
        "text": request.POST['text'],
        "icon": request.POST['icon'],
        "parent": request.POST['parent'],
    }

    workspace_utils = WorkspaceUtils(
        request.user, workspace_id=workspace_id, session_key=session_key)
    status, error = workspace_utils.save_folder(folder, passphrase)
    return result(status, error, folder)


@login_required()
def moveFolder(request):
    session_key = request.session['key']
    workspace_id = request.POST['workspace_id']
    passphrase = request.POST['passphrase']
    parent_id = request.POST['parent_id']
    folder_id = request.POST['folder_id']

    workspace_utils = WorkspaceUtils(
        request.user, workspace_id=workspace_id, session_key=session_key)
    status, error = workspace_utils.move_folder(
        folder_id, parent_id, passphrase)
    return result(status, error)


@login_required()
def delFolder(request):
    session_key = request.session['key']
    workspace_id = request.POST['workspace_id']
    passphrase = request.POST['passphrase']
    folder_id = request.POST['folder_id']

    workspace_utils = WorkspaceUtils(
        request.user, workspace_id=workspace_id, session_key=session_key)
    status, error = workspace_utils.del_folder(folder_id, passphrase)
    return result(status, error, folder_id)

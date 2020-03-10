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


from api.decorators.api_auth import api_auth
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from gui.models.workspace import Workspace, Shared
from teamlock_toolkit.workspace_utils import WorkspaceUtils
from django.utils.translation import ugettext as _
import json


@api_auth()
def get_workspaces(request):
    print(request.session.get('key'))
    workspaces = []
    for tmp in Workspace.objects.filter(owner=request.user):
        workspaces.append({
            'id': tmp.pk,
            'name': tmp.name
        })

    for tmp in Shared.objects.filter(user=request.user):
        workspaces.append({
            'id': tmp.workspace.pk,
            'name': tmp.workspace.name
        })

    return JsonResponse({
        'status': True,
        'workspaces': workspaces
    })


@api_auth()
def get_tree_workspace(request):
    passphrase = request.headers['passphrase']
    workspace_id = request.GET.get('workspace_id')

    if not workspace_id:
        return JsonResponse({
            'status': False,
            'error': _("Please define a workspace ID")
        })

    workspace_utils = WorkspaceUtils(
        request.user, workspace_id, session_key=request.session.get('key'))
    status = workspace_utils.get_tree(passphrase)

    if not status['status']:
        return JsonResponse({
            'status': False,
            'error': status['error']
        })

    folders = json.loads(status['folders'])

    rights = 'Read & Write'
    if status['rights'] == 1:
        rights = 'Readonly'

    return JsonResponse({
        'status': True,
        'tree': folders,
        'rights': rights
    })


@api_auth()
def get_keys(request):
    passphrase = request.headers['passphrase']
    workspace_id = request.GET.get('workspace_id')
    folder_id = request.GET.get('folder_id')

    if not workspace_id:
        return JsonResponse({
            'status': False,
            'error': _("Please define a workspace ID")
        })

    if not folder_id:
        return JsonResponse({
            'status': False,
            'error': _("Please define a folder ID")
        })

    workspace_utils = WorkspaceUtils(
        request.user, workspace_id, session_key=request.session.get('key'))
    status = workspace_utils.get_keys(passphrase, folder_id, api=True)

    print(status)

    if not status['status']:
        return JsonResponse({
            'status': False,
            'error': status['error']
        })

    return JsonResponse(status)


@csrf_exempt
@api_auth()
def add_key(request):
    passphrase = request.headers['passphrase']

    session_key = request.session['key']
    workspace_id = request.POST.get('workspace_id')

    key = {
        "id": None,
        "name": request.POST['name'],
        "login": request.POST['login'],
        "password": request.POST['password'],
        "uri": request.POST.get('uri'),
        "ipv4": request.POST.get('ipv4'),
        "ipv6": request.POST.get('ipv6'),
        "informations": request.POST.get('informations', ""),
        "folder": request.POST['folder_id'],
    }

    workspace_utils = WorkspaceUtils(
        request.user, workspace_id=workspace_id, session_key=session_key)
    status, error = workspace_utils.save_key(key, passphrase)

    if not status:
        return JsonResponse({
            'status': False,
            'error': error
        }, status=500)

    return JsonResponse({
        'status': True
    }, status=201)

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
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.http import StreamingHttpResponse
from django.shortcuts import render
from django.utils.translation import ugettext as _
from gui.models.workspace import Shared
from gui.models.workspace import Workspace
from gui.models.history import History
from teamlock_toolkit.crypto_utils import CryptoUtils
from teamlock_toolkit.workspace_utils import WorkspaceUtils

logging.config.dictConfig(settings.LOG_SETTINGS)
logger = logging.getLogger('workspace')
User = get_user_model()


@login_required
def workspace(request):
    if not request.is_ajax() or request.method == "GET":
        return render(request, "workspace.html", {
            'users': User.select2(configure=True, remove_users=[request.user.email]),
        })

    workspaces = []
    for w in Workspace.objects.filter(owner=request.user):
        workspaces.append({
            'id': str(w.pk),
            'text': w.name
        })

    for s in Shared.objects.filter(user=request.user):
        workspaces.append({
            'id': str(s.workspace.pk),
            'text': s.workspace.name,
            'shared': True
        })

    return JsonResponse({
        'workspaces': workspaces,
        'favorite_workspace': request.user.favorite_workspace.pk
    })


@login_required
def passphrase(request):
    workspace_id = request.POST['workspace_id']

    workspace = Workspace.objects.get(pk=workspace_id)
    crypto_utils = CryptoUtils(request.user)
    passphrase = hashlib.sha512(
        request.POST['passphrase'].encode("utf-8")).hexdigest()
    status, error = crypto_utils.rsa_decrypt(workspace.sym_key, passphrase)

    if not status:
        return JsonResponse({
            'status': False,
            'error': error
        })

    request.session['key'] = crypto_utils.generate_sim()
    passphrase = crypto_utils.sym_encrypt(
        passphrase,
        request.session['key']
    )

    if isinstance(passphrase, bytes):
        passphrase = passphrase.decode('utf-8')

    return JsonResponse({
        'status': True,
        'passphrase': passphrase
    })


@login_required
def workspace_create(request):
    name = request.POST['name']

    workspace_utils = WorkspaceUtils(request.user)
    status = workspace_utils.create_workspace(name)

    if not status['status']:
        return JsonResponse({
            'status': False,
            'error': status['error']
        })

    return JsonResponse({
        'status': True,
        'workspace': status['workspace']
    })


@login_required
def workspace_tree(request):
    passphrase = request.POST['passphrase']
    workspace_id = request.POST['workspace_id']

    workspace_utils = WorkspaceUtils(
        request.user, workspace_id, session_key=request.session.get('key'))
    status = workspace_utils.get_tree(passphrase)

    if not status['status']:
        return JsonResponse({
            'status': False,
            'error': status['error']
        })

    return JsonResponse(status)


@login_required
def workspace_keys(request):
    passphrase = request.POST['passphrase']
    workspace_id = request.POST['workspace_id']
    folder_id = request.POST['folder_id']

    workspace_utils = WorkspaceUtils(
        request.user, workspace_id, session_key=request.session.get('key'))
    status = workspace_utils.get_keys(passphrase, folder_id)

    if not status['status']:
        return JsonResponse({
            'status': False,
            'error': status['error']
        })

    return JsonResponse(status)


@login_required
def workspace_search(request):
    passphrase = request.POST['passphrase']
    workspace_id = request.POST['workspace_id']
    search = request.POST['search']

    workspace_utils = WorkspaceUtils(
        request.user, workspace_id, session_key=request.session.get('key'))
    status = workspace_utils.search(passphrase, search)
    return JsonResponse(status)


@login_required
def workspace_delete(request):
    workspace_id = request.POST['workspace_id']
    workspace = Workspace.objects.filter(pk=workspace_id)

    # Share.objects.remove(workspace=workspace)
    workspace.delete()

    return JsonResponse({'status': True})


@login_required
def workspace_share_get(request):
    workspace_id = request.POST['workspace_id']
    workspace = Workspace.objects.get(pk=workspace_id)

    shared = []
    for s in Shared.objects.filter(workspace=workspace).exclude(user=User.objects.get(email="backup@teamlock.io")):
        shared.append(s.to_dict())

    return JsonResponse({
        "iTotalRecords": len(shared),
        "iTotalDisplayRecords": len(shared),
        "aaData": shared
    })


@login_required
def workspace_share(request):
    workspace_id = request.POST['workspace_id']
    passphrase = request.POST['passphrase']

    right = request.POST['right']
    users = json.loads(request.POST['users'])

    workspace_utils = WorkspaceUtils(
        request.user, workspace_id, session_key=request.session.get('key'))

    status = workspace_utils.share_workspace(passphrase, users, [], right)

    if not status['status']:
        return JsonResponse({
            'status': False,
            'error': status['error']
        })

    return JsonResponse(status)


@login_required
def workspace_share_delete(request):
    shared_id = request.POST['shared_id']
    share = Shared.objects.get(pk=shared_id)

    if not share.workspace.owner == request.user:
        return JsonResponse({
            'status': False,
            'error': _("You are not the owner of this workspace")
        })

    share.delete()

    workspace = share.workspace
    History.objects.create(
        user=request.user.email,
        workspace=workspace.name,
        workspace_owner=workspace.owner,
        action="Delete share for user {share.user.email}"
    )

    return JsonResponse({
        'status': True
    })


@login_required
def workspace_export(request):
    workspace_id = request.POST['workspace_id']
    passphrase = request.POST['passphrase']

    workspace_utils = WorkspaceUtils(
        request.user, workspace_id, session_key=request.session.get('key'))

    status = workspace_utils.export_workspace(passphrase)

    if not status['status']:
        return JsonResponse({
            'status': False,
            'error': status['error']
        })

    response = StreamingHttpResponse(streaming_content=status['file'])
    response['Content-Disposition'] = 'attachement; filename="{filename}.kbdx"'.format(filename=workspace_id)
    return response


@login_required
def workspace_import_xml_keepass(request):
    passphrase = request.POST.get('passphrase')
    workspace_id = request.POST['workspace_id']
    file = request.FILES['keepass']

    workspace_utils = WorkspaceUtils(
        request.user, workspace_id, session_key=request.session.get('key')
    )

    status = workspace_utils.import_xml_keepass(passphrase, file)

    if not status['status']:
        return JsonResponse({
            'status': False,
            'error': status['error']
        })

    return JsonResponse({'status': True})


# @login_required
# def workspace_backup(request):
#     passphrase = request.POST.get('passphrase')
#     workspace_id = request.POST['workspace_id']

#     workspace_utils = WorkspaceUtils(
#         request.user, workspace_id, session_key=request.session.get('key')
#     )

#     status, file = workspace_utils.backup(passphrase, from_ui=True)

#     if not status:
#         return JsonResponse({
#             'status': False,
#             'error': file
#         })

#     return JsonResponse({
#         'status': True,
#         'backup': json.dumps(file, indent=4)
#     })

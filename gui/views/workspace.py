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
from django.http import JsonResponse, StreamingHttpResponse
from django.contrib.auth.decorators import login_required
from teamlock_toolkit.crypto_utils import CryptoUtils
from gui.models.workspace import Workspace, Shared
from django.utils.translation import ugettext as _
from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.conf import settings
from gui.models.team import Team
import logging.config
import hashlib
import json

logging.config.dictConfig(settings.LOG_SETTINGS)
logger = logging.getLogger('debug')
User = get_user_model()


@login_required
def workspace(request):
    if not request.is_ajax():
        return render(request, "workspace.html", {
            'users': User.select2(configure=True, remove_users=[request.user.email]),
            'teams': Team.select2()
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
        'workspaces': workspaces
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
    for s in Shared.objects.filter(workspace=workspace):
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
def workspace_import_keepass(request):
    passphrase = request.POST.get('passphrase')
    passphrase_file = request.POST.get('passphrase_file')
    workspace_id = request.POST['workspace_id']
    file = request.FILES['keepass']

    workspace_utils = WorkspaceUtils(
        request.user, workspace_id, session_key=request.session.get('key'))

    status = workspace_utils.import_keepass(passphrase, file, passphrase_file)

    if not status['status']:
        return JsonResponse({
            'status': False,
            'error': status['error']
        })

    return JsonResponse({'status': True})

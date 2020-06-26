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

from django.contrib.auth.decorators import user_passes_test
from django.utils.translation import ugettext as _
from teamlock_toolkit.mail import registration
from django.contrib.auth import get_user_model
from gui.models.workspace import Workspace
from django.http import JsonResponse
from django.shortcuts import render
from gui.forms.user import UserForm
from django.conf import settings
from django.urls import reverse
import logging.config

logging.config.dictConfig(settings.LOG_SETTINGS)
logger = logging.getLogger('django')
User = get_user_model()


@user_passes_test(lambda u: u.is_superuser)
def users(request):
    users = User.objects.all().exclude(email="backup@teamlock.io")
    locked_users = User.objects.filter(is_locked=True).count()
    not_configured_users = User.objects.filter(configure=False).count()
    return render(request, 'users.html', {
        'users': users,
        'locked_users': locked_users,
        'not_configured_users': not_configured_users
    })


@user_passes_test(lambda u: u.is_superuser)
def edit_users(request):
    user_id = request.POST.get('user_id', "")

    if user_id:
        user = User.objects.get(pk=user_id)
    else:
        user = User()

    form = UserForm(instance=user)
    return render(request, 'edit_user.html', {
        'form': form,
        'user_id': user_id
    })


@user_passes_test(lambda u: u.is_superuser)
def save_users(request):
    user_id = request.GET.get('id')
    if user_id:
        user = User.objects.get(pk=user_id)
        form = UserForm(request.POST, instance=user)
    else:
        form = UserForm(request.POST)

    if not form.is_valid():
        return JsonResponse({
            'status': False,
            'error': form.errors
        })

    try:
        user = form.save()

        user.is_superuser = request.POST.get('is_superuser', "") == "on"
        user.save()

        if not user_id:
            configure_uri = settings.PUBLIC_URI + reverse('gui:configure_account', args=(str(user.pk),))
            status, error = registration(configure_uri, user.first_name, user.last_name, user.email)

            logger.info('User {} created'.format(user.email))
        else:
            logger.info('User {} edited'.format(user.email))

    except Exception as e:
        raise
        return JsonResponse({
            'status': False,
            'error': str(e)
        })

    return JsonResponse({
        'status': True,
        'user_id': user_id,
        'user': user.to_dict()
    })


@user_passes_test(lambda u: u.is_superuser)
def get_users_workspaces(request):
    try:
        user_id = request.POST['user_id']
        user = User.objects.get(pk=user_id)

        workspaces = [w.name for w in Workspace.objects.filter(owner=user)]

        return JsonResponse({
            'status': True,
            'workspaces': workspaces
        })
    except Exception as e:
        return JsonResponse({
            'status': False,
            'error': str(e)
        })


@user_passes_test(lambda u: u.is_superuser)
def delete_users(request):
    try:
        user_id = request.POST['user_id']
        user = User.objects.get(pk=user_id)
    except (User.DoesNotExist, KeyError):
        return JsonResponse({
            'status': False,
            'error': _("User not found")
        })

    user.delete()
    return JsonResponse({
        'status': True,
        'success': _("User has been deleted !")
    })


@user_passes_test(lambda u: u.is_superuser)
def lock_user(request):
    try:
        user_id = request.POST['user_id']
        user = User.objects.get(pk=user_id)
    except (User.DoesNotExist, KeyError):
        return JsonResponse({
            'status': False,
            'error': _("User not found")
        })

    user.is_locked = True
    user.save()
    return JsonResponse({
        'status': True,
        'success': _("User has been locked !")
    })


@user_passes_test(lambda u: u.is_superuser)
def unlock_user(request):
    try:
        user_id = request.POST['user_id']
        user = User.objects.get(pk=user_id)
    except (User.DoesNotExist, KeyError):
        return JsonResponse({
            'status': False,
            'error': _("User not found")
        })

    user.is_locked = False
    user.save()
    return JsonResponse({
        'status': True,
        'success': _("User has been unlocked !")
    })


def favorite(request):
    try:
        workspace_id = request.POST['workspace_id']

        workspace = Workspace.objects.get(pk=workspace_id)
        request.user.favorite_workspace = workspace
        request.user.save()

        return JsonResponse({
            "status": True
        })
    
    except Exception as err:
        logger.error(err, exc_info=1)
        return JsonResponse({
            "status": False,
            "error": str(err)
        })

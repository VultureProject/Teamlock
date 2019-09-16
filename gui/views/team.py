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
from django.http import JsonResponse
from django.shortcuts import render
from gui.forms.team import TeamForm
from gui.models.team import Team
from django.conf import settings
import logging.config


logging.config.dictConfig(settings.LOG_SETTINGS)
logger = logging.getLogger('debug')


@user_passes_test(lambda u: u.is_superuser)
def teams(request):
    teams = Team.objects.all()

    return render(request, 'teams.html', {
        'teams': teams
    })


@user_passes_test(lambda u: u.is_superuser)
def edit_teams(request):
    team_id = request.POST.get('team_id', "")

    if team_id:
        team = Team.objects.get(pk=team_id)
        form = TeamForm(instance=team, initial={
            'users': team.users.all()
        })
    else:
        team = Team()
        form = TeamForm(instance=team)

    return render(request, 'edit_team.html', {
        'form': form,
        'team_id': team_id
    })


@user_passes_test(lambda u: u.is_superuser)
def save_teams(request, team_id=None):
    if team_id:
        team = Team.objects.get(pk=team_id)
        form = TeamForm(request.POST, instance=team)
    else:
        form = TeamForm(request.POST)

    if not form.is_valid():
        return JsonResponse({
            'status': False,
            'error': form.errors
        })

    try:
        team = form.save()

    except Exception as e:
        return JsonResponse({
            'status': False,
            'error': e.message
        })

    return JsonResponse({
        'status': True,
        'team_id': team_id,
        'team': team.to_dict()
    })


@user_passes_test(lambda u: u.is_superuser)
def delete_teams(request):
    try:
        team_id = request.POST['team_id']
        team = Team.objects.get(pk=team_id)
    except (Team.DoesNotExist, KeyError):
        return JsonResponse({
            'status': False,
            'error': _('Team not found')
        })

    team.delete()
    return JsonResponse({
        'status': True,
        'success': _('Team has been deleted !')
    })

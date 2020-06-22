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

import json
import datetime

from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.shortcuts import render
from gui.models.history import History


@user_passes_test(lambda u: u.is_superuser)
def history(request):
    if not request.is_ajax():
        workspaces_list = History.objects.values('workspace').distinct()
        users_list = History.objects.values('user').distinct()
        return render(request, 'history.html', {
            "workspaces_list": workspaces_list,
            "users_list": users_list
        })

    order_dir = {
        'asc': "-",
        'desc': ""
    }

    draw = request.GET.get('draw')
    start = request.GET.get("start")
    length = request.GET.get('length', 10)
    columns = json.loads(request.GET['columns'])
    order_0_dir = request.GET.get('order[0][dir]')
    order_0_col = request.GET.get('order[0][column]')

    workspaces = json.loads(request.GET['workspaces'])
    users = json.loads(request.GET['users'])

    start_date = datetime.datetime.strptime(
        request.GET['startDate'].split('+')[0], "%Y-%m-%dT%H:%M:%S"
    )

    end_date = datetime.datetime.strptime(
        request.GET['endDate'].split('+')[0], "%Y-%m-%dT%H:%M:%S"
    )

    query = Q(date__gte=start_date) & Q(date__lte=end_date)

    if workspaces:
        query &= Q(workspace__in=workspaces)
    if users:
        query &= Q(user__in=users)

    order = f"{order_dir[order_0_dir]}{columns[int(order_0_col)]}"

    nb_data = History.objects.filter(query).count()

    data = []
    for f in History.objects.filter(query).order_by(order)[int(start): int(length) + int(start)]:
        data.append(model_to_dict(f))

    return JsonResponse({
        'draw': draw,
        'recordsTotal': nb_data,
        'recordsFiltered': nb_data,
        'data': data
    })

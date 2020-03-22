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

from api.views import auth as api_auth_view
from api.views import main as api_main_view
from api.views import workspace as api_workspace_view
from django.conf.urls import url

urlpatterns = [
    url(r'^version/$', api_main_view.version),
    url(r'^auth/$', api_auth_view.api_auth),
    url(r'^workspace/$', api_workspace_view.get_workspaces),
    url(r'^workspace/tree$', api_workspace_view.get_tree_workspace),
    url(r'^workspace/keys$', api_workspace_view.get_keys),
    url(r'^workspace/keys/add$', api_workspace_view.add_key)
]

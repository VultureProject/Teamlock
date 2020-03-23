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

from django.conf.urls import url
from django.urls import path
from gui.views import auth as auth_view
from gui.views import folder as folder_view
from gui.views import install as install_view
from gui.views import key as key_view
from gui.views import profile as profile_view
from gui.views import settings as settings_view
from gui.views import user as user_view
from gui.views import workspace as workspace_view

urlpatterns = [
    url(r'^$', auth_view.main, name='workspace'),
    url(r'^login/$', auth_view.log_in, name='log_in'),
    url(r'^logout/$', auth_view.log_out, name="log_out"),
    url(r'^recover/', auth_view.recover_passphrase, name="recover_passphrase"),

    url(r'^install/', install_view.install, name="install"),

    url(r'^users/$', user_view.users, name="users"),
    url(r'^users/edit/$', user_view.edit_users, name="user_edit"),
    url(r'^users/save/', user_view.save_users, name="user_save"),
    url(r'^users/save/$', user_view.save_users),

    url(r'^users/workspace/', user_view.get_users_workspaces, name="get_users_workspaces"),
    url(r'^users/delete/$', user_view.delete_users, name="user_delete"),
    url(r'^users/lock/$', user_view.lock_user, name="user_lock"),
    url(r'^users/unlock/$', user_view.unlock_user, name="user_unlock"),


    url(r'^configure/(?P<user_id>[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12})?$',
        auth_view.configure_account, name='configure_account'),

    url(r'^profile/$', profile_view.profile, name="profile"),
    url(r'^profile/update/password', profile_view.update_password, name="update_password"),
    url(r'^profile/recovery_file', profile_view.generate_recovery_view, name="generate_recovery_key"),

    url(r'^settings/(?P<classe_name>[a-z]*)?$', settings_view.settings, name="settings"),

    url(r'^sendmail/test$', settings_view.test_send_mail, name="test_send_mail"),

    url(r'^passphrase/$', workspace_view.passphrase),
    url(r'^workspace/$', workspace_view.workspace, name="workspace"),
    url(r'^workspace/new/$', workspace_view.workspace_create),
    url(r'^workspace/search/$', workspace_view.workspace_search),
    url(r'^workspace/tree/$', workspace_view.workspace_tree),
    url(r'^workspace/keys/$', workspace_view.workspace_keys),
    url(r'^workspace/backup/$', workspace_view.workspace_backup),
    url(r'^workspace/delete/$', workspace_view.workspace_delete),
    url(r'^workspace/share/$', workspace_view.workspace_share),
    url(r'^workspace/share/get/$', workspace_view.workspace_share_get),
    url(r'^workspace/share/delete/$', workspace_view.workspace_share_delete),
    url(r'^workspace/export/$', workspace_view.workspace_export),
    url(r'^workspace/import/$', workspace_view.workspace_import_xml_keepass, name="workspace_import_xml_keepass"),

    # KEYS
    url(r'^generatepass/$', key_view.generatepass),
    url(r'^workspace/movekey/$', key_view.moveKey),
    url(r'^workspace/savekey/$', key_view.saveKey),
    url(r'^workspace/delkey/$', key_view.delKey),
    url(r'^workspace/getpasswd', key_view.getPassword),

    # Folders
    url(r'^workspace/savefolder/$', folder_view.saveFolder),
    url(r'^workspace/movefolder/$', folder_view.moveFolder),
    url(r'^workspace/delfolder/$', folder_view.delFolder),
]
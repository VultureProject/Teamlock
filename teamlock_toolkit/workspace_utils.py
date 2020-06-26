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

import datetime
import django
import json
import logging.config
import uuid
import xml.etree.ElementTree as ET

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.utils.translation import ugettext as _
from gui.models.history import History
from gui.models.workspace import Shared
from gui.models.workspace import Workspace
from teamlock_toolkit.crypto_utils import CryptoUtils


logging.config.dictConfig(settings.LOG_SETTINGS)
logger = logging.getLogger('workspace')
User = get_user_model()


class WorkspaceUtils(CryptoUtils):

    def __init__(self, user, workspace_id=None, session_key=None):
        super().__init__()

        self.workspace = workspace_id
        self.session_key = session_key
        self.user = user
        self.rights = 2
        self.shared = None

        if self.workspace:
            try:
                self.workspace = Workspace.objects.get(pk=workspace_id, owner=user)
            except Workspace.DoesNotExist:
                self.shared = Shared.objects.get(
                    workspace=Workspace.objects.get(pk=workspace_id),
                    user=user
                )

                self.workspace = self.shared.workspace

            if self.user == self.workspace.owner:
                self.sym_key = self.workspace.sym_key
            elif self.shared:
                self.sym_key = self.shared.sym_key
                self.rights = self.shared.right

    def id_generator(self):
        return str(uuid.uuid4())

    def create_workspace(self, name):
        sym_key = self.generate_sim()

        id_one = self.id_generator()
        id_two = self.id_generator()
        id_three = self.id_generator()

        folders = [{
            "id": id_one,
            "text": "Web",
            "icon": "fa fa-globe",
            "parent": "#",
        }, {
            "id": id_two,
            "text": "Servers",
            "icon": "fa fa-server",
            "parent": "#",
        }, {
            "id": id_three,
            "text": "Perso",
            "icon": "fa fa-folder",
            "parent": id_one,
        }]

        encrypted_keys = {
            id_one: self.sym_encrypt(json.dumps([{
                "id": self.id_generator(),
                "name": "Google Account",
                "login": "demo@google.com",
                "password": 'u!Jg>FhJ"H',
                "uri": "https://www.google.fr",
                "ipv4": "",
                "ipv6": "",
                "informations": "",
            }]), sym_key),

            id_two: self.sym_encrypt(json.dumps([{
                "id": self.id_generator(),
                "name": "Proxmox",
                "login": "admin",
                "password": '3A!Su$H`H>M8',
                "uri": "",
                "ipv4": "192.168.1.1",
                "ipv6": "",
                "informations": "",
                "folder": id_two
            }]), sym_key),

            id_three: self.sym_encrypt(json.dumps([]), sym_key)
        }

        encrypted_folders = self.sym_encrypt(json.dumps(folders), sym_key)

        workspace = Workspace(
            name=name,
            sym_key=self.rsa_encrypt(sym_key),
            owner=self.user,
            folders=encrypted_folders,
            keys=encrypted_keys
        )

        try:
            workspace.save()
        except django.db.utils.IntegrityError:
            return {
                'status': False,
                'error': _('Name already exists')
            }

        # Backup user will access the Workspace
        self.workspace = workspace
        self.share_workspace(False, [User.objects.get(email="backup@teamlock.io").pk], [], 3, sym_key, history=False)

        return {
            'status': True,
            'workspace': json.dumps({
                'name': workspace.name,
                'id': str(workspace.pk)
            })
        }
        return True, None

    def get_tree(self, passphrase):
        pwd = self._decrypt_passphrase(passphrase)
        sym_key, error = self.rsa_decrypt(self.sym_key, pwd)
        del passphrase

        if not sym_key:
            return {
                'status': False,
                'error': error
            }

        folders = self.sym_decrypt(self.workspace.folders, sym_key)
        del sym_key

        return {
            'status': True,
            'folders': folders,
            'rights': self.rights
        }

    def get_keys(self, passphrase, folder_id, api=False):
        pwd = self._decrypt_passphrase(passphrase)
        sym_key, error = self.rsa_decrypt(self.sym_key, pwd)
        del passphrase

        if not sym_key:
            return {
                'status': False,
                'error': error
            }

        try:
            keys = []
            for k in json.loads(self.sym_decrypt(self.workspace.keys[folder_id], sym_key)):
                if not api:
                    k['password'] = "***********"

                k['folder'] = folder_id
                keys.append(k)

        except KeyError:
            keys = []

        del sym_key

        return {
            'status': True,
            'keys': keys
        }

    def save_change(self, keys, folder_id, folders, sym_key):
        if keys is not None:
            if folder_id:
                self.workspace.keys[folder_id] = self.sym_encrypt(
                    json.dumps(keys), sym_key)
            elif folder_id:
                self.workspace.keys = keys

        if folders:
            self.workspace.folders = self.sym_encrypt(
                json.dumps(folders), sym_key)

        self.workspace.last_change = datetime.datetime.now()
        self.workspace.save()

    def move_key(self, key_id, folder_from, folder_to, passphrase):
        if self.rights < 2:
            return False, _('You are not allowed to write in this workspace')

        sym_key, error = self.rsa_decrypt(
            self.sym_key, self._decrypt_passphrase(passphrase))

        if not sym_key:
            return False, error

        status, key = self.del_key(key_id, folder_from, passphrase)
        if not status:
            return False, key

        key['id'] = None
        key['folder'] = folder_to
        status, error = self.save_key(key, passphrase)
        return status, error

    def save_key(self, key, passphrase):
        if self.rights < 2:
            return False, _('You are not allowed to write in this workspace')

        sym_key, error = self.rsa_decrypt(
            self.sym_key, self._decrypt_passphrase(passphrase))
        del passphrase

        if not sym_key:
            return False, error

        try:
            keys = json.loads(self.sym_decrypt(
                self.workspace.keys[key['folder']], sym_key))
        except KeyError:
            keys = []

        if not key['id']:
            # insert
            key['id'] = self.id_generator()
            keys.append(key)
            type_save = "Create"
        else:
            # update
            type_save = "Update"
            for i in range(len(keys)):
                if keys[i]['id'] == key['id']:
                    keys[i] = key
                    break

        self.save_change(keys, key['folder'], False, sym_key)

        folders = json.loads(self.sym_decrypt(
            self.workspace.folders, sym_key))

        for folder in folders:
            if folder['id'] == key['folder']:
                History.objects.create(
                    user=self.user.email,
                    workspace=self.workspace.name,
                    workspace_owner=self.workspace.owner,
                    action=f"{type_save} key <b>{key['name']}</b> in folder <b>{folder['text']}</b>"
                )
                break

        del sym_key
        return True, key

    def search(self, passphrase, search):
        sym_key, error = self.rsa_decrypt(
            self.sym_key, self._decrypt_passphrase(passphrase))
        del passphrase

        founded_keys = []
        for folder_id, encrypted_keys in self.workspace.keys.items():
            keys = json.loads(self.sym_decrypt(encrypted_keys, sym_key))
            for key in keys:
                match = False

                name = key['name'] if key['name'] else ""
                login = key['login'] if key['login'] else ""
                uri = key['uri'] if key['uri'] else ""

                if search.lower() in name.lower():
                    match = True
                elif search.lower() in str(login).lower():
                    match = True
                elif search.lower() in str(uri).lower():
                    match = True

                if match:
                    key['password'] = "***********"
                    key['folder'] = folder_id
                    founded_keys.append(key)

        return {
            'status': True,
            "founded_keys": founded_keys
        }

    def get_password(self, key_id, folder_id, passphrase):
        sym_key, error = self.rsa_decrypt(
            self.sym_key, self._decrypt_passphrase(passphrase))
        del passphrase

        if not sym_key:
            return False, error

        keys = json.loads(self.sym_decrypt(
            self.workspace.keys[folder_id], sym_key))
        folders = json.loads(
            self.sym_decrypt(self.workspace.folders, sym_key))

        del sym_key

        for i in range(len(keys)):
            if keys[i]['id'] == key_id:
                for folder in folders:
                    if folder['id'] == folder_id:
                        action = f"Retreive password for key <b>{keys[i]['name']}</b> in folder <b>{folder['text']}</b>"
                        History.objects.create(
                            user=self.user.email,
                            workspace=self.workspace.name,
                            workspace_owner=self.workspace.owner,
                            action=action
                        )
                        break

                return True, keys[i]['password']

        return False, _('Key not found')

    def del_key(self, key_id, folder_id, passphrase):
        if self.rights < 2:
            return False, _('You are not allowed to delete a key in this Workspace')

        sym_key, error = self.rsa_decrypt(
            self.sym_key, self._decrypt_passphrase(passphrase))
        del passphrase

        if not sym_key:
            return False, error

        keys = json.loads(self.sym_decrypt(
            self.workspace.keys[folder_id], sym_key))
        folders = json.loads(
            self.sym_decrypt(self.workspace.folders, sym_key))

        tmp_key = None
        for i in range(len(keys)):
            if keys[i]['id'] == key_id:
                tmp_key = keys[i]
                del (keys[i])
                break

        if tmp_key is None:
            return False, _('Key not found')

        for folder in folders:
            if folder['id'] == folder_id:
                History.objects.create(
                    user=self.user.email,
                    workspace=self.workspace.name,
                    workspace_owner=self.workspace.owner,
                    action=f"Delete key <b>{tmp_key['name']}</b> in folder <b>{folder['text']}</b>"
                )
                break

        self.save_change(keys, folder_id, False, sym_key)
        del sym_key
        return True, tmp_key

    def save_folder(self, folder, passphrase):
        if self.rights < 2:
            return False, _('You are not allowed to create a folder in this Workspace')

        sym_key, error = self.rsa_decrypt(
            self.sym_key, self._decrypt_passphrase(passphrase))
        del passphrase

        if not sym_key:
            return False, error

        folders = json.loads(self.sym_decrypt(self.workspace.folders, sym_key))
        if not folder['id']:
            # Insert
            folder['id'] = self.id_generator()
            folders.append(folder)

            History.objects.create(
                user=self.user.email,
                workspace=self.workspace.name,
                workspace_owner=self.workspace.owner,
                action=f"Create folder {folder['text']}"
            )
        else:
            # Update
            for i in range(len(folders)):
                if folders[i]['id'] == folder['id']:
                    folders[i] = folder
                    History.objects.create(
                        user=self.user.email,
                        workspace=self.workspace.name,
                        workspace_owner=self.workspace.owner,
                        action=f"Update folder {folder['text']}"
                    )
                    break

        self.save_change(None, False, folders, sym_key)
        del sym_key
        return True, folder['id']

    def move_folder(self, folder_id, parent_id, passphrase):
        if self.rights < 2:
            return False, _('You are not allowed to move a folder in this Workspace')

        sym_key, error = self.rsa_decrypt(
            self.sym_key, self._decrypt_passphrase(passphrase))
        del passphrase

        if not sym_key:
            return False, error

        folders = json.loads(self.sym_decrypt(self.workspace.folders, sym_key))
        for folder in folders:
            if folder['id'] == folder_id:
                folder['parent'] = parent_id

        self.save_change(None, False, folders, sym_key)
        del sym_key
        return True, None

    def del_folder(self, folder_id, passphrase):
        if self.rights < 2:
            return False, _('You are not allowed to delete a key in this Workspace')

        sym_key, error = self.rsa_decrypt(
            self.sym_key, self._decrypt_passphrase(passphrase))
        del passphrase

        if not sym_key:
            return False, error

        folders = json.loads(self.sym_decrypt(self.workspace.folders, sym_key))

        new_folders = []
        folders_to_del = []
        folder_deleted_name = []

        for folder in folders:
            if folder['id'] == folder_id:
                folders_to_del.append(folder['id'])
                folder_deleted_name.append(folder['text'])
            elif folder['parent'] == folder_id:
                folders_to_del.append(folder['id'])
                folder_deleted_name.append(folder['text'])
            else:
                new_folders.append(folder)

        keys = {}
        nb_deleted_keys = 0
        for x, y in self.workspace.keys.items():
            if x not in folders_to_del:
                keys[x] = y
            else:
                nb_deleted_keys += len(json.loads(self.sym_decrypt(y, sym_key)))

        History.objects.create(
            user=self.user.email,
            workspace=self.workspace.name,
            workspace_owner=self.workspace.owner,
            action=f"Delete folder <b>{folder_deleted_name}</b> with <b>{nb_deleted_keys}</b> keys",
        )

        self.save_change(keys, False, new_folders, sym_key)
        del sym_key
        return True, None

    def share_workspace(self, passphrase, users, teams, rights, sym_key=False, history=True):
        if self.rights < 2:
            return {
                'status': False,
                'error': _('You are not allowed to share this this workspace')
            }

        if sym_key is False:
            pwd = self._decrypt_passphrase(passphrase)
            sym_key, error = self.rsa_decrypt(self.sym_key, pwd)
            del passphrase

            if not sym_key:
                return {
                    'status': False,
                    'error': error
                }

        users_email = []
        for user_id in users:
            user = User.objects.get(pk=user_id)
            users_email.append(user.email)

            try:
                sym_key = sym_key.decode('utf-8')
            except AttributeError:
                pass

            encrypted_sym_key = self.rsa_encrypt(sym_key, user.public_key)

            try:
                Shared.objects.create(
                    sym_key=encrypted_sym_key,
                    right=rights,
                    user=user,
                    workspace=self.workspace
                )
            except IntegrityError:
                pass

            del encrypted_sym_key

        mapping_right = {
            1: 'Read',
            2: "Read & Write",
            "1": "Read",
            "2": "Read & Write"
        }

        if history:
            action = f"Shared workspace with user(s) <b>{', '.join(users_email)}</b> with <b>{mapping_right[rights]}</b> rights"
            History.objects.create(
                user=self.user.email,
                workspace=self.workspace.name,
                workspace_owner=self.workspace.owner,
                action=action
            )

        del sym_key
        return {
            'status': True
        }

    def export_workspace(self, passphrase):
        if self.rights < 2:
            return {
                "status": False,
                "error": _('You are not allowed to export this workspace')
            }

        sym_key, error = self.rsa_decrypt(
            self.sym_key, self._decrypt_passphrase(passphrase))
        del passphrase

        if not sym_key:
            return False, error

        return {
            "status": False,
            'error': 'BONSOIR'
        }

    def find_group(self, sym_key, group, group_mapping, folders, parent="Racine"):
        key_mapping = {
            'Password': 'password',
            'Title': 'name',
            'URL': 'uri',
            'UserName': 'login',
            'Notes': 'informations'
        }

        for subgroup in group.findall('Group'):
            group_name = subgroup.find('Name').text
            pk_folder = self.id_generator()

            group_mapping[group_name] = pk_folder

            folders.append({
                'id': pk_folder,
                'text': group_name,
                'icon': 'fa fa-folder',
                'parent': group_mapping[parent]
            })

            keys = []
            for entry in subgroup.findall('Entry'):
                pk_entry = self.id_generator()
                tmp = {
                    "id": pk_entry
                }

                for entry_value in entry.findall('String'):
                    key = entry_value.find('Key').text
                    value = entry_value.find('Value').text

                    if key in ('Notes', 'Password', 'Title', 'URL', 'UserName'):
                        tmp[key_mapping[key]] = value

                keys.append(tmp)

            self.save_change(keys, pk_folder, False, sym_key)
            self.find_group(sym_key, subgroup, group_mapping, folders, group_name)

    def import_xml_keepass(self, passphrase, file):
        if self.rights < 2:
            return {
                "status": False,
                "error": _('You are not allowed to export this workspace')
            }

        sym_key, error = self.rsa_decrypt(
            self.sym_key, self._decrypt_passphrase(passphrase))
        del passphrase

        if not sym_key:
            return {
                "status": False,
                "error": error
            }

        content = file.read()
        folders = []
        group_mapping = {
            "Racine": "#"
        }

        try:
            xml_file = ET.fromstring(content)
            racine = xml_file.find('Root').find('Group')

            self.find_group(sym_key, racine, group_mapping, folders)
            self.save_change(False, False, folders, sym_key)

        except Exception as e:
            logger.critical(e, exc_info=1)
            return {
                'status': False,
                'error': str(e)
            }

        return {
            "status": True
        }

    def backup(self, passphrase, from_ui=False):
        if from_ui:
            passphrase = self._decrypt_passphrase(passphrase)

        sym_key, error = self.rsa_decrypt(self.sym_key, passphrase)
        del passphrase

        if not sym_key:
            return False, error

        def get_keys(folder_id):
            return json.loads(self.sym_decrypt(self.workspace.keys[folder_id], sym_key))

        def find_child(folders, folder_id):
            childs = []
            for tmp in folders:
                if tmp['parent'] == folder_id:
                    childs.append({
                        "id": tmp['id'],
                        "name": tmp['text'],
                        "childs": find_child(folders, tmp['id']),
                        "keys": get_keys(tmp['id'])
                    })

            return childs

        folders = []
        tmp_folders = json.loads(self.sym_decrypt(self.workspace.folders, sym_key))
        for tmp in tmp_folders:
            if tmp['parent'] == "#":
                tmp_folder = {
                    "id": tmp['id'],
                    "name": tmp['text'],
                    "childs": find_child(tmp_folders, tmp['id']),
                    "keys": get_keys(tmp['id'])
                }

                folders.append(tmp_folder)

        return True, folders

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

import logging

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils.translation import ugettext as _
from teamlock_toolkit.crypto_utils import CryptoUtils
from teamlock_toolkit.managers import UserManager
from uuid import uuid4

logging.config.dictConfig(settings.LOG_SETTINGS)
logger = logging.getLogger('gui')


class TeamlockUser(AbstractBaseUser, PermissionsMixin):
    _id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=100, unique=True)
    last_change_passwd = models.DateField(blank=False, null=True)
    last_password = models.CharField(max_length=255, null=True)
    private_key = models.TextField(null=True)
    public_key = models.TextField(null=True)
    recovery_passphrase = models.TextField(null=True)
    configure = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return "{}".format(self.email)

    def to_dict(self):
        return {
            'id': str(self._id),
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'configure': self.configure,
            'is_locked': self.is_locked,
            'is_superuser': self.is_superuser
        }

    def generate_keys(self, passphrase):
        crypto = CryptoUtils()
        crypto.generate_rsa(passphrase)

        self.public_key = crypto.pubkey
        self.private_key = crypto.privkey

    @staticmethod
    def select2(configure=True, remove_users=[]):
        users = []

        remove_users.append('backup@teamlock.io')
        for tmp_user in TeamlockUser.objects.filter(configure=configure).exclude(email__in=remove_users):
            users.append({
                'id': str(tmp_user.pk),
                'name': str(tmp_user)
            })

        return users

    def generate_recovery_key(self, passphrase, session_key):
        try:
            crypto_utils = CryptoUtils(self)
            encrypted_passphrase, sym_key = crypto_utils.generate_recovery_symkey(
                passphrase,
                session_key=session_key
            )

            self.recovery_passphrase = encrypted_passphrase
            self.save()

            return {
                'status': True,
                'data': sym_key,
                'filename': "recovery_{}.txt".format(str(self.pk))
            }

        except Exception as e:
            logger.error(e, exc_info=1)
            return {
                'status': False,
                'error': _('An error has occured')
            }

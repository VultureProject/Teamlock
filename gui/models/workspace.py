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


from djongo.models import json as django_json
from django.utils import timezone
from django.conf import settings
from djongo import models


class Workspace(models.Model):
    _id = models.ObjectIdField()
    name = models.TextField()
    sym_key = models.TextField()
    date_creation = models.DateTimeField(default=timezone.now)
    last_change = models.DateTimeField(default=timezone.now)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    folders = models.TextField()
    keys = django_json.JSONField()

    def __str__(self):
        return "{} - {}".format(self.name, self.owner)

    class Meta:
        unique_together = ('name', 'owner')


class Shared(models.Model):
    """
        sym_key: Symetric key used to encrypt all workspace.
        The symkey is encrypted with the public key of the user

        right: 1: read; 2: read+right; 3: read+right+delete
    """
    _id = models.ObjectIdField()
    sym_key = models.TextField()
    right = models.IntegerField(default=1)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('workspace', 'user')

    def to_dict(self):
        return {
            "pk": str(self.pk),
            "right": self.right,
            "user": self.user.email
        }

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

from django.conf import settings
from djongo import models


class Mobile(models.Model):
    _id = models.ObjectIdField()
    name = models.TextField()
    type_mobile = models.TextField()
    key = models.TextField()
    activated = models.BooleanField(default=False)
    join = models.DateField(null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("name", "user")

    def to_dict(self):
        type_m = {
            'android': "<i class='fa fa-android'></i>",
            'ios': "<i class='fa fa-apple'></i>",
            'desktop': "<i class='fa fa-desktop'></i>",
            'console': "<i class='fa fa-terminal'></i>",
        }

        tmp = {
            'name': self.name,
            'key': self.key if not self.activated else "-",
            'join': "",
            'type_mobile': type_m[self.type_mobile],
            'activated': "<i class='fa fa-times'></i>",
            'action': "<button href='#' class='btn btn-xs btn-flat btn-danger action' data-id='{}' data-action='delete'><i class='fa fa-trash'></i></button>".format(str(self.pk))
        }

        if self.activated:
            tmp['activated'] = "<i class='fa fa-check'></i>"

        try:
            tmp['join'] = self.join.strftime('%d/%m/%Y')
        except Exception:
            pass

        return tmp

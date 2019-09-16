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

from django.contrib.auth.hashers import check_password
from django.contrib.auth import get_user_model


class AuthenticationBackend:

    def authenticate(self, request, username=None, password=None):
        try:
            user = get_user_model().objects.get(email=username)

            if check_password(password, user.password):
                return user
        except get_user_model().DoesNotExist:
            pass

        return None

    def get_user(self, user_id):
        try:
            return get_user_model().objects.get(pk=user_id)
        except get_user_model().DoesNotExist:
            return None


# class TeamlockAuthenticationBackend(LDAPBackend):

#     def authenticate(self, request, email=None, password=None):
#             """ Overrides LDAPBackend.authenticate to save user password in django """

#             print(email)
#             print(password)
#             print('okokokok')
#             user = LDAPBackend.authenticate(self, email, password)
#             print(user)

#             # If user has successfully logged, save his password in django database
#             if user:
#                 user.set_password(password)
#                 user.save()

#             return user

#!/usr/bin/env python

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

from django.forms import (ModelForm, CharField, EmailField,
                          TextInput, EmailInput, BooleanField, CheckboxInput)
from django.utils.translation import gettext as _
from django.contrib.auth import get_user_model


class UserForm(ModelForm):
    first_name = CharField(
        label=_("First name"),
        widget=TextInput(attrs={'class': 'form-control'})
    )

    last_name = CharField(
        label=_("Last name"),
        widget=TextInput(attrs={'class': 'form-control'})
    )

    email = EmailField(
        label=_("Email"),
        widget=EmailInput(attrs={'class': 'form-control'})
    )

    is_superuser = BooleanField(
        label=_("Staff"),
        widget=CheckboxInput(
            attrs={'class': 'js-switch'}),
        required=False
    )

    class Meta:
        model = get_user_model()
        fields = ('first_name', 'last_name', 'email', 'is_superuser')

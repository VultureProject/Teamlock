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

from django.forms import ModelForm, CharField, TextInput, IntegerField, NumberInput
from gui.models.settings import GeneralSettings, SecuritySettings, MailSettings
from django.utils.translation import ugettext as _


class GeneralSettingsForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['company_name'] = CharField(
            label=_("Company name"),
            widget=TextInput(attrs={'class': 'form-control'})
        )

    class Meta:
        model = GeneralSettings
        fields = ('company_name',)


class SecuritySettingsForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['password_change'] = IntegerField(
            label=_("Duration of user password in days"),
            widget=NumberInput(attrs={'class': 'form-control', 'min': 1})
        )
        self.fields['length_password'] = IntegerField(
            label=_("Length of user password"),
            widget=NumberInput(attrs={'class': 'form-control', 'min': 0})
        )
        self.fields['key_size'] = IntegerField(
            label=_("Length of RSA key"),
            widget=NumberInput(attrs={'class': 'form-control', 'min': 2048})
        )

    class Meta:
        model = SecuritySettings
        fields = ('password_change', 'length_password', 'key_size')


class MailSettingsForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["host"] = CharField(
            label=_("SMTP Host"),
            widget=TextInput(attrs={'class': 'form-control'})
        )

    class Meta:
        model = MailSettings
        fields = ('host',)

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

from django.forms import (ModelForm, CharField, Select, TextInput, ChoiceField)
from django.utils.translation import ugettext as _
from gui.models.mobile import Mobile


class MobileForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(MobileForm, self).__init__(*args, **kwargs)
        type_mobile_choices = (('android', 'Android'), ('ios', 'iOS'),
                               ('desktop', 'Desktop'), ('console', 'Console'))

        self.fields['name'] = CharField(label=_("Mobile name"),
                                        widget=TextInput(
                                            attrs={'class': 'form-control'}))

        self.fields['type_mobile'] = ChoiceField(required=True,
                                                 label=_("Mobile type"),
                                                 choices=type_mobile_choices,
                                                 widget=Select(
                                                     attrs={
                                                         'class': 'form-control select2'
                                                     }))

    class Meta:
        model = Mobile
        fields = ('name', 'type_mobile')

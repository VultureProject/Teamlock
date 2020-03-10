#!/home/vlt-os/env/bin/python
"""This file is part of Vulture OS.

Vulture OS is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Vulture OS is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Vulture OS.  If not, see http://www.gnu.org/licenses/.
"""
__author__ = "Kevin GUILLEMOT"
__credits__ = []
__license__ = "GPLv3"
__version__ = "4.0.0"
__maintainer__ = "Vulture OS"
__email__ = "contact@vultureproject.org"
__doc__ = 'Frontends API'


import redis
import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponseForbidden
from django.http import JsonResponse
from django.utils.translation import ugettext as _


def api_auth():

    def decorator(func):
        def inner(request, *args, **kwargs):
            jwt = request.headers.get('Authorization')
            if jwt:
                redis_client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

                token = redis_client.get(f'jwt_token_{jwt}')
                if not token:
                    return HttpResponseForbidden()

            request.user = get_user_model().objects.get(pk=uuid.UUID(token.decode('utf-8')))

            if not request.headers.get('passphrase'):
                return JsonResponse({
                    'status': False,
                    'error': _("Please define encrypted passphrase in headers")
                })

            return func(request, *args, **kwargs)

        return inner

    return decorator

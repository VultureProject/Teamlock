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

import redis
import datetime
import hashlib
import logging
import logging.config

from django.conf import settings
from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt
from teamlock_toolkit.crypto_utils import CryptoUtils

logging.config.dictConfig(settings.LOG_SETTINGS)
logger = logging.getLogger('auth')


@csrf_exempt
def api_auth(request):
    try:
        email = request.POST['email']
        password = request.POST['password']
    except KeyError:
        return JsonResponse({
            'status': False,
            'error': _("Please provide email & password to authenticate")
        }, status=400)

    user = authenticate(username=email, password=password)

    if user:
        crypto_utils = CryptoUtils(user)
        request.session['key'] = crypto_utils.generate_sim()
        passphrase = hashlib.sha512(password.encode()).hexdigest()
        passphrase = crypto_utils.sym_encrypt(passphrase, request.session['key'])

        logger.info("User {} successfully authenticated".format(
            user.email
        ))

        token = get_random_string(length=200)

        redis_client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

        redis_client.setex(f'jwt_token_{token}', 300, str(user.pk))
        expiration = datetime.datetime.utcnow() + datetime.timedelta(seconds=settings.JWT_EXPIRATION)

        return JsonResponse({
            'status': True,
            'token': token,
            'passphrase': passphrase,
            'expireAt': expiration.isoformat()
        })

    logger.info('User {} failed to authenticate'.format(email))
    return JsonResponse({
        'status': False,
        'error': _("Authentication failed")
    }, status=401)

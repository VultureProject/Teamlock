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

from email.mime.multipart import MIMEMultipart
from gui.models.settings import MailSettings
from email.mime.text import MIMEText
from django.conf import settings
import smtplib
import logging

logging.config.dictConfig(settings.LOG_SETTINGS)
logger = logging.getLogger('auth')


def send_mail_test(config):
    try:
        server = smtplib.SMTP(config['host'])
        server.set_debuglevel(settings.DEBUG)
        server.ehlo()

        msg = MIMEMultipart()
        msg['From'] = "test.teamlock.io"
        msg['To'] = config['to']
        msg['Subject'] = "TeamLock: Test message"

        body = "This is a test message from Teamlock"
        msg.attach(MIMEText(body, 'plain', _charset="UTF-8"))

        server.sendmail("test.teamlock.io", config['to'], msg.as_string())
        server.quit()
    except Exception as e:
        logger.error(e)
        return False, str(e)

    return True, None


def send_mail(to, message, subject="Teamlock"):
    try:
        config = MailSettings.objects.get()

        server = smtplib.SMTP(config.host)
        server.set_debuglevel(settings.DEBUG)
        server.ehlo()

        msg = MIMEMultipart()
        msg['From'] = "contact.teamlock.io"
        msg['To'] = to
        msg['Subject'] = subject

        message = MIMEText(message, 'html')
        msg.attach(message)

        server.sendmail("contact.teamlock.io", to, msg.as_string())
        server.quit()
    except Exception as e:
        logger.error(e)
        return False, str(e)

    return True, None


def registration(uri, first_name, last_name, email):
    message = """Hi {first} {last},<br/><br/>
You have been added into a TeamLock configuration.<br/>
Please follow this link to configure your account:
<a href='{uri}'>{uri}</a>""".format(first=first_name, last=last_name, uri=uri)

    if settings.DEV_MODE:
        print(message)
        return True, None

    return send_mail(email, message, subject="Teamlock registration")

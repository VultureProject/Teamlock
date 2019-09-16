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
along with Teamlock.  If not, see <http://www.gnu.org/licenses/>.
"""

__author__ = "Olivier de Régis"
__credits__ = []
__license__ = "GPLv3"
__version__ = "3.0.0"
__maintainer__ = "Teamlock Project"
__email__ = "contact@teamlock.io"
__doc__ = ''

from django.utils.translation import ugettext as _
from gui.models.settings import SecuritySettings
from Crypto.Cipher import PKCS1_OAEP
from django.conf import settings
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto.Hash import MD5
from Crypto import Random
import logging.config
import base64
import logging
import time

logging.config.dictConfig(settings.LOG_SETTINGS)
logger = logging.getLogger('debug')


def timeme(func):
    def wrapper(*args, **kw):
        logging.config.dictConfig(settings.LOG_SETTINGS)
        logger = logging.getLogger('project')

        startTime = int(round(time.time() * 1000))
        result = func(*args, **kw)
        endTime = int(round(time.time() * 1000))

        ftime = endTime - startTime
        if func.__name__ == "decrypt_file":
            logger.info("Decryption {}ms".format(ftime), extra={
                        'type': 'time_decrypt', 'ftime': ftime})
        elif func.__name__ == 'encrypt_file':
            logger.info("Encryption {}ms".format(ftime), extra={
                        'type': 'time_encrypt', 'ftime': ftime})

        return result

    return wrapper


class CryptoUtils:

    def __init__(self, user=None):
        """Initialize crypto class

        Args:
            user (None, optional): User of the django request
        """
        self.random_gen = Random.new().read
        self.user = user
        self.bs = 32

        try:
            self.settings = SecuritySettings.objects.get()
        except SecuritySettings.DoesNotExist:
            self.settings = SecuritySettings()

    def _decrypt_passphrase(self, passphrase, session_key=None):
        """Decrypt passphrase

        Args:
            passphrase (str): Passphrase of the user
            session_key (None, optional): Session key used
            to encrypt passphrase

        Returns:
            TYPE: decrypted passphrase
        """
        if not session_key:
            session_key = self.session_key

        passphrase = self.sym_decrypt(passphrase, session_key)
        return passphrase

    def generate_recovery_symkey(self, passphrase, session_key):
        pwd = self._decrypt_passphrase(passphrase, session_key=session_key)

        sym_key = self.generate_sim()
        encrypted_passphrase = self.sym_encrypt(pwd, sym_key)
        return encrypted_passphrase, base64.b64encode(bytes(sym_key, 'utf-8')).decode('utf-8')

    def generate_rsa(self, passphrase=None):
        """Generate RSA Private & Public key

        Args:
            passphrase (None, optional): Passphrase for RSA Private key
        """
        self.key = RSA.generate(self.settings.key_size, self.random_gen)
        self.pubkey = self.key.publickey().exportKey().decode('utf-8')

        if passphrase:
            self.privkey = self.key.exportKey(
                passphrase=passphrase).decode('utf-8')
        else:
            self.privkey = self.key.exportKey().decode('utf-8')

    def generate_sim(self):
        """Generate symetric key
        """
        return MD5.new().hexdigest()

    def rsa_encrypt(self, message, public_key=None):
        """
        Args:
            message (TYPE): message to encrypt

        Returns:
            encrypted message

        Deleted Parameters:
            rsa_pubkey (TYPE): RSA Public key
        """

        if not public_key:
            public_key = self.user.public_key

        rsa = RSA.importKey(public_key)
        pkc = PKCS1_OAEP.new(rsa)
        x = pkc.encrypt(bytes(message, 'utf-8'))
        m = base64.b64encode(x)
        return m.decode('utf-8')

    def rsa_decrypt(self, message, passphrase):
        """Decrypt message with a RSA Private Key and passphrase

        Args:
            message (TYPE): message to decrypt
            passphrase (TYPE): passphrase for the Private key

        Returns:
            Message decrypted, or error

        Deleted Parameters:
            rsa_privkey (m): RSA Private key
        """
        try:
            rsa = RSA.importKey(self.user.private_key, passphrase=passphrase)
            pkc = PKCS1_OAEP.new(rsa)
            return pkc.decrypt(base64.b64decode(message)), None
        except ValueError:
            return False, _("Invalid passphrase")

    # def _pad(self, s):
    #     return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s) - 1:])]

    def sym_encrypt(self, message, sym_key):
        """Symetric encryption

        Args:
            message (str): Message to encrypt
            sym_key (str): Key for encryption

        Returns:
            str: Encrypted message
        """
        pad = lambda s: bytes(s + (16 - len(s) % 16) * chr(16 - len(s) % 16), encoding='utf8')

        message = pad(message)
        iv = Random.new().read(AES.block_size)

        if not isinstance(sym_key, bytes):
            sym_key = sym_key.encode('utf-8')

        cipher = AES.new(sym_key, AES.MODE_CBC, iv)

        x = base64.b64encode(iv + cipher.encrypt(message))

        if isinstance(x, bytes):
            return x.decode('utf-8')

        return x

    def sym_decrypt(self, message, sym_key):
        """Symetric decryption

        Args:
            message (str): Message to decrypt
            sym_key (str): Key for decryption

        Returns:
            str: Decrypted message
        """
        # unpad = lambda s: s[0:-ord(s[-1])]

        message = base64.b64decode(message)
        iv = message[:AES.block_size]

        if not isinstance(sym_key, bytes):
            sym_key = sym_key.encode('utf-8')

        cipher = AES.new(sym_key, AES.MODE_CBC, iv)

        text = self._unpad(cipher.decrypt(message[AES.block_size:]))
        return text.decode('utf-8')

    def update_user_key(self, user, oldpassphrase, passphrase):
        """Reencrypt all the symetric key for an User with the new passphrase

        Args:
            user (TYPE): Description
            oldpassphrase (TYPE): Description
            passphrase (TYPE): Description
        """

        objects_to_reencrypt = {
            "Workspace": {},
            "Shared": {},
        }

        for obj in objects_to_reencrypt.keys():
            for temp in obj.objects.filter(user=user):
                decrypted_key, error = self.rsa_decrypt(
                    temp.sym_key, oldpassphrase)

                if not decrypted_key:
                    return False, error

                objects_to_reencrypt[obj][temp] = decrypted_key

        user.generate_keys(passphrase)
        user.save()

        for obj, value in objects_to_reencrypt.items():
            for temp, decrypted_key in value.items():
                temp.sym_key = self.rsa_encrypt(decrypted_key)
                temp.save()

        logger.info(
            "User {} changed his private key".format(user.email.upper()))
        return True, None

#!/usr/bin/env python

from teamlock_toolkit.crypto_utils import CryptoUtils
import datetime


def update_password_toolkit(user, workspaces, shares, passphrase, new_passphrase, new_password):
    old_sym_keys = []

    crypto_utils = CryptoUtils(user)
    for workspace in workspaces:
        sym_key, error = crypto_utils.rsa_decrypt(workspace.sym_key, passphrase)
        if not sym_key:
            raise Exception(error)

        old_sym_keys.append({
            'workspace': workspace,
            'sym_key': sym_key
        })

    for share in shares:
        sym_key, error = crypto_utils.rsa_decrypt(share.sym_key, passphrase)
        if not sym_key:
            raise Exception(error)

        old_sym_keys.append({
            'share': share,
            'sym_key': sym_key
        })

    user.generate_keys(new_passphrase)
    user.set_password(new_password)
    user.last_change_passwd = datetime.datetime.now()
    user.save()

    crypto_utils = CryptoUtils(user)
    for keys in old_sym_keys:
        try:
            obj = keys['workspace']
        except KeyError:
            obj = keys['share']

        sym_key = keys['sym_key']

        encrypted_sym_key = crypto_utils.rsa_encrypt(sym_key.decode('utf-8'))
        obj.sym_key = encrypted_sym_key
        obj.save()

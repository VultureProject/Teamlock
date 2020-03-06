#!/usr/bin/env python

from django.contrib.auth import authenticate
from gui.models.workspace import Shared
from teamlock_toolkit.workspace_utils import WorkspaceUtils

import hashlib
import os.path


def backup_workspaces(password, path="/var/tmp/"):
    email = "backup@teamlock.io"
    user = authenticate(username=email, password=password)

    if not user:
        raise Exception("Invalid backup password")

    for shared in Shared.objects.filter(user=user):
        workspace_utils = WorkspaceUtils(user, workspace_id=shared.workspace.pk)

        status, file = workspace_utils.backup(
            hashlib.sha512(password.encode()).hexdigest())

        if status:
            filename = f"backup_workspace_{shared}.json"
            with open(os.path.join(path, filename), 'w') as f:
                f.write(file)

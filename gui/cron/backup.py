#!/usr/bin/env python

from django.contrib.auth import authenticate
from gui.models.workspace import Shared
from teamlock_toolkit.workspace_utils import WorkspaceUtils

import hashlib


def backup_workspaces(password):
    email = "backup@teamlock.io"
    user = authenticate(username=email, password=password)

    if not user:
        raise Exception("Invalid backup password")

    for shared in Shared.objects.all():
        workspace_utils = WorkspaceUtils(user, workspace_id=shared.workspace.pk)

        workspace_utils.export_xml_keepass(
            hashlib.sha512(password.encode()).hexdigest())

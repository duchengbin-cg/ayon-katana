# -*- coding: utf-8 -*-
"""Pipeline tools for AYON Katana integration.

This is intentionally a minimal first iteration focused on:
- registering AYON host (install_host)
- registering create/publish plugin paths
- providing workfile operations for `.katana` files
"""

from __future__ import annotations

import logging
import os

import pyblish.api

from ayon_core.host import HostBase, IWorkfileHost, IPublishHost
from ayon_core.pipeline import (
    register_creator_plugin_path,
    register_workfile_build_plugin_path,
)

from ayon_katana import KATANA_ADDON_DIR

log = logging.getLogger("ayon_katana")

PLUGINS_DIR = os.path.join(KATANA_ADDON_DIR, "plugins")
PUBLISH_PATH = os.path.join(PLUGINS_DIR, "publish")
CREATE_PATH = os.path.join(PLUGINS_DIR, "create")
WORKFILE_BUILD_PATH = os.path.join(PLUGINS_DIR, "workfile_build")


def _is_katana_available() -> bool:
    try:
        import Katana  # noqa: F401
        return True
    except Exception:
        return False


class KatanaHost(HostBase, IWorkfileHost, IPublishHost):
    name = "katana"

    def get_app_information(self):
        from ayon_core.host import ApplicationInformation

        if not _is_katana_available():
            return ApplicationInformation(app_name="Katana", app_version="N/A")

        from Katana import Configuration  # type: ignore

        release = None
        try:
            release = Configuration.get("KATANA_RELEASE")
        except Exception:
            # Older versions may not have this available via Configuration.get
            pass

        return ApplicationInformation(
            app_name="Katana",
            app_version=release or "Unknown",
        )

    def install(self):
        # Pyblish host registration
        pyblish.api.register_host("katana")

        # Register plugin paths
        pyblish.api.register_plugin_path(PUBLISH_PATH)
        register_creator_plugin_path(CREATE_PATH)
        register_workfile_build_plugin_path(WORKFILE_BUILD_PATH)

        log.info("AYON Katana host installed.")

    # --- Workfile API ---
    def get_workfile_extensions(self):
        return [".katana"]

    def workfile_has_unsaved_changes(self):
        if not _is_katana_available():
            return False
        from Katana import KatanaFile  # type: ignore
        return bool(KatanaFile.IsFileDirty())

    def get_current_workfile(self):
        """Return current project file path or None if unsaved."""
        if not _is_katana_available():
            return None
        from Katana import NodegraphAPI  # type: ignore

        path = NodegraphAPI.GetProjectFile()
        if not path:
            return None
        # For unsaved projects, Katana may return an unresolved asset ID.
        if not os.path.exists(path):
            return None
        return path

    def save_workfile(self, dst_path=None):
        if not _is_katana_available():
            return dst_path
        from Katana import KatanaFile  # type: ignore

        current = self.get_current_workfile()
        file_to_save = dst_path or current
        if not file_to_save:
            raise ValueError("Katana workfile is not saved yet.")
        return KatanaFile.Save(file_to_save)

    def open_workfile(self, filepath):
        if not _is_katana_available():
            return filepath
        from Katana import KatanaFile  # type: ignore

        KatanaFile.Load(filepath)
        return filepath


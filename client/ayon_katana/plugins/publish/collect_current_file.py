# -*- coding: utf-8 -*-
import os

import pyblish.api

from ayon_katana.api import plugin


class CollectKatanaCurrentFile(plugin.KatanaContextPlugin):
    """Inject the current working file into context."""

    order = pyblish.api.CollectorOrder - 0.5
    label = "Katana Current File"

    def process(self, context):
        current_file = ""
        try:
            from Katana import NodegraphAPI  # type: ignore

            path = NodegraphAPI.GetProjectFile()
            if path and os.path.exists(path):
                current_file = path
        except Exception:
            # Katana modules not available (e.g. tests/import)
            pass

        if not current_file:
            self.log.warning("Katana workfile is unsaved.")

        context.data["currentFile"] = current_file
        self.log.info("Current workfile path: %s", current_file)


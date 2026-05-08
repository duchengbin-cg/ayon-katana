# -*- coding: utf-8 -*-
import os

import pyblish.api

from ayon_katana.api import plugin


class CollectWorkfile(plugin.KatanaInstancePlugin):
    """Inject workfile representation into instance."""

    order = pyblish.api.CollectorOrder - 0.01
    label = "Katana Workfile Data"
    families = ["workfile"]

    def process(self, instance):
        current_file = instance.context.data.get("currentFile") or ""
        if not current_file:
            self.log.warning("No currentFile collected - skipping workfile data.")
            return

        folder, file_name = os.path.split(current_file)
        _, ext = os.path.splitext(file_name)

        # Basic workfile members
        instance.data["setMembers"] = [current_file]

        # Frame data might already exist in context from ayon-core collectors.
        for key in ("frameStart", "frameEnd", "handleStart", "handleEnd"):
            if key in instance.context.data and key not in instance.data:
                instance.data[key] = instance.context.data[key]

        instance.data["representations"] = [{
            "name": ext.lstrip(".") or "katana",
            "ext": ext.lstrip(".") or "katana",
            "files": file_name,
            "stagingDir": folder,
        }]

        self.log.debug("Collected workfile instance: %s", file_name)


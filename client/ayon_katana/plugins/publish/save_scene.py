# -*- coding: utf-8 -*-
import inspect

import pyblish.api

from ayon_core.pipeline import registered_host, PublishError

from ayon_katana.api import plugin


class SaveCurrentScene(plugin.KatanaContextPlugin):
    """Save current scene if it has unsaved changes."""

    label = "Save current file"
    order = pyblish.api.ExtractorOrder - 0.49

    def process(self, context):
        host = registered_host()

        current_file = host.get_current_workfile()
        if (context.data.get("currentFile") or "") != (current_file or ""):
            raise PublishError(
                f"Collected filename '{context.data.get('currentFile')}' differs"
                f" from current scene name '{current_file}'.",
                description=self.get_error_description(),
            )

        if not current_file:
            raise PublishError(
                "Katana workfile is not saved yet. Please save the scene first.",
                description="Save the Katana project to a .katana file, then retry publishing.",
            )

        if host.workfile_has_unsaved_changes():
            self.log.info("Saving current file: %s", current_file)
            host.save_workfile(current_file)
        else:
            self.log.debug("No unsaved changes, skipping file save.")

    def get_error_description(self):
        return inspect.cleandoc(
            """### Scene File Name Changed During Publishing
            该错误通常发生在打开 Publisher 后又另存为/打开了其他文件。

            请重置 Publisher 并在不切换文件的情况下重新发布。
            """
        )


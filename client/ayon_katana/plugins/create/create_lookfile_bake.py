# -*- coding: utf-8 -*-
"""AutoCreator: Lookfile instances from Katana LookFileBake nodes."""

from __future__ import annotations

import os

from ayon_core.pipeline import AutoCreator, CreatedInstance

from ayon_katana.api import katana_node_utils as kutils


LOOK_NODE_TYPES = (
    "LookFileBake",
    "LookFileBakeAPI",  # just in case (older/custom)
)


class CreateLookfileBake(AutoCreator):
    identifier = "io.ayon.creators.katana.lookfile"
    label = "Lookfile (from LookFileBake nodes)"
    product_base_type = "look"
    product_type = product_base_type
    icon = "fa5.palette"

    default_variant = "Main"
    settings_category = "katana"
    is_mandatory = False

    def create(self):
        if not kutils.is_katana_available():
            return

        existing = [
            inst for inst in self.create_context.instances
            if inst.creator_identifier == self.identifier
        ]
        existing_by_node = {
            (inst.get("sourceNodeName") or ""): inst
            for inst in existing
            if inst.get("sourceNodeName")
        }

        project_entity = self.create_context.get_current_project_entity()
        folder_entity = self.create_context.get_current_folder_entity()
        task_entity = self.create_context.get_current_task_entity()

        project_name = project_entity["name"]
        host_name = self.create_context.host_name

        for node_type in LOOK_NODE_TYPES:
            for node in kutils.get_all_nodes_by_type(node_type):
                node_name = node.getName()
                if node_name in existing_by_node:
                    continue

                # According to Katana node reference, LookFileBake uses `saveTo`
                output_path = kutils.get_param_string(node, ("saveTo", "outputPath", "fileName"))
                if not output_path:
                    continue

                output_path = kutils.normalize_path(output_path)
                # Default output is .klf archive, but could be a directory.
                ext = "klf"
                if os.path.splitext(output_path)[1]:
                    ext = os.path.splitext(output_path)[1].lstrip(".").lower() or "klf"

                variant = node_name or self.default_variant
                product_name = self.get_product_name(
                    project_name=project_name,
                    folder_entity=folder_entity,
                    task_entity=task_entity,
                    variant=variant,
                    host_name=host_name,
                )

                data = {
                    "folderPath": folder_entity["path"],
                    "task": task_entity["name"],
                    "variant": variant,
                    "sourceNodeType": node_type,
                    "sourceNodeName": node_name,
                    "outputPath": output_path,
                    "ext": ext,
                }

                created = CreatedInstance(
                    product_type=self.product_type,
                    product_name=product_name,
                    data=data,
                    creator=self,
                )
                self._add_instance_to_context(created)


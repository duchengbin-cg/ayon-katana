# -*- coding: utf-8 -*-
"""AutoCreator: USD export instances from Katana USD export nodes."""

from __future__ import annotations

import os

from ayon_core.pipeline import AutoCreator, CreatedInstance

from ayon_katana.api import katana_node_utils as kutils


USD_NODE_TYPES = (
    "UsdLayerExport",  # Katana 7.5+
    "UsdExport",       # Katana USD plug-ins
)


class CreateUsdExport(AutoCreator):
    identifier = "io.ayon.creators.katana.usd"
    label = "USD Export (from Katana nodes)"
    product_base_type = "usd"
    product_type = product_base_type
    icon = "fa5.file-export"

    default_variant = "Main"
    settings_category = "katana"
    is_mandatory = False

    def create(self):
        # This AutoCreator generates instances automatically based on existing
        # export nodes in the Katana node graph.
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

        for node_type in USD_NODE_TYPES:
            for node in kutils.get_all_nodes_by_type(node_type):
                node_name = node.getName()
                if node_name in existing_by_node:
                    continue

                # We don't have an official parameter name list for all versions.
                # Try a few common ones and allow the user to fix on their side.
                output_path = kutils.get_param_string(
                    node,
                    (
                        # common patterns
                        "fileName",
                        "file",
                        "filepath",
                        "outputPath",
                        "outputFile",
                        "saveTo",
                        # UsdLayerExport mentions an "asset" parameter in docs
                        "asset",
                        "asset.value",
                    ),
                )
                if not output_path:
                    # Not configured, skip instance creation.
                    continue

                output_path = kutils.normalize_path(output_path)
                _, ext = os.path.splitext(output_path)
                ext = ext.lstrip(".").lower() or "usd"

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


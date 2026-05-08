# -*- coding: utf-8 -*-
"""Creator plugin for creating Katana workfile instance.

This is a minimal AutoCreator that ensures there is a `workfile` instance
available in the Create/Publish UI so users can submit the current `.katana`
file to AYON.
"""

from ayon_core.pipeline import CreatedInstance, AutoCreator


class CreateWorkfile(AutoCreator):
    identifier = "io.ayon.creators.katana.workfile"
    label = "Workfile"
    product_base_type = "workfile"
    product_type = product_base_type
    icon = "fa5.file"

    default_variant = "Main"
    settings_category = "katana"
    is_mandatory = False

    def create(self):
        variant = self.default_variant
        current_instance = next(
            (
                instance for instance in self.create_context.instances
                if instance.creator_identifier == self.identifier
            ),
            None,
        )

        project_entity = self.create_context.get_current_project_entity()
        folder_entity = self.create_context.get_current_folder_entity()
        task_entity = self.create_context.get_current_task_entity()

        project_name = project_entity["name"]
        folder_path = folder_entity["path"]
        task_name = task_entity["name"]
        host_name = self.create_context.host_name

        if current_instance is None:
            product_name = self.get_product_name(
                project_name=project_name,
                folder_entity=folder_entity,
                task_entity=task_entity,
                variant=variant,
                host_name=host_name,
            )
            data = {
                "folderPath": folder_path,
                "task": task_name,
                "variant": variant,
            }

            self.log.info("Auto-creating Katana workfile instance...")
            current_instance = CreatedInstance(
                product_base_type=self.product_base_type,
                product_type=self.product_base_type,
                product_name=product_name,
                data=data,
                creator=self,
            )
            self._add_instance_to_context(current_instance)
        else:
            # Keep instance in sync with current context
            if (
                current_instance["folderPath"] != folder_path
                or current_instance["task"] != task_name
            ):
                product_name = self.get_product_name(
                    project_name=project_name,
                    folder_entity=folder_entity,
                    task_entity=task_entity,
                    variant=variant,
                    host_name=host_name,
                )
                current_instance["folderPath"] = folder_path
                current_instance["task"] = task_name
                current_instance["productName"] = product_name

        if hasattr(current_instance, "set_mandatory"):
            current_instance.set_mandatory(self.is_mandatory)

    # Intentionally no persistence into the Katana scene yet.
    def collect_instances(self):
        return


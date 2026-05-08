# -*- coding: utf-8 -*-
import pyblish.api

from ayon_katana.api import plugin


class FixWorkfileFamily(plugin.KatanaContextPlugin):
    """Ensure workfile instances have proper `family` metadata.

    Depending on ayon-core version, CreatedInstance -> pyblish Instance
    conversion may store workfile type under different keys.
    This makes sure downstream publish plugins that rely on `families`
    filtering will still run.
    """

    order = pyblish.api.CollectorOrder - 0.2
    label = "Fix Workfile Family"

    def process(self, context):
        for instance in context:
            product_type = (
                instance.data.get("productType")
                or instance.data.get("product_type")
                or instance.data.get("productTypeName")
            )
            if product_type != "workfile":
                continue

            # Ensure family / families exist
            instance.data.setdefault("family", "workfile")
            families = instance.data.setdefault("families", [])
            if "workfile" not in families:
                families.append("workfile")


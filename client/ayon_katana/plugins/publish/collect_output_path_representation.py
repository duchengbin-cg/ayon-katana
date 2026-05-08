# -*- coding: utf-8 -*-
import os

import pyblish.api

from ayon_core.pipeline import PublishError

from ayon_katana.api import plugin


class CollectOutputPathRepresentation(plugin.KatanaInstancePlugin):
    """Collect representation for instances that define `outputPath`.

    Used for:
    - USD exports (UsdLayerExport / UsdExport)
    - Lookfiles (LookFileBake)
    """

    label = "Collect Output Path Representation"
    # Must run after `ExecuteKatanaExports` which can generate the files.
    order = pyblish.api.CollectorOrder + 0.2

    def process(self, instance):
        output_path = instance.data.get("outputPath")
        if not output_path:
            return

        output_path = os.path.normpath(output_path)

        # Determine family from product type
        product_type = (
            instance.data.get("productType")
            or instance.data.get("product_type")
            or instance.data.get("productTypeName")
            or instance.data.get("product_type_name")
        )
        if product_type:
            instance.data.setdefault("family", product_type)
            families = instance.data.setdefault("families", [])
            if product_type not in families:
                families.append(product_type)

        if not os.path.exists(output_path):
            raise PublishError(
                f"输出文件不存在：{output_path}",
                description=(
                    "发布前导出动作已尝试自动触发，但仍未在磁盘找到输出。\n"
                    "请检查节点的输出路径参数是否正确、是否有权限写入、以及节点是否报错。"
                ),
            )

        ext = instance.data.get("ext")
        if not ext:
            ext = os.path.splitext(output_path)[1].lstrip(".").lower() or "dat"

        if os.path.isdir(output_path):
            staging_dir = output_path
            files = sorted(
                f for f in os.listdir(output_path)
                if os.path.isfile(os.path.join(output_path, f))
            )
            if not files:
                raise PublishError(
                    f"输出目录为空：{output_path}",
                    description="LookFileBake 输出为目录时，目录里应至少包含一个 .klf 文件。",
                )
        else:
            staging_dir = os.path.dirname(output_path)
            files = os.path.basename(output_path)

        instance.data.setdefault("setMembers", []).append(output_path)

        instance.data["representations"] = [{
            "name": ext,
            "ext": ext,
            "files": files,
            "stagingDir": staging_dir,
        }]

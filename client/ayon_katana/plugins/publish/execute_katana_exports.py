# -*- coding: utf-8 -*-
import os

import pyblish.api

from ayon_core.pipeline import PublishError

from ayon_katana.api import plugin
from ayon_katana.api import katana_export


class ExecuteKatanaExports(plugin.KatanaContextPlugin):
    """Trigger Katana export nodes before collecting representations.

    This runs in Collector phase so later collectors can validate file
    existence and build representations from exported files.
    """

    label = "Execute Katana Exports"
    # Run after basic collectors (e.g. currentFile) but before representation
    # collectors that validate existence.
    order = pyblish.api.CollectorOrder + 0.05

    def process(self, context):
        # Only execute in Katana
        try:
            from Katana import Configuration  # type: ignore
            # UI plugins are not loaded in batch/script/shell modes, so we also
            # skip export execution in those modes.
            if not Configuration.get("KATANA_UI_MODE"):
                self.log.info("Not running in Katana UI mode - skipping exports.")
                return
        except Exception:
            # Katana not available
            return

        for instance in context:
            node_name = instance.data.get("sourceNodeName")
            node_type = instance.data.get("sourceNodeType")
            output_path = instance.data.get("outputPath")
            if not node_name or not node_type or not output_path:
                continue

            # Normalize outputPath
            output_path = os.path.normpath(output_path)
            instance.data["outputPath"] = output_path.replace("\\", "/")

            # Trigger export
            exported_to = None
            if node_type == "LookFileBake":
                exported_to = katana_export.export_lookfile(node_name)
            elif node_type in {"UsdLayerExport", "UsdExport"}:
                exported_to = katana_export.export_usd(node_name)

            if exported_to:
                instance.data["outputPath"] = os.path.normpath(exported_to).replace("\\", "/")
                output_path = os.path.normpath(exported_to)

            # Validate result exists (directory allowed for LookFileBake)
            if not os.path.exists(output_path):
                raise PublishError(
                    f"自动导出失败：未在磁盘找到输出：{output_path}",
                    description=(
                        f"实例来源节点：{node_type} / {node_name}\n\n"
                        "可能原因：\n"
                        "1) 节点尚未正确配置输出路径（saveTo/asset/outputPath 等）\n"
                        "2) 节点的导出按钮参数名与预期不一致（需要针对你现场的节点做适配）\n"
                        "3) 当前不是 UI 模式或导出被 Katana 阻止\n\n"
                        "你可以把该节点的参数截图（尤其是导出按钮和输出路径字段），"
                        "我会把触发逻辑补齐到 Katana 9.0v2。"
                    ),
                )


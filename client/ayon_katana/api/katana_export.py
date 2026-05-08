# -*- coding: utf-8 -*-
"""Best-effort helpers to trigger Katana export nodes programmatically.

Important:
Katana node APIs differ between versions, renderers and customizations.
So we try multiple approaches:
- call a known module API (when available)
- press a script button parameter (when available)
"""

from __future__ import annotations

from typing import Iterable, Optional

from . import katana_node_utils as kutils


def _press_button(param) -> bool:
    """Attempt to trigger a Katana "script button" parameter."""
    # Different Katana versions expose different methods on param objects.
    for attr in ("pressButton", "execute", "trigger"):
        fn = getattr(param, attr, None)
        if callable(fn):
            fn()
            return True

    # Fallback: some parameters accept setValue(1, 0) for button-like params.
    fn = getattr(param, "setValue", None)
    if callable(fn):
        try:
            fn(1, 0)
            return True
        except Exception:
            return False
    return False


def _press_first_button(
    node,
    candidate_param_paths: Iterable[str],
) -> bool:
    for param_path in candidate_param_paths:
        try:
            param = node.getParameter(param_path)
        except Exception:
            param = None
        if param is None:
            continue
        if _press_button(param):
            return True
    return False


def export_lookfile(node_name: str) -> Optional[str]:
    """Trigger LookFileBake export for given node name.

    Returns output path (best-effort) or None if not triggered.
    """
    if not kutils.is_katana_available():
        return None
    from Katana import NodegraphAPI  # type: ignore

    node = NodegraphAPI.GetNode(node_name)
    if node is None:
        return None

    # Try module API first (if present)
    try:
        import Nodes3DAPI  # type: ignore  # noqa
        import LookFileBakeAPI  # type: ignore  # noqa
        # Some versions provide callable helper on the API module.
        # If not available we fall back to pressing the node's button.
    except Exception:
        pass

    # Press the "Write Look File" button on the node.
    # In node reference it is displayed as "Write Look File".
    ok = _press_first_button(
        node,
        (
            "writeLookFile",
            "writeLookFileNow",
            "write",
            "Write Look File",  # unlikely but cheap to try
        ),
    )
    if not ok:
        return None

    return kutils.get_param_string(node, ("saveTo", "outputPath", "fileName"))


def export_usd(node_name: str) -> Optional[str]:
    """Trigger USD export (UsdLayerExport / UsdExport) for given node name."""
    if not kutils.is_katana_available():
        return None
    from Katana import NodegraphAPI  # type: ignore

    node = NodegraphAPI.GetNode(node_name)
    if node is None:
        return None

    # Press common export buttons.
    ok = _press_first_button(
        node,
        (
            "export",
            "exportNow",
            "write",
            "writeNow",
            "doExport",
            "run",
        ),
    )
    if not ok:
        return None

    return kutils.get_param_string(
        node,
        (
            "fileName",
            "file",
            "filepath",
            "outputPath",
            "outputFile",
            "saveTo",
            "asset",
            "asset.value",
        ),
    )


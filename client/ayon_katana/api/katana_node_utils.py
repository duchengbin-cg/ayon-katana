# -*- coding: utf-8 -*-
from __future__ import annotations

import os
from typing import Iterable, Optional


def is_katana_available() -> bool:
    try:
        import Katana  # noqa: F401
        return True
    except Exception:
        return False


def get_all_nodes_by_type(node_type: str):
    """Return list of Katana nodes by type (or empty list)."""
    if not is_katana_available():
        return []
    from Katana import NodegraphAPI  # type: ignore

    return NodegraphAPI.GetAllNodesByType(node_type) or []


def _get_parameter(node, param_path: str):
    try:
        return node.getParameter(param_path)
    except Exception:
        return None


def find_first_parameter(node, candidate_paths: Iterable[str]):
    for path in candidate_paths:
        param = _get_parameter(node, path)
        if param is not None:
            return param
    return None


def get_param_string(node, candidate_paths: Iterable[str]) -> Optional[str]:
    """Try to get a string parameter value from a list of possible paths."""
    param = find_first_parameter(node, candidate_paths)
    if param is None:
        return None
    try:
        value = param.getValue(0)
    except Exception:
        return None
    if value is None:
        return None
    value = str(value).strip()
    return value or None


def normalize_path(path: str) -> str:
    # Keep consistent slashes across platforms for publish metadata.
    return os.path.normpath(path).replace("\\", "/")


# -*- coding: utf-8 -*-
"""Katana specific AYON/Pyblish plugin definitions (minimal)."""

import pyblish.api

SETTINGS_CATEGORY = "katana"


class KatanaInstancePlugin(pyblish.api.InstancePlugin):
    """Base class for Katana instance publish plugins."""

    hosts = ["katana"]
    settings_category = SETTINGS_CATEGORY


class KatanaContextPlugin(pyblish.api.ContextPlugin):
    """Base class for Katana context publish plugins."""

    hosts = ["katana"]
    settings_category = SETTINGS_CATEGORY


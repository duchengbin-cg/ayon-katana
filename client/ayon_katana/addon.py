import os

from ayon_core.addon import AYONAddon, IHostAddon

from .version import __version__

KATANA_ADDON_DIR = os.path.dirname(os.path.abspath(__file__))


class KatanaAddon(AYONAddon, IHostAddon):
    name = "katana"
    version = __version__
    host_name = "katana"

    def add_implementation_envs(self, env, _app):
        """Inject Katana resources and python paths into launched app env.

        Katana loads customization from `KATANA_RESOURCES` (colon-separated
        list on Linux). Under each resource root Katana will look for specific
        subfolders like `Startup` (exec init.py), `Shelves`, `UIPlugins`, etc.
        """

        # 1) Katana resources (Startup/init.py, Shelves, ...)
        resources_root = os.path.join(KATANA_ADDON_DIR, "resources")
        old_resources = env.get("KATANA_RESOURCES") or ""
        new_resources = [resources_root]
        for path in old_resources.split(os.pathsep):
            if not path:
                continue
            norm_path = os.path.normpath(path)
            if norm_path not in new_resources:
                new_resources.append(norm_path)
        env["KATANA_RESOURCES"] = os.pathsep.join(new_resources)

        # 2) Python paths - prefer POST path to avoid overriding Katana internals
        startup_python = os.path.join(KATANA_ADDON_DIR, "startup")
        vendor_python = os.path.join(KATANA_ADDON_DIR, "vendor", "python")
        old_post = env.get("KATANA_POST_PYTHONPATH") or ""
        new_post = [startup_python, vendor_python]
        for path in old_post.split(os.pathsep):
            if not path:
                continue
            norm_path = os.path.normpath(path)
            if norm_path not in new_post:
                new_post.append(norm_path)
        env["KATANA_POST_PYTHONPATH"] = os.pathsep.join(new_post)

        # 3) Default envs
        env.setdefault("AYON_LOG_NO_COLORS", "1")

        # 4) USD plug-in discovery for Katana's namespaced USD (fnpxr)
        #
        # AYON USD resolver (ayon-usd addon) sets `PXR_PLUGINPATH_NAME`.
        # Katana expects `FNPXR_PLUGINPATH` for its namespaced USD library.
        pxr_pluginpath = env.get("PXR_PLUGINPATH_NAME") or ""
        if pxr_pluginpath:
            old_fnpxr = env.get("FNPXR_PLUGINPATH") or ""
            merged = []
            for p in (old_fnpxr.split(os.pathsep) if old_fnpxr else []):
                if p:
                    merged.append(os.path.normpath(p))
            for p in pxr_pluginpath.split(os.pathsep):
                if not p:
                    continue
                p = os.path.normpath(p)
                if p not in merged:
                    merged.append(p)
            env["FNPXR_PLUGINPATH"] = os.pathsep.join(merged)

    def get_launch_hook_paths(self, app):
        if app.host_name != self.host_name:
            return []
        return [
            os.path.join(KATANA_ADDON_DIR, "hooks"),
        ]

    def get_workfile_extensions(self):
        return [".katana"]

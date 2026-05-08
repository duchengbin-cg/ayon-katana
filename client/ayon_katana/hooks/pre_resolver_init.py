"""Pre-launch hook to initialize AYON OpenUSD Resolver for Katana.

The official `ayon-usd` addon provides a similar hook for some DCCs.
As Katana uses a namespaced USD library (fnpxr) it expects `FNPXR_PLUGINPATH`
instead of `PXR_PLUGINPATH_NAME`, so we additionally mirror the paths.
"""

from __future__ import annotations

import json
import os

from ayon_applications import LaunchTypes, PreLaunchHook


class InitializeUsdResolverForKatana(PreLaunchHook):
    app_groups = {"katana"}
    launch_types = {LaunchTypes.local, LaunchTypes.farm_publish}

    def execute(self):
        # Soft dependency on ayon-usd addon
        try:
            from ayon_usd import config, utils  # type: ignore
            from ayon_usd.addon import ADDON_DATA_JSON_PATH  # type: ignore
        except Exception:
            self.log.info("ayon-usd is not available - skipping USD resolver init.")
            return

        project_settings = self.data["project_settings"]
        usd_settings = project_settings.get("usd") or {}
        distribution = (usd_settings.get("distribution") or {})
        if not distribution.get("enabled"):
            self.log.info("USD binary distribution is disabled - skipping resolver init.")
            return

        # Note: `self.app_name` is typically the application key e.g. 'katana'
        resolver_lake_fs_path = utils.get_resolver_to_download(
            project_settings, self.app_name
        )
        if not resolver_lake_fs_path:
            self.log.warning(
                "No USD resolver configured for application: %s", self.app_name
            )
            return

        # Resolve timestamp on lakeFS so we can skip re-download.
        self.log.info("Using resolver from lakeFS: %s", resolver_lake_fs_path)
        lake_fs = config.get_global_lake_instance()
        lake_fs_resolver_time_stamp = (
            lake_fs.get_element_info(resolver_lake_fs_path).get("Modified Time")
        )
        if not lake_fs_resolver_time_stamp:
            self.log.error(
                "Could not find resolver timestamp on lakeFS server for: %s",
                self.app_name,
            )
            return

        # Ensure addon data json exists (ayon-usd creates it on tray start,
        # but Katana may be launched without Tray running).
        os.makedirs(os.path.dirname(ADDON_DATA_JSON_PATH), exist_ok=True)
        if not os.path.exists(ADDON_DATA_JSON_PATH):
            with open(ADDON_DATA_JSON_PATH, "w", encoding="utf-8") as f:
                json.dump({}, f)

        with open(ADDON_DATA_JSON_PATH, "r", encoding="utf-8") as f:
            addon_data_json = json.load(f) or {}

        key = str(self.app_name).replace("/", "_")
        local_resolver_key = f"resolver_data_{key}"
        local_resolver_timestamp, local_resolver = addon_data_json.get(
            local_resolver_key, [None, None]
        )

        if (
            local_resolver
            and lake_fs_resolver_time_stamp == local_resolver_timestamp
            and os.path.exists(local_resolver)
        ):
            self.log.info("Using cached local resolver: %s", local_resolver)
        else:
            local_resolver = utils.lakefs_download_and_extract(
                resolver_lake_fs_path, str(utils.get_download_dir())
            )
            if not local_resolver:
                self.log.warning("Resolver download failed - skipping.")
                return

            addon_data_json[local_resolver_key] = [
                lake_fs_resolver_time_stamp,
                local_resolver,
            ]
            with open(ADDON_DATA_JSON_PATH, "w", encoding="utf-8") as f:
                json.dump(addon_data_json, f)

        updated_env = utils.get_resolver_setup_info(
            local_resolver, project_settings, env=self.launch_context.env
        )
        self.launch_context.env.update(updated_env)

        # Katana uses namespaced USD library; mirror PXR_PLUGINPATH_NAME into
        # FNPXR_PLUGINPATH so resolver can be discovered by Katana USD.
        pxr = self.launch_context.env.get("PXR_PLUGINPATH_NAME") or ""
        if pxr:
            current = self.launch_context.env.get("FNPXR_PLUGINPATH") or ""
            # ensure we append rather than overwrite
            fnpxr = current + (os.pathsep if current else "") + pxr
            self.launch_context.env["FNPXR_PLUGINPATH"] = fnpxr

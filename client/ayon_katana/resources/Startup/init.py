"""AYON startup script for Katana.

Katana executes `<KATANA_RESOURCES>/Startup/init.py` on startup.
This file is kept intentionally lightweight.
"""

from ayon_core.pipeline import install_host
from ayon_katana.api import KatanaHost


def main():
    print("Installing AYON for Katana ...")
    install_host(KatanaHost())

    # Optional debug: print key env vars for troubleshooting launcher injection.
    # Enable by setting `AYON_KATANA_DEBUG_ENV=1` in the launch environment.
    try:
        import os
        if os.environ.get("AYON_KATANA_DEBUG_ENV", "").strip() in {"1", "true", "True"}:
            keys = (
                "KATANA_RESOURCES",
                "KATANA_POST_PYTHONPATH",
                "PXR_PLUGINPATH_NAME",
                "FNPXR_PLUGINPATH",
                "PYTHONPATH",
                "PATH",
            )
            print("AYON_KATANA_DEBUG_ENV=1 - printing relevant environment:")
            for k in keys:
                v = os.environ.get(k)
                if v:
                    print(f"  {k}={v}")
    except Exception:
        pass


main()

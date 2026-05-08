"""AYON startup script for Katana.

Katana executes `<KATANA_RESOURCES>/Startup/init.py` on startup.
This file is kept intentionally lightweight.
"""

from ayon_core.pipeline import install_host
from ayon_katana.api import KatanaHost


def main():
    print("Installing AYON for Katana ...")
    install_host(KatanaHost())


main()


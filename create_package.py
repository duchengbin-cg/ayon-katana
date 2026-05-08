#!/usr/bin/env python3
"""Build AYON server addon package from this repository.

This is a lightweight variant of the packaging script used in other official
AYON host addons. It creates:

`./package/<addon_name>/<addon_version>/`

Containing:
- `server/` copied as-is
- `private/client.zip` with `client/<client_dir>/...`

Usage:
    python create_package.py
    python create_package.py --output-dir /path/to/ayon-backend/addons
"""

from __future__ import annotations

import argparse
import os
import shutil
import zipfile

import package as package_module


def _rmtree(path: str):
    if os.path.exists(path):
        shutil.rmtree(path)


def _ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def _zip_dir(src_dir: str, dst_zip_path: str):
    _ensure_dir(os.path.dirname(dst_zip_path))
    with zipfile.ZipFile(dst_zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _dirs, files in os.walk(src_dir):
            for fname in files:
                if fname.endswith((".pyc", ".pyo")):
                    continue
                abs_path = os.path.join(root, fname)
                rel_path = os.path.relpath(abs_path, src_dir)
                zf.write(abs_path, rel_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        default=os.path.join(os.path.dirname(__file__), "package"),
        help="Output directory where package/<name>/<version> will be created.",
    )
    args = parser.parse_args()

    root = os.path.dirname(os.path.abspath(__file__))
    addon_name = package_module.name
    addon_version = package_module.version
    client_dir = getattr(package_module, "client_dir", None)

    out_root = os.path.abspath(args.output_dir)
    dst_root = os.path.join(out_root, addon_name, addon_version)

    _rmtree(dst_root)
    _ensure_dir(dst_root)

    # Copy server
    server_src = os.path.join(root, "server")
    if os.path.exists(server_src):
        shutil.copytree(server_src, os.path.join(dst_root, "server"))

    # Zip client code into private
    if client_dir:
        client_src = os.path.join(root, "client", client_dir)
        if not os.path.exists(client_src):
            raise RuntimeError(f"Client dir not found: {client_src}")
        _zip_dir(
            client_src,
            os.path.join(dst_root, "private", "client.zip"),
        )

    print(f"Package created: {dst_root}")


if __name__ == "__main__":
    main()


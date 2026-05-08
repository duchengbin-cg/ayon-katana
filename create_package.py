#!/usr/bin/env python3
"""Build AYON server addon package from this repository.

This script creates a ready-to-upload zip (like other official AYON addons):

`./package/<addon_name>-<addon_version>.zip`

The zip contains:

`<addon_name>/<addon_version>/server/...`
`<addon_name>/<addon_version>/private/client.zip`  (client/<client_dir> zipped)

Usage:
    python create_package.py
    python create_package.py --output-dir /path/to/output
"""

from __future__ import annotations

import argparse
import io
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

def _zip_folder_to_bytes(src_dir: str) -> bytes:
    """Zip full folder (src_dir) and return bytes."""
    buff = io.BytesIO()
    with zipfile.ZipFile(buff, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _dirs, files in os.walk(src_dir):
            for fname in files:
                if fname.endswith((".pyc", ".pyo")):
                    continue
                abs_path = os.path.join(root, fname)
                rel_path = os.path.relpath(abs_path, src_dir)
                zf.write(abs_path, rel_path)
    return buff.getvalue()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        default=os.path.join(os.path.dirname(__file__), "package"),
        help="Output directory where package zip will be created.",
    )
    args = parser.parse_args()

    root = os.path.dirname(os.path.abspath(__file__))
    addon_name = package_module.name
    addon_version = package_module.version
    client_dir = getattr(package_module, "client_dir", None)

    out_root = os.path.abspath(args.output_dir)
    dst_root = os.path.join(out_root, addon_name, addon_version)
    dst_zip_path = os.path.join(out_root, f"{addon_name}-{addon_version}.zip")

    _rmtree(dst_root)
    if os.path.exists(dst_zip_path):
        os.remove(dst_zip_path)
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

        # Keep client version in sync with package version for releases.
        version_py_path = os.path.join(client_src, "version.py")
        if os.path.exists(version_py_path):
            with open(version_py_path, "w", encoding="utf-8") as f:
                f.write(
                    "# -*- coding: utf-8 -*-\n"
                    f"\"\"\"Package declaring AYON addon '{addon_name}' version.\"\"\"\n"
                    f"__version__ = \"{addon_version}\"\n"
                )

        _zip_dir(
            client_src,
            os.path.join(dst_root, "private", "client.zip"),
        )

    # Build final zip (ayon server expects a single zip file)
    _ensure_dir(out_root)
    with zipfile.ZipFile(dst_zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # Put the folder under "<addon_name>/<addon_version>/"
        base_prefix = os.path.join(addon_name, addon_version)
        for root_dir, _dirs, files in os.walk(dst_root):
            for fname in files:
                abs_path = os.path.join(root_dir, fname)
                rel = os.path.relpath(abs_path, dst_root)
                zf.write(abs_path, os.path.join(base_prefix, rel))

    print(f"Package folder created: {dst_root}")
    print(f"Package zip created: {dst_zip_path}")


if __name__ == "__main__":
    main()

"""Katana Shelf Item: Open AYON Publisher."""

from ayon_core.tools.utils import host_tools


def main():
    # In most hosts `host_tools.show_publisher()` will resolve correct Qt parent
    # internally (or fall back to None).
    host_tools.show_publisher()


main()


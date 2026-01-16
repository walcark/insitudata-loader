"""
pygeodes_visu.py

Author  : Kévin Walcarius
Date    : 2025-01-13
Version : 1.0
License : MIT
Summary : Module to perform visualization of PyGeodes Items.
"""

from pygeodes.utils.stac import Item
import time


def visualize_item(item: Item) -> None:
    """
    Visualize a pygeodes item.
    """
    item.show_quicklook()
    time.sleep(10)

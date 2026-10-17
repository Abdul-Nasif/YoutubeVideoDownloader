"""Load all KV files in the correct order.

common.kv defines the styles. download.kv and library.kv define screen
rules. root.kv wires everything into a ScreenManager and is loaded last.
"""
import os

from kivy.lang import Builder

_HERE = os.path.dirname(__file__)
_ORDER = ["common.kv", "download.kv", "library.kv", "root.kv"]


def load_all():
    for name in _ORDER:
        path = os.path.join(_HERE, name)
        if os.path.exists(path):
            Builder.load_file(path)
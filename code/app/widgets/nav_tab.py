from kivy.properties import BooleanProperty
from kivy.uix.button import Button


class NavTab(Button):
    """Top-bar tab; `selected` drives its styling in common.kv."""
    selected = BooleanProperty(False)
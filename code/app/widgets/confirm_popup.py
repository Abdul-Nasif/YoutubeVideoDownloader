from kivy.properties import StringProperty
from kivy.uix.popup import Popup


class ConfirmPopup(Popup):
    message = StringProperty("")
    confirm_text = StringProperty("Delete")
    cancel_text = StringProperty("Cancel")
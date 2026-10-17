from kivy.properties import NumericProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview.views import RecycleDataViewBehavior


class FileEntry(RecycleDataViewBehavior, BoxLayout):
    """One row in the library RecycleView."""
    filename = StringProperty("")
    size_str = StringProperty("")
    date_str = StringProperty("")
    path = StringProperty("")
    index = NumericProperty(0)

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        return super().refresh_view_attrs(rv, index, data)
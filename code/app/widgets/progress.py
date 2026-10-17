from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.properties import NumericProperty
from kivy.uix.widget import Widget


class ProgressTrack(Widget):
    value = NumericProperty(0.0)
    max = NumericProperty(100.0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            self._track_c = Color(0.153, 0.153, 0.165, 1)
            self._track = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(3)])
            self._fill_c = Color(0.97, 0.97, 0.97, 1)
            self._fill = RoundedRectangle(pos=self.pos, size=(0, self.height), radius=[dp(3)])
        self.bind(pos=self._sync, size=self._sync, value=self._sync, max=self._sync)

    def _sync(self, *_):
        r = min(dp(3), self.height / 2.0)
        self._track.pos = self.pos
        self._track.size = self.size
        self._track.radius = [r]

        ratio = (self.value / self.max) if self.max else 0.0
        ratio = max(0.0, min(1.0, ratio))
        w = self.width * ratio
        fr = min(r, w / 2.0) if w > 0 else 0.0
        self._fill.pos = self.pos
        self._fill.size = (w, self.height)
        self._fill.radius = [fr]
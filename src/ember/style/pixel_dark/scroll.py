from ember.ui import Scroll as _Scroll
from .scrollbar import ScrollBar


class Scroll(_Scroll):
    scrollbar_class = ScrollBar

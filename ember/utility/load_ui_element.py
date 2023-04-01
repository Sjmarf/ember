from ember import common as _c
from ember.ui.text import Text


def load_element(element, default_text_style=None):
    if type(element) is str:
        element = Text(element, height=default_text_style if default_text_style else _c.default_text_style)

    return element

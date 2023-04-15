from ember.ui.element import Element, ElementStrType
from typing import Optional

from ember.ui.text import Text


def load_element(element: ElementStrType, text_style=None,
                 text_width=None, text_height=None) -> Optional[Element]:
    if type(element) is str:
        return Text(element, style=text_style, width=text_width, height=text_height)
    elif isinstance(element, Element):
        return element
    elif element is None:
        return None
    else:
        raise ValueError(f"You must provide elements of type Element or str, not {type(element).__name__}.")

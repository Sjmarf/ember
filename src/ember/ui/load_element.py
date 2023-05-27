from typing import Optional

from .text import Text, TextStyle
from .base.element import Element, ElementStrType


def load_element(
    element: ElementStrType,
    text_style: Optional[TextStyle] = None,
    text_width: Optional[int] = None,
    text_height: Optional[int] = None,
) -> Optional[Element]:
    if type(element) is str:
        return Text(element, style=text_style, width=text_width, height=text_height)
    elif isinstance(element, Element):
        return element
    elif element is None:
        return None
    else:
        raise ValueError(
            f"You must provide elements of type Element or str, not {type(element).__name__}."
        )

from typing import Optional, TYPE_CHECKING

from .text import Text
from .base.element import Element, ElementStrType

if TYPE_CHECKING:
    from ..style.text_style import TextStyle


def load_element(
    element: ElementStrType,
    text_style: Optional["TextStyle"] = None,
    text_width: Optional[int] = None,
    text_height: Optional[int] = None,
) -> Optional[Element]:
    if type(element) is str:
        return Text(element, style=text_style, w=text_width, h=text_height)
    elif isinstance(element, Element):
        return element
    elif element is None:
        return None
    else:
        raise ValueError(
            f"You must provide elements of type Element or str, not {type(element).__name__}."
        )

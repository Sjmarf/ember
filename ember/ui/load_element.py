from ember.ui.element import Element, ElementType

from ember.ui.text import Text

def load_element(element: ElementType, text_style=None):
    if type(element) is str:
        return Text(element, style=text_style)
    elif isinstance(element, Element):
        return element
    else:
        raise ValueError(f"You must provide elements of type Element or str, not {element}.")    
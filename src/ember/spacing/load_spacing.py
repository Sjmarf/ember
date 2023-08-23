from typing import Union
from .spacing import Spacing
from .absolute_spacing import AbsoluteSpacing


def load_spacing(value: Union["Spacing", float]) -> "Spacing":
    if isinstance(value, (float, int)):
        return AbsoluteSpacing(value)
    return value

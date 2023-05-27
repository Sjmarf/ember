from typing import TypeVar

from ..common import DEFAULT_STYLE
from ember.style import load
from . import defaults

T = TypeVar("T")


def _get_style(style: T, name: str) -> T:
    if style is None:
        if getattr(defaults, name) is None:
            load(DEFAULT_STYLE, parts=[name])
        return getattr(defaults, name)
    else:
        return style

from typing import Union
from pygame import Surface
from ..material.material import Material


class Style:
    """
    All Styles inherit from this class. This base class should not be directly instantiated.
    """
    pass


MaterialType = Union[Material, Surface, str, None]

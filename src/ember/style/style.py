from typing import Union
from pygame import Surface
from ..material.material import Material


class Style:
    pass


MaterialType = Union[Material, Surface, str, None]

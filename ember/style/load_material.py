import pygame
from typing import Union

from ember.style.style import MaterialType
from ember.material.blank import Blank
from ember.material.stretched_surface import StretchedSurface
from ember.material.material import Material

def load_material(image: MaterialType, default: Union[Material, None]):
    if isinstance(image, Material):
        return image
    elif type(image) in {str,pygame.Surface}:
        return StretchedSurface(image)
    else:
        return Blank() if default is None else default

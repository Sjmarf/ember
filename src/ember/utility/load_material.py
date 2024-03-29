import pygame
from typing import Union, Optional

from ..common import MaterialType
from os import PathLike
from ember.material.blank import Blank
from ember.material.stretched_surface import StretchedSurface
from ember.material.material import Material

def load_material(image: Optional[MaterialType], existing: Material, fallback: Union[Material, None]) -> Material:
    if isinstance(image, Material):
        return image
    elif isinstance(image, (str, pygame.Surface, PathLike)):
        return StretchedSurface(image)
    elif not isinstance(existing, Blank):
        return existing
    elif fallback is not None:
        return fallback
    else:
        return Blank()


def load_sound(sound: Union[pygame.mixer.Sound, str, None]) -> Optional[pygame.mixer.Sound]:
    if isinstance(sound, pygame.mixer.Sound) or sound is None:
        return sound
    elif type(sound) is str:
        return pygame.mixer.Sound(sound)
    else:
        raise ValueError(f"Sound must be of type pygame.mixer.Sound, str or None, not {type(sound).__name__}.")

import pygame
from typing import Union, Optional

from ember.style.style import MaterialType
from ember.material.blank import Blank
from ember.material.stretched_surface import StretchedSurface
from ember.material.material import Material

def load_material(image: MaterialType, default: Union[Material, None]) -> Material:
    if isinstance(image, Material):
        return image
    elif type(image) in {str,pygame.Surface}:
        return StretchedSurface(image)
    else:
        return Blank() if default is None else default


def load_sound(sound: Union[pygame.mixer.Sound, str, None]) -> Optional[pygame.mixer.Sound]:
    if isinstance(sound, pygame.mixer.Sound) or sound is None:
        return sound
    elif type(sound) is str:
        return pygame.mixer.Sound(sound)
    else:
        raise ValueError(f"Sound must be of type pygame.mixer.Sound, str or None, not {type(sound).__name__}.")

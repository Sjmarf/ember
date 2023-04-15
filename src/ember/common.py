import pygame
from .common_styles import *
try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal


VERSION: str = "0.1"
is_ce: bool = getattr(pygame, "IS_CE", False)


class InheritType:
    pass


class DefaultType:
    pass


DEFAULT = DefaultType()
INHERIT = InheritType()

display_zoom: float = 1
mouse_pos: tuple[int, int] = (0, 0)

clock: Optional[pygame.time.Clock] = None
delta_time: float = 1

# Path to the library. It is an importlib Traversable object, but I can't work out how to typehint it
package = None

# Populated in View.__init__. Maybe that should be changed?
event_ids: list = []

audio_enabled: bool = False
audio_muted: bool = False

DEFAULT_STYLE: Literal['stone', 'plastic', 'white', 'dark'] = "plastic"

import pygame
from typing import Literal, Union, Sequence, Optional
from . import event as _event
from weakref import WeakSet

VERSION: str = "0.0.1"
is_ce: bool = getattr(pygame, "IS_CE", False)

event_ids = _event.__dict__.values()


class InheritType:
    pass


ColorType = Union[
    pygame.Color,
    int,
    str,
    tuple[int, int, int],
    tuple[int, int, int, int],
    Sequence[int],
]


class Error(Exception):
    pass


INHERIT = InheritType()

display_zoom: float = 1
mouse_pos: tuple[int, int] = (0, 0)

clock: Optional[pygame.time.Clock] = None
delta_time: float = 1

# Path to the library. It is an importlib Traversable object, but I can't work out how to typehint it
package = None

# Populated in View.__init__. Maybe that should be changed?
event_ids: list = []

views: WeakSet = WeakSet()

audio_enabled: bool = False
audio_muted: bool = False

DEFAULT_STYLE: Literal["stone", "plastic", "white", "dark"] = "dark"

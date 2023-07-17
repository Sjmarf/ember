import pygame
from typing import Literal, Union, Sequence, Optional, TYPE_CHECKING, Type
from collections import UserDict
from . import event as _event
from enum import Enum
from weakref import WeakSet

VERSION: str = "0.0.1"
is_ce: bool = getattr(pygame, "IS_CE", False)

event_ids = _event.__dict__.values()

if TYPE_CHECKING:
    from .ui.base.element import Element
    from .ui.default_style_dict import DefaultStyleDict
    from .ui.base.context_manager import ContextManagerMixin


class InheritType:
    pass


INHERIT = InheritType()


class FocusType:
    pass


FOCUS_CLOSEST = FocusType()
FOCUS_FIRST = FocusType()


class BlurMode:
    pass


BLUR_PIL = BlurMode()
BLUR_PYGAME = BlurMode()


class FocusDirection(Enum):
    SELECT = 0  # Used when focusing an element when no element is yet focused.
    IN = 1  # Pressing enter.
    IN_FIRST = 2  # The same as IN, but always enters the first element of a container.
    OUT = 3  # Pressing escape.
    LEFT = 4
    RIGHT = 5
    UP = 6
    DOWN = 7
    FORWARD = 8  # Pressing tab.
    BACKWARD = 9  # Pressing shift + tab.


ColorType = Union[
    pygame.Color,
    int,
    str,
    tuple[int, int, int],
    tuple[int, int, int, int],
    Sequence[int],
]

MaterialType = Union["Material", pygame.Surface, str]

RectType = Union[Sequence[float], Sequence[int], pygame.Rect, pygame.FRect]


class Error(RuntimeError):
    pass


display_zoom: float = 1
mouse_pos: tuple[int, int] = (0, 0)

clock: Optional[pygame.time.Clock] = None
delta_time: float = 1

# Path to the library. It is an importlib Traversable object, but I can't work out how to typehint it
package = None

views: WeakSet = WeakSet()

default_styles: "DefaultStyleDict"

joysticks: [pygame.joystick.Joystick] = []

audio_enabled: bool = False
audio_muted: bool = False

DEFAULT_STYLE: Literal["stone", "plastic", "white", "dark"] = "dark"


class Escaping:
    def __enter__(self):
        element_context_stack.append(None)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        element_context_stack.pop()


ESCAPING = Escaping()

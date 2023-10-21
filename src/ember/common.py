import pygame
import importlib.resources
from typing import Literal, Union, Sequence, Optional, TYPE_CHECKING, Generator, NewType
from . import event as _event
from enum import Enum
from weakref import WeakSet
from os import PathLike

VERSION: str = "0.1.0"
is_ce: bool = getattr(pygame, "IS_CE", False)

event_ids = _event.__dict__.values()

if TYPE_CHECKING:
    from .ui.default_style_dict import DefaultStyleDict

package = importlib.resources.files("ember")


class DefaultType:
    pass


DEFAULT = DefaultType()


class FocusType:
    pass


FOCUS_CLOSEST = FocusType()
FOCUS_FIRST = FocusType()
FOCUS_LAST = FocusType()


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
    BACKWARD = 9  # Pressing shift + tab
    AXIS_BACKWARD: list["FocusDirection"]
    AXIS_FORWARD: list["FocusDirection"]


FocusDirection.AXIS_BACKWARD = [FocusDirection.LEFT, FocusDirection.UP]
FocusDirection.AXIS_FORWARD = [FocusDirection.RIGHT, FocusDirection.DOWN]

ColorType = Union[
    pygame.Color,
    int,
    str,
    tuple[int, int, int],
    tuple[int, int, int, int],
    Sequence[int],
]

ElementType = Union["Element", str]
SequenceElementType = Union[
    Optional[ElementType],
    Sequence[Optional[ElementType]],
    Generator[Optional[ElementType], None, None],
]

MaterialType = Union["Material", pygame.Surface, str, PathLike]

RectType = Union[Sequence[float], Sequence[int], pygame.Rect, pygame.FRect]


class Error(RuntimeError):
    pass


display_zoom: float = 1
mouse_pos: tuple[int, int] = (0, 0)

clock: Optional[pygame.time.Clock] = None
delta_time: float = 1

views: WeakSet = WeakSet()

default_styles: "DefaultStyleDict"

joysticks: list[pygame.joystick.Joystick] = []

audio_enabled: bool = False
audio_muted: bool = False

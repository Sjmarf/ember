import importlib.resources
from typing import Optional as _Optional

from . import common as _c
from .ui.default_style_dict import DefaultStyleDict as _DefaultStyleDict

_c.default_styles = _DefaultStyleDict()
default_styles = _c.default_styles

from .common import (
    INHERIT,
    Error,
    ColorType,
    joysticks,
    FOCUS_CLOSEST,
    FOCUS_FIRST,
    FocusType,
    BlurMode,
    BLUR_PIL,
    BLUR_PYGAME,
    FocusDirection,
    ESCAPING
)

from . import event
from .event import *

from . import ui
from .ui import *

from . import style
from .style import (
    Style,
    ViewStyle,
    ContainerStyle,
    SectionStyle,
    ButtonStyle,
    TextFieldStyle,
    ToggleStyle,
    SliderStyle,
    TextStyle,
    IconStyle,
    ScrollStyle,
)

from . import font
from .font import Font, PixelFont, IconFont, TextVariant, BOLD, ITALIC, UNDERLINE, STRIKETHROUGH, OUTLINE

from . import state
from .state import State, ButtonState, TextFieldState

from . import material
from . import animation
from . import transition
from . import timer
from . import log

from . import size
from .size import FIT, FILL, Size

from . import position
from .position import (
    Position,
    LEFT,
    RIGHT,
    TOP,
    BOTTOM,
    TOPLEFT,
    TOPRIGHT,
    BOTTOMLEFT,
    BOTTOMRIGHT,
    CENTER,
    MIDLEFT,
    MIDRIGHT,
    MIDTOP,
    MIDBOTTOM,
)

from .utility.stretch_surface import stretch_surface
from .utility.spritesheet import SpriteSheet

import pygame as _pygame
import logging

# logging.basicConfig(level=logging.DEBUG)


def mute_audio(muted: bool) -> None:
    if not (_c.audio_enabled or muted):
        logging.warning("Cannot unmute audio because audio hasn't been loaded.")
        return
    _c.audio_muted = muted


def set_display_zoom(value: float) -> None:
    if _c.display_zoom != value:
        _c.display_zoom = value
        update_views()


def update_views() -> None:
    for view in _c.views:
        view.update_elements()


def update() -> None:
    _c.delta_time = 1 / max(1.0, _c.clock.get_fps())


def init(
    clock: _Optional[_pygame.time.Clock] = None, audio: _Optional[bool] = None
) -> None:
    if audio:
        pygame.mixer.init()
    pygame.scrap.init()
    _c.audio_enabled = audio
    _c.audio_muted = False
    _c.clock = clock if clock is not None else _c.clock

    _c.package = importlib.resources.files("ember")


def set_clock(clock: pygame.time.Clock) -> None:
    _c.clock = clock


print("Ember 0.0.1")

from . import common as _c

from .common import (
    DEFAULT,
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
    package,
)

from . import event
from .event import *

from . import ui
from .ui import *

from . import base
from .base import *

from . import trait
from .trait import new_trait

from . import font
from .font import (
    Font,
    PixelFont,
    IconFont,
    TextVariant,
    BOLD,
    ITALIC,
    UNDERLINE,
    STRIKETHROUGH,
    OUTLINE,
)

from . import material
from . import animation

from . import log

from . import style

from . import size
from .size import FIT, FILL, Size, ClampedSize, RATIO

from .on_event import on_event

from . import size
from .size import FIT, FILL
from . import position
from .position import (
    LEFT,
    RIGHT,
    TOP,
    BOTTOM,
    CENTER,
    TOPLEFT,
    TOPRIGHT,
    BOTTOMLEFT,
    BOTTOMRIGHT,
    MIDTOP,
    MIDLEFT,
    MIDRIGHT,
    MIDBOTTOM,
)
from . import spacing
from .spacing import DEFAULT_SPACING

from .utility.stretch_surface import stretch_surface
from .utility.spritesheet import SpriteSheet

import logging

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


def set_clock(clock: pygame.time.Clock) -> None:
    _c.clock = clock


print("Ember 0.0.1")

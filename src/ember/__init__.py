import importlib.resources
from typing import Union, Optional

from . import common as _c
from .common import INHERIT, Error

from . import event
from .event import *

from . import material

from . import ui
from .ui import *

from . import transition
from . import style
from . import font
from . import size
from . import state
from .size import FIT, FILL, Size

from . import position
from .position import Position, LEFT, RIGHT, TOP, BOTTOM, TOPLEFT, TOPRIGHT, \
     BOTTOMLEFT, BOTTOMRIGHT, CENTER, MIDLEFT, MIDRIGHT, MIDTOP, MIDBOTTOM

from .utility.stretch_surface import stretch_surface
from .utility.spritesheet import SpriteSheet

import pygame as _pygame
import logging

#logging.basicConfig(level=logging.DEBUG)

def mute_audio(muted: bool):
    if not (_c.audio_enabled or muted):
        logging.warning("Cannot unmute audio because audio hasn't been loaded.")
        return
    _c.audio_muted = muted

def set_display_zoom(value: float):
    _c.display_zoom = value
    update_views()

def update_views() -> None:
    for view in _c.views:
        view.update_elements()

def update():
    _c.delta_time = 1 / max(1.0, _c.clock.get_fps())


def init(clock: Optional[_pygame.time.Clock] = None, audio: Optional[bool] = None):
    if audio:
        pygame.mixer.init()
    pygame.scrap.init()
    _c.audio_enabled = audio
    _c.audio_muted = False
    _c.clock = clock if clock is not None else _c.clock

    _c.package = importlib.resources.files("ember")


def set_clock(clock: pygame.time.Clock):
    _c.clock = clock


print('Ember 0.0.1')

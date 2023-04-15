import importlib.resources
from typing import Union, Optional

from . import common as _c
from .common import DEFAULT, INHERIT

from . import event
from .event import *

from . import ui
from .ui import *

from . import transition
from . import display
from . import style
from . import material
from . import font
from . import size
from .size import FIT, FILL

from .utility.size_element import size_element
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

def update():
    mouse = pygame.mouse.get_pos()
    _c.mouse_pos = mouse[0] // _c.display_zoom, mouse[1] // _c.display_zoom


def init(clock: Optional[_pygame.time.Clock] = None, audio: Optional[bool] = None):
    _c.audio_enabled = audio if audio is not None else (_pygame.mixer.get_init() is not None)
    pygame.scrap.init()
    _c.audio_muted = False
    _c.clock = clock if clock is not None else _c.clock

    _c.package = importlib.resources.files("ember")


def set_clock(clock: pygame.time.Clock):
    _c.clock = clock


print('Ember 0.0.1')

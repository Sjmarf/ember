import importlib.resources
from typing import Union, Optional

from ember import common as _c

import ember.event
from ember.event import *

import ember.ui
from ember.ui import *

from ember import transition
from ember import display
from ember import style
from ember import material
from ember import font
from ember import size

from ember.size import FIT, FILL

from ember.utility.size_element import size_element
from ember.utility.spritesheet import SpriteSheet

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
    _c.is_ce = getattr(_pygame, "IS_CE", False)

    _c.package = importlib.resources.files("ember")


def set_clock(clock: pygame.time.Clock):
    _c.clock = clock


print('pxui 0.0.1')

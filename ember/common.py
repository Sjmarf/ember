import pygame
from typing import Optional
from ember.style import *

VERSION: str = "0.1"
is_ce: bool = False

display_zoom: float = 1

# TODO: rework how these are stored
mouse_pos: tuple[int, int] = (0, 0)
clock: Optional[pygame.time.Clock] = None
delta_time: float = 1

# Path to the library. It is an importlib Traversable object, but I can't work out how to typehint it
package = None

# Populated in View.__init__. Maybe that should be changed?
event_ids: list = []

audio_enabled: bool = False
audio_muted: bool = False

default_view_style: Optional[ViewStyle] = None
default_text_style: Optional[TextStyle] = None
default_button_style: Optional[ButtonStyle] = None
default_text_field_style: Optional[TextFieldStyle] = None
default_toggle_style: Optional[ToggleStyle] = None
default_slider_style: Optional[SliderStyle] = None
default_list_style: Optional[ListStyle] = None
default_scroll_style: Optional[ScrollStyle] = None

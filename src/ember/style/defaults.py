"""
The default Style objects.
"""

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ember.style import *

view: Optional["ViewStyle"] = None

container: Optional["ContainerStyle"] = None
scroll: Optional["ScrollStyle"] = None

text: Optional["TextStyle"] = None
button: Optional["ButtonStyle"] = None
text_field: Optional["TextFieldStyle"] = None
toggle: Optional["ToggleStyle"] = None
slider: Optional["SliderStyle"] = None

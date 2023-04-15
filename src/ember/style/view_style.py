from typing import Optional, TYPE_CHECKING

from .. import common as _c

from .style import Style, MaterialType
from .load_material import load_material

if TYPE_CHECKING:
    from ..transition.transition import Transition


class ViewStyle(Style):
    def __init__(self,
                 background: MaterialType = None,
                 transition: Optional["Transition"] = None,
                 transition_in: Optional["Transition"] = None,
                 transition_out: Optional["Transition"] = None
                 ):
        self.background = load_material(background, None)
        self.transition_in = transition_in if transition_in else transition
        self.transition_out = transition_out if transition_out else transition

    def set_as_default(self):
        _c.default_view_style = self

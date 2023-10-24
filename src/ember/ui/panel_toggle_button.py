from typing import Optional

from .panel_button import PanelButton
from .toggle_button import ToggleButton

from ..common import MaterialType

from ..material import Material
from ..material.blank import Blank

from ..utility.load_material import load_material


class PanelToggleButton(PanelButton, ToggleButton):
    ...

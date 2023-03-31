from typing import Optional

from ember import common as _c

from ember.style.style import Style
from ember.material.material import Material


class ListStyle(Style):
    def __init__(self,
                 highlight_material: Optional[Material] = None,
                 highlight_focus_material: Optional[Material] = None,
                 default_text_height: Optional[int] = None):

        self.highlight_material = highlight_material
        self.highlight_focus_material = highlight_focus_material if highlight_focus_material else highlight_material
        self.default_text_height = default_text_height

    def set_as_default(self):
        _c.default_list_style = self

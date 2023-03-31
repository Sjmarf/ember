from typing import Optional

from ember import common as _c
from ember.style.style import Style

from ember.style.load_material import load_material
from ember.material.material import Material


class ScrollStyle(Style):
    def __init__(self,
                 base_image: Optional[Material] = None,
                 default_image: Optional[Material] = None,
                 hover_image: Optional[Material] = None,

                 scrollbar_width: int = 3,
                 padding: int = 10,
                 scroll_speed: int = 5):

        default_image = load_material(default_image,None)
        self.images = [load_material(base_image, None),
                       default_image,
                       load_material(hover_image,default_image)]

        self.scrollbar_width = scrollbar_width
        self.padding = padding
        self.scroll_speed = scroll_speed

    def set_as_default(self):
        _c.default_scroll_style = self

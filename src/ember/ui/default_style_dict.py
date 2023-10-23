from collections import UserDict
from typing import Type, Optional, TYPE_CHECKING
import inspect

from . import *

if TYPE_CHECKING:
    from ember.ui.element import Element

class DefaultStyleDict(UserDict):
    def get(self, element_type: Type["Element"]) -> Optional[Style]:
        for cls in inspect.getmro(element_type):
            if cls in self.data:
                return self.data[cls]
        return None

    @property
    def view(self) -> Optional[Style]:
        return self.get(ViewLayer)

    @property
    def button(self) -> Optional[Style]:
        return self.get(Button)

    @property
    def text_field(self) -> Optional[Style]:
        return self.get(TextField)

    @property
    def toggle(self) -> Optional[Style]:
        return self.get(Toggle)

    @property
    def slider(self) -> Optional[Style]:
        return self.get(Slider)

    @property
    def text(self) -> Optional[Style]:
        return self.get(Text)

    @property
    def icon(self) -> Optional[Style]:
        return self.get(Icon)
    
    @property
    def container(self) -> Optional[Style]:
        return self.get(Container)

    @property
    def section(self) -> Optional[Style]:
        return self.get(Section)

    @property
    def scroll(self) -> Optional[Style]:
        return self.get(Scroll)

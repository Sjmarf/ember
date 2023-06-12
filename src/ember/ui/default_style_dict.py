from collections import UserDict
from typing import Type, Optional
import inspect

from . import *
from ..style import *


class DefaultStyleDict(UserDict):
    def get(self, element_type: Type[Element]) -> Optional[Style]:
        for cls in inspect.getmro(element_type):
            if cls in self.data:
                return self.data[cls]
        return None

    @property
    def view(self) -> Optional[ViewStyle]:
        return self.get(ViewLayer)

    @property
    def button(self) -> Optional[ButtonStyle]:
        return self.get(Button)

    @property
    def text_field(self) -> Optional[TextFieldStyle]:
        return self.get(TextField)

    @property
    def toggle(self) -> Optional[ToggleStyle]:
        return self.get(Toggle)

    @property
    def slider(self) -> Optional[SliderStyle]:
        return self.get(Slider)

    @property
    def text(self) -> Optional[TextStyle]:
        return self.get(Text)

    @property
    def container(self) -> Optional[ContainerStyle]:
        return self.get(Container)

    @property
    def section(self) -> Optional[SectionStyle]:
        return self.get(Section)

    @property
    def scroll(self) -> Optional[ScrollStyle]:
        return self.get(Scroll)

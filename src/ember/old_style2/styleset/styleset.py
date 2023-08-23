from abc import ABC, abstractmethod
from typing import Optional

import pygame

from ..style import Style
from ...ui import *


class StyleSet(ABC):
    @abstractmethod
    def set_as_default(self) -> None:
        ...

    @abstractmethod
    def load(self) -> None:
        ...


class CompleteStyleSet(StyleSet, ABC):
    def __init__(self, background_color: pygame.Color) -> None:
        self.background_color: pygame.Color = background_color
        self.text_style: Optional[Style[Text]] = None
        self.icon_style: Optional[Style[Icon]] = None
        self.button_style: Optional[Style[Button]] = None
        self.slider_style: Optional[Style[Slider]] = None
        self.scroll_style: Optional[Style[Scroll]] = None

    def load(self) -> None:
        self.load_text()
        self.load_icon()
        self.load_button()
        self.load_slider()
        self.load_scroll()

    @abstractmethod
    def load_text(self) -> None:
        ...

    @abstractmethod
    def load_icon(self) -> None:
        ...

    @abstractmethod
    def load_button(self) -> None:
        ...

    @abstractmethod
    def load_slider(self) -> None:
        ...

    @abstractmethod
    def load_scroll(self) -> None:
        ...

    def set_as_default(self) -> None:
        if self.text_style is not None:
            self.text_style.set_as_default()
        if self.icon_style is not None:
            self.icon_style.set_as_default()
        if self.button_style is not None:
            self.button_style.set_as_default()
        if self.slider_style is not None:
            self.slider_style.set_as_default()
        if self.scroll_style is not None:
            self.scroll_style.set_as_default()


class ExtendedStyleSet(CompleteStyleSet):
    def __init__(self, background_color: pygame.Color) -> None:
        super().__init__(background_color)
        self.switch_style: Optional[Style[Toggle]] = None

    def load(self) -> None:
        super().load()
        self.load_switch()

    @abstractmethod
    def load_switch(self) -> None:
        ...

    def set_as_default(self) -> None:
        super().set_as_default()
        if self.switch_style is not None:
            self.switch_style.set_as_default()

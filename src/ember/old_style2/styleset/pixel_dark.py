import pygame

from ...common import package
from ...size import FILL
from ... import ui
from ... import font
from ... import material
from ..text_style import TextStyle
from ..icon_style import IconStyle
from ..button_style import ButtonStyle
from ..switch_style import SwitchStyle
from ..slider_style import SliderStyle
from ..scroll_style import ScrollStyle
from .styleset import ExtendedStyleSet


class PixelDark(ExtendedStyleSet):
    def __init__(self):
        super().__init__(background_color=pygame.Color([40, 40, 50]))

    def load_text(self) -> None:
        self.text_style = TextStyle(
            font=font.PixelFont(path=package.joinpath(f"default_fonts/pixel")),
            color="white",
        )

    def load_icon(self) -> None:
        self.icon_style = IconStyle(
            font=font.IconFont(path=package.joinpath(f"default_icon_fonts/pixel")),
            color="white",
        )

    def load_button(self) -> None:
        root = package / "stylesets/pixel_dark/button"
        self.button_style = ButtonStyle(
            size=(100, 20),
            content_size=(FILL - 4, FILL - 5),
            content_y=2,
            content_y_clicked=3,
            default_material=root / "default.png",
            hover_material=root / "hover.png",
            click_material=root / "click.png",
            focus_material=root / "focus.png",
            focus_click_material=root / "focus_click.png",
            disabled_material=root / "disabled.png",
        )

    def load_switch(self) -> None:
        root = package / "stylesets/pixel_dark/toggle"

        self.switch_style = SwitchStyle(
            size=(30, 15),
            default_material=root / "base.png",
            default_handle_material=root / "default.png",
            hover_handle_material=root / "hover.png",
            focus_handle_material=root / "focus.png",
            disabled_handle_material=root / "disabled.png",
        )

    def load_slider(self) -> None:
        root = package / "stylesets/pixel_dark/slider"

        self.slider_style = SliderStyle(
            size=(90, 15),
            default_material=root / "base.png",
            default_handle_material=root / "default.png",
            hover_handle_material=root / "hover.png",
            click_handle_material=root / "click.png",
            focus_handle_material=root / "focus.png",
            focus_click_handle_material=root / "focus_click.png",
            disabled_handle_material=root / "disabled.png",
        )

    def load_scroll(self) -> None:
        if self.slider_style is None:
            self.load_slider()

        self.scroll_style = ScrollStyle()

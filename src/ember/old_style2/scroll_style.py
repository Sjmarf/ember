import pygame
from typing import Optional, TYPE_CHECKING

from ember.style.style import Style
from ..ui.base.scroll import Scroll
from ..ui.v_scroll import VScroll
from ..ui.v_slider import VSlider
from ..ui.h_slider import HSlider
from ..event import SCROLLMOVED
from ember.animation.ease import EaseInOut

from ..size import FILL
from ..position import TOPRIGHT

from ember.trait.trait import Trait

if TYPE_CHECKING:
    from ember.animation.animation import Animation


class ScrollStyle(Style[Scroll]):
    def __init__(
        self,
        animation: Optional["Animation"] = None,
    ):
        self.animation = EaseInOut(0.2) if animation is None else animation

        super().__init__()
        self.add_event_callback(self.on_scroll, SCROLLMOVED)

    @staticmethod
    def _get_scrollbar_value(element: Scroll) -> float:
        return element.scroll / element.scrollable_element.get_abs_h()

    def on_scroll(self, element: Scroll, event: Optional[pygame.Event]) -> None:
        if event is not None and event.cause in {
            element.MovementCause.VISIBILITY,
            element.MovementCause.SET,
        }:
            with self.animation:
                element.set_parallel_content_pos(-int(element.scroll))
        else:
            element.set_parallel_content_pos(-int(element.scroll))

        element[0].set_content_h(element.rect.h / element.scrollable_element.rect.h * element.rect.h)

    def _on_become_active(self, element: Scroll, event: Optional[pygame.Event]) -> None:
        cls = VSlider if isinstance(element, VScroll) else HSlider
        slider = cls(
            size=(10, FILL),
            pos=TOPRIGHT,
            min_value=0,
            max_value=1,
            value=self._get_scrollbar_value(element),
        )
        with Trait.inspecting(Trait.Layer.PARENT):
            slider.set_content_h(element.rect.h / element.scrollable_element.get_abs_h(element.rect.h) * element.rect.h)
        element.insert(0, slider)
        element.set_perpendicular_content_size(FILL - 16)
        element.set_perpendicular_content_pos(0)

    def _on_become_deactive(
        self, element: Scroll, event: Optional[pygame.Event]
    ) -> None:
        del element[0]

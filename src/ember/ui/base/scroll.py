import pygame
import abc
import inspect
from typing import TYPE_CHECKING, Optional, Sequence, Union

from ember.common import INHERIT, InheritType

from ember import log

if TYPE_CHECKING:
    from ember.ui.view import ViewLayer
    from ember.style.scroll_style import ScrollStyle
    from ember.state.background_state import BackgroundState

from ember import common as _c
from ember.ui.base.element import Element
from .single_element_container import SingleElementContainer
from ember.material.material import Material
from ember.size import FIT, SizeType, SequenceSizeType, SizeMode
from ember.position import PositionType, CENTER, SequencePositionType, Position

from ember.state.state import load_background

from ember.state.state_controller import StateController

from ember.utility.timer import BasicTimer


class Scroll(SingleElementContainer, abc.ABC):
    """
    A Scroll holds one Element, and allows you to scroll that Element. There are two subclasses of Scroll -
    :py:class:`ember.ui.VScroll` and :py:class:`ember.ui.HScroll`. This base class should not be
    instantiated directly.
    """

    def __init__(
        self,
        element: Optional[Element],
        material: Union["BackgroundState", Material, None] = None,
        over_scroll: Union[InheritType, Sequence[int]] = INHERIT,
        align: Union[InheritType, SequencePositionType] = INHERIT,
        rect: Union[pygame.rect.RectType, Sequence, None] = None,
        pos: Optional[SequencePositionType] = None,
        x: Optional[PositionType] = None,
        y: Optional[PositionType] = None,
        size: Optional[SequenceSizeType] = None,
        width: Optional[SizeType] = None,
        height: Optional[SizeType] = None,
        style: Optional["ScrollStyle"] = None,
    ):
        self.set_style(style)

        self.state_controller: StateController = StateController(self)
        """
        The :py:class:`ember.state.StateController` responsible for managing the Scroll's 
        background states. Read-only.
        """

        self.scrollbar_controller: StateController = StateController(self, materials=2)
        """
        The :py:class:`ember.state.StateController` responsible for managing the Scroll's 
        scrollbar states. Read-only.
        """

        self.can_scroll: bool = False
        """
        Is :code:`True` when the child element is large enough to need scrolling. Read-only.
        """

        self.scrollbar_hovered: bool = False
        """
        Is :code:`True` when the user is hovering over the scrollbar handle. Read-only.
        """

        self.scrollbar_grabbed: bool = False
        """
        Is :code:`True` when the user is moving the scrollbar handle. Read-only.
        """

        self.over_scroll: tuple[int, int] = (
            self._style.over_scroll if over_scroll is INHERIT else over_scroll
        )
        """
        The distance, in pixels, to allow scrolling past the child element. tuple[start, finish].
        """

        self._subsurf: Optional[pygame.Surface] = None

        self._fit_width: int = 0
        self._fit_height: int = 0

        self.layer = None

        self._element: Optional[Element] = None
        self.set_element(element, _update=False)

        self.scroll = BasicTimer(self.over_scroll[0] * -1)
        self._scrollbar_pos: int = 0
        self._scrollbar_size: int = 0
        self._scrollbar_grabbed_pos: int = 0

        super().__init__(material, rect, pos, x, y, size, width, height)

        if not isinstance(align, (Sequence, InheritType)):
            align = (align, align)

        self.align: Sequence[Position] = (
            self._style.align if align is INHERIT else align
        )

    def _render_elements(
        self, surface: pygame.Surface, offset: tuple[int, int], alpha: int = 255
    ) -> None:
        rect = self._int_rect.move(*offset)

        self._element._render_a(self._subsurf, offset, alpha=alpha)

        self._render_scrollbar(surface, rect, alpha)

    @abc.abstractmethod
    def _render_scrollbar(
        self, surface: pygame.Surface, rect: pygame.Rect, alpha: int
    ) -> None:
        pass

    def _check_element(self, max_size: tuple[float, float]) -> None:
        pass

    def _update_rect_chain_down(
        self,
        surface: pygame.Surface,
        pos: tuple[float, float],
        max_size: tuple[float, float],
        _ignore_fill_width: bool = False,
        _ignore_fill_height: bool = False,
    ) -> None:
        self._check_element(max_size)

        super()._update_rect_chain_down(
            surface, pos, max_size, _ignore_fill_width, _ignore_fill_height
        )

        if (
            self._subsurf is None
            or (*self._subsurf.get_abs_offset(), *self._subsurf.get_size()) != self.rect
            or self._subsurf.get_abs_parent() is not surface.get_abs_parent()
        ) and self.is_visible:
            parent_surface = surface.get_abs_parent()
            rect = self.rect.copy().clip(parent_surface.get_rect())
            try:
                self._subsurf = parent_surface.subsurface(rect)
            except ValueError as e:
                log.size.info(self, f"An error occured: {e}")
                self._scrollbar_calc()
                return

        self._scrollbar_calc()
        self._update_element_rect()

    @abc.abstractmethod
    def _update_element_rect(self) -> None:
        pass

    @Element._chain_up_decorator
    def _update_rect_chain_up(self) -> None:
        if self._h.mode == SizeMode.FIT:
            if self._element:
                if self._element._h.mode == SizeMode.FILL:
                    raise ValueError(
                        "Cannot have elements of FILL height inside of a FIT height Scroll."
                    )
                self._fit_height = self._element.get_ideal_height()
            else:
                self._fit_height = 20

        if self._w.mode == SizeMode.FIT:
            if self._element:
                if self._element._w.mode == SizeMode.FILL:
                    raise ValueError(
                        "Cannot have elements of FILL width inside of a FIT width Scroll."
                    )
                self._fit_width = self._element.get_ideal_width()
            else:
                self._fit_width = 20

    def _set_layer_chain(self, layer: "ViewLayer") -> None:
        log.layer.info(self, f"Set layer to {layer}")
        self.layer = layer
        if self._element is not None:
            self._element._set_layer_chain(layer)

    def _focus_chain(
        self, direction: _c.FocusDirection, previous: Optional["Element"] = None
    ) -> "Element":
        if self.layer.element_focused is self:
            log.nav.info(self, f"-> parent {self.parent}.")
            return self.parent._focus_chain(direction, previous=self)

        if (
            direction
            in {
                _c.FocusDirection.LEFT,
                _c.FocusDirection.RIGHT,
                _c.FocusDirection.UP,
                _c.FocusDirection.DOWN,
                _c.FocusDirection.FORWARD,
            }
            or self._element is None
        ):
            log.nav.info(self, f"-> parent {self.parent}.")
            return self.parent._focus_chain(direction, previous=self)

        elif direction == _c.FocusDirection.OUT:
            log.nav.info(self, f"-> parent {self.parent}.")
            return self.parent._focus_chain(direction, previous=self)

        else:
            log.nav.info(self, f"-> child {self._element}.")
            return self._element._focus_chain(direction, previous=self)

    def _event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONUP:
            if self.scrollbar_grabbed:
                self.scrollbar_grabbed = False
                return True

        if self._element is not None:
            # Stops you from clicking on elements that are clipped out of the frame
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not self.rect.collidepoint(_c.mouse_pos):
                    return False
            if self._element._event(event):
                return True

        if self._event2(event):
            return True

        return False

    @abc.abstractmethod
    def _event2(self, event: pygame.event.Event) -> bool:
        pass

    @abc.abstractmethod
    def _scrollbar_calc(self) -> None:
        pass

    def _clamp_scroll_position(self, max_scroll) -> None:
        # If the scrollbar is outside the limits, move it inside.

        if not (-self.over_scroll[0] <= self.scroll.val <= max_scroll):
            if -self.over_scroll[0] == self.scroll.val:
                return
            log.size.info(
                self,
                f"Scrollbar pos {self.scroll.val} is outside limits "
                f"{(-self.over_scroll[0], max_scroll)}, starting chain down...",
            )
            if self.can_scroll:
                self.scroll.val = pygame.math.clamp(
                    self.scroll.val, -self.over_scroll[0], max_scroll
                )
            else:
                self.scroll.val = -self.over_scroll[0]
            if max_scroll <= 0:
                return
            self._update_element_rect()
            self._scrollbar_calc()

    def _set_style(self, style: "ScrollStyle") -> None:
        self.set_style(style)

    def set_style(self, style: "ScrollStyle") -> None:
        """
        Sets the ScrollStyle of the Scroll.
        """
        self._style: "ScrollStyle" = self._get_style(style)

    @abc.abstractmethod
    def scroll_to_show_position(
        self, position: int, size: int = 0, offset: int = 0, duration: float = 0.1
    ) -> None:
        """
        Scroll so that a position is shown within the Scroll.
        """
        pass

    @abc.abstractmethod
    def scroll_to_element(self, element: Element) -> None:
        """
        Scroll so that an element is shown within the Scroll.
        """
        pass

    style: "ScrollStyle" = property(
        fget=lambda self: self._style,
        fset=_set_style,
        doc="The ScrollStyle of the Scroll.",
    )

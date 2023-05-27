import pygame
import abc
from typing import TYPE_CHECKING, Optional, Sequence, Union

from ember.common import INHERIT, InheritType

from ember import log

if TYPE_CHECKING:
    from ember.ui.view import ViewLayer

from ember import common as _c
from ember.ui.base.element import Element
from ember.style.load_style import load as load_style
from ember.material.material import Material
from ember.size import FIT, SizeType
from ember.position import PositionType

from ember.state.state import State, load_background

from ember.style.scroll_style import ScrollStyle

from ember.state.state_controller import StateController

from ember.utility.timer import BasicTimer
from ...style.get_style import _get_style


class Scroll(Element, abc.ABC):
    """
    A Scroll holds one Element, and allows you to scroll that Element. There are two subclasses of Scroll -
    :py:class:`ember.ui.VScroll` and :py:class:`ember.ui.HScroll`. This base class should not be
    instantiated directly.
    """
    def __init__(
        self,
        element: Optional[Element],
        background: Optional[Material] = None,
        focus_self: Union[bool, InheritType] = INHERIT,
        over_scroll: Union[InheritType, tuple[int, int]] = INHERIT,
        position: PositionType = None,
        size: Sequence[SizeType] = (0, 0),
        width: SizeType = None,
        height: SizeType = None,
        style: Optional[ScrollStyle] = None,
    ):
        super().__init__(position, size, width, height, (FIT, 100))

        # Load the ScrollStyle object.
        self.set_style(style)

        self.background: Optional[State] = load_background(self, background)
        """
        The background :py:class:`State<ember.state.State>` of the Scroll. Overrides all ContainerStyle materials.
        """

        self.background_controller: StateController = StateController(self)
        """
        The :py:class:`ember.state.StateController` responsible for managing the Scroll's 
        background states. Read-only.
        """

        self.base_controller: StateController = StateController(self)
        """
        The :py:class:`ember.state.StateController` responsible for managing the Scroll's 
        scrollbar base states. Read-only.
        """

        self.handle_controller: StateController = StateController(self)
        """
        The :py:class:`ember.state.StateController` responsible for managing the Scroll's 
        scrollbar handle states. Read-only.
        """

        self.can_scroll: bool = False
        """
        Is :code:`True` when the child element is large enough to need scrolling. Read-only.
        """

        self.focus_self: bool = (
            self._style.focus_self if focus_self is INHERIT else focus_self
        )
        """
        Modifies how the Scroll behaves with keyboard / controller navigation. If set to True, the Scroll itself 
        is focusable. If you press enter when the Scroll is focused, the first child of the Scroll is focused.
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

        self._element: Optional[Element] = None
        self.set_element(element)

        self.scroll = BasicTimer(self.over_scroll[0] * -1)
        self._scrollbar_pos: int = 0
        self._scrollbar_size: int = 0
        self._scrollbar_grabbed_pos: int = 0

    def _render(
        self, surface: pygame.Surface, offset: tuple[int, int], alpha: int = 255
    ) -> None:
        rect = self._draw_rect.move(*offset)

        self.background_controller.render(
            self._style.state_func(self),
            surface,
            (
                rect.x - surface.get_abs_offset()[0],
                rect.y - surface.get_abs_offset()[1],
            ),
            rect.size,
            alpha,
        )

        if not self._element:
            return

        # Render element
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
            (self._subsurf is None
            or (*self._subsurf.get_abs_offset(), *self._subsurf.get_size()) != self.rect
            or self._subsurf.get_abs_parent() is not surface.get_abs_parent())
            and self.is_visible
        ):
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
        if self._height.mode == 1:
            if self._element:
                if self._element._height.mode == 2:
                    raise ValueError(
                        "Cannot have elements of FILL height inside of a FIT height Scroll."
                    )
                self._fit_height = self._element.get_abs_height()
            else:
                self._fit_height = 20

        if self._width.mode == 1:
            if self._element:
                if self._element._width.mode == 2:
                    raise ValueError(
                        "Cannot have elements of FILL width inside of a FIT width Scroll."
                    )
                self._fit_width = self._element.get_abs_width()
            else:
                self._fit_width = 20

    def _set_layer_chain(self, layer: "ViewLayer") -> None:
        log.layer.info(self, f"Set layer to {layer}")
        self.layer = layer
        if self._element is not None:
            self._element._set_layer_chain(layer)

    def _focus_chain(
        self, previous: Optional[Element] = None, direction: str = "in"
    ) -> Element:
        if self.layer.element_focused is self:
            log.nav.info(self, f"-> parent {self.parent}.")
            return self.parent._focus_chain(self, direction=direction)

        if (
            direction in {"up", "down", "left", "right", "forward"}
            or self._element is None
        ):
            log.nav.info(self, f"-> parent {self.parent}.")
            return self.parent._focus_chain(self, direction=direction)

        elif direction == "out":
            if self.focus_self:
                log.nav.info(self, f"Returning self.")
                return self
            else:
                log.nav.info(self, f"-> parent {self.parent}.")
                return self.parent._focus_chain(self, direction=direction)

        else:
            if self.focus_self:
                log.nav.info(self, f"Returning self.")
                return self

            log.nav.info(self, f"-> child {self._element}.")
            return self._element._focus_chain(None, direction=direction)

    def _event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONUP:
            if self.scrollbar_grabbed:
                self.scrollbar_grabbed = False
                return True

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self.layer.element_focused is self:
                    log.nav.info(self, "Enter key pressed, starting focus chain.")
                    with log.nav.indent:
                        self.layer._focus_element(
                            self._element._focus_chain(self, direction="in_first")
                        )
                    log.nav.info(
                        self,
                        f"Focus chain ended. Focused {self.layer.element_focused}.",
                    )
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

    def _set_element(self, element: Optional[Element]) -> None:
        self.set_element(element)

    def set_element(self, element: Optional[Element]) -> None:
        """
        Replace the child element of the Scroll.
        """
        if element is not self._element:
            self._element = element
            if element is not None:
                self._can_focus = element._can_focus
                self._element._set_parent(self)
                log.layer.line_break()
                log.layer.info(self, "Element added to Scroll - starting chain...")
                with log.layer.indent:
                    self._element._set_layer_chain(self.layer)
                log.size.info(self, "Element set, starting chain up...")
                with log.size.indent:
                    self._update_rect_chain_up()

            else:
                self._can_focus = False

    def _set_style(self, style: ScrollStyle) -> None:
        self.set_style(style)

    def set_style(self, style: ScrollStyle) -> None:
        """
        Sets the ScrollStyle of the Scroll.
        """
        self._style = _get_style(style, "scroll")

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

    element: Optional[Element] = property(
        fget=lambda self: self._element,
        fset=_set_element,
        doc="The element contained in the Scroll.",
    )

    style: ScrollStyle = property(
        fget=lambda self: self._style,
        fset=_set_style,
        doc="The ScrollStyle of the Scroll.",
    )

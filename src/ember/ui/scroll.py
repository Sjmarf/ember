import pygame
from typing import TYPE_CHECKING, Optional, Sequence, NoReturn, Union

from ..common import INHERIT, InheritType

from .. import log

if TYPE_CHECKING:
    from .view import View

from .. import common as _c
from .element import Element
from ..style.load_style import load as load_style
from ..material.material import MaterialController, Material
from ..size import FIT, SizeType

from ..style.scroll_style import ScrollStyle

from ..utility.timer import BasicTimer


class Scroll(Element):
    def __init__(self,
                 element: Optional[Element],
                 size: Sequence[SizeType] = (0, 0),
                 width: SizeType = None,
                 height: SizeType = None,

                 style: Optional[ScrollStyle] = None,

                 background: Optional[Material] = None,
                 focus_self: bool = False,
                 over_scroll: Union[InheritType, tuple[int, int]] = INHERIT
                 ):

        super().__init__(size, width, height, (FIT, 100))

        # Load the ScrollStyle object.
        if style is None:
            if _c.default_scroll_style is None:
                load_style("plastic", parts=['scroll'])
            self._style: ScrollStyle = _c.default_scroll_style
        else:
            self._style: ScrollStyle = style

        self.subsurf: Optional[pygame.Surface] = None

        self.background: Optional[Material] = background
        self.background_controller: MaterialController = MaterialController(self)

        self.base_controller: MaterialController = MaterialController(self)
        self.handle_controller: MaterialController = MaterialController(self)

        self.focus_self: bool = focus_self

        self.over_scroll: tuple[int, int] = self._style.over_scroll if over_scroll is INHERIT else over_scroll

        self._fit_width: int = 0
        self._fit_height: int = 0

        self._element: Optional[Element] = None
        self.set_element(element)

        self.scroll = BasicTimer(self.over_scroll[0] * -1)
        self.can_scroll: bool = False
        self._scrollbar_pos: int = 0
        self._scrollbar_size: int = 0
        self.scrollbar_hovered: bool = False
        self.scrollbar_grabbed: bool = False
        self._scrollbar_grabbed_pos: int = 0

    def set_element(self, element: Optional[Element]) -> NoReturn:
        """
        Replace the child element of the Scroll.
        """
        if element is not self._element:
            self._element = element
            if element is not None:
                self.can_focus = element._can_focus
                self._element._set_parent(self)
            else:
                self.can_focus = False

    def _update_rect_chain_up(self) -> NoReturn:
        if self._height.mode == 1:
            if self._element:
                if self._element._height.mode == 2:
                    raise ValueError("Cannot have elements of FILL height inside of a FIT height VScroll.")
                self._fit_height = self._element.get_abs_height(0)
            else:
                self._fit_height = 20

        if self._width.mode == 1:
            if self._element:
                if self._element._width.mode == 2:
                    raise ValueError("Cannot have elements of FILL width inside of a FIT width VScroll.")
                self._fit_width = self._element.get_abs_width(0)
            else:
                self._fit_width = 20

        if self._element:
            self.can_focus = self._element._can_focus
        if hasattr(self.parent, "update_rect_chain_up"):
            self.parent._update_rect_chain_up()

    def _update_rect_chain_down(self, surface: pygame.Surface, pos: tuple[float, float], max_size: tuple[float, float],
                                root: "View", _ignore_fill_width: bool = False,
                                _ignore_fill_height: bool = False) -> NoReturn:

        if hasattr(self._element, "check_for_surface_update"):
            log.size.info(self, "Checking element surface update...")
            self._element.check_for_surface_update()
        super()._update_rect_chain_down(surface, pos, max_size, root, _ignore_fill_width, _ignore_fill_height)

        if self.subsurf is None or (*self.subsurf.get_abs_offset(), *self.subsurf.get_size()) != self.rect:
            self.subsurf = surface.subsurface(self.rect)

        self._update_element_rect()

    def _update_element_rect(self):
        pass

    def _render(self, surface: pygame.Surface, offset: tuple[int, int], root: "View", alpha: int = 255) -> NoReturn:
        rect = self.rect.move(*offset)

        if self.background:
            self.background_controller.set_material(self.background, self._style.material_transition)
        elif root.element_focused is self:
            self.background_controller.set_material(self._style.focus_material,
                                                    self._style.material_transition)
        elif root.element_focused is not None and self in root.element_focused.get_parent_tree():
            self.background_controller.set_material(self._style.focus_child_material,
                                                    self._style.material_transition)
        else:
            self.background_controller.set_material(self._style.material, self._style.material_transition)

        self.background_controller.render(self, surface, (rect.x - surface.get_abs_offset()[0],
                                                          rect.y - surface.get_abs_offset()[1]),
                                          rect.size, alpha)

        if not self._element:
            return

        # Render element
        self._element._render_a(self.subsurf, offset, root, alpha=alpha)

        self._render_scrollbar(surface, rect, alpha)

    def _scrollbar_calc(self) -> NoReturn:
        pass

    def _clamp_scroll_position(self, max_scroll) -> NoReturn:
        # If the scrollbar is outside the limits, move it inside.
        if max_scroll <= 0:
            return
        if not (-self.over_scroll[0] <= self.scroll.val <= max_scroll):
            log.size.info(self, f"Scrollbar pos {self.scroll.val} is outside limits "
                                f"{(-self.over_scroll[0], max_scroll)}, starting chain down...")
            if self.can_scroll:
                self.scroll.val = pygame.math.clamp(self.scroll.val, -self.over_scroll[0], max_scroll)
            else:
                self.scroll.val = -self.over_scroll[0]
            self._update_element_rect()

    def _render_scrollbar(self, surface: pygame.Surface, rect: pygame.Rect, alpha: int) -> NoReturn:
        pass

    def _event2(self, event: pygame.event.Event, root: "View") -> NoReturn:
        pass

    def _event(self, event: pygame.event.Event, root: "View") -> NoReturn:
        if self._event2(event, root):
            return True

        if event.type == pygame.MOUSEBUTTONUP:
            if self.scrollbar_grabbed:
                self.scrollbar_grabbed = False
                return True

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if root.element_focused is self:
                    log.nav.info(self, "Enter key pressed, starting focus chain.")
                    with log.nav.indent:
                        root.element_focused = self._element._focus_chain(root, self, direction='in_first')
                    log.nav.info(self, f"Focus chain ended. Focused {root.element_focused}.")
                    return True

        if self._element is not None:
            # Stops you from clicking on elements that are clipped out of the frame
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not self.rect.collidepoint(_c.mouse_pos):
                    return
            self._element._event(event, root)

    def _focus_chain(self, root: "View", previous: Optional[Element] = None, direction: str = 'in') -> NoReturn:
        if root.element_focused is self:
            log.nav.info(self, f"-> parent {self.parent}.")
            return self.parent._focus_chain(root, self, direction=direction)

        if direction in {'up', 'down', 'left', 'right', 'forward'} or self._element is None:
            log.nav.info(self, f"-> parent {self.parent}.")
            return self.parent._focus_chain(root, self, direction=direction)

        elif direction == "out":
            if self.focus_self:
                log.nav.info(self, f"Returning self.")
                return self
            else:
                log.nav.info(self, f"-> parent {self.parent}.")
                return self.parent._focus_chain(root, self, direction=direction)

        else:
            if self.focus_self:
                log.nav.info(self, f"Returning self.")
                return self

            log.nav.info(self, f"-> child {self._element}.")
            return self._element._focus_chain(root, None, direction=direction)

    def _set_style(self, style: ScrollStyle) -> NoReturn:
        self.set_style(style)

    def set_style(self, style: ScrollStyle) -> NoReturn:
        """
        Sets the ScrollStyle of the Scroll.
        """
        self._style = style

    def scroll_to_show_position(self, position: int, size: int = 0, offset: int = 0, duration: float = 0.1):
        """
        Scroll so that a position is shown within the Scroll.
        """
        pass

    def scroll_to_element(self, element: Element) -> NoReturn:
        """
        Scroll so that an element is shown within the Scroll.
        """
        pass

    element: Optional[Element] = property(
        fget=lambda self: self._element,
        fset=set_element,
        doc="The element contained in the Scroll."
    )

    style: ScrollStyle = property(
        fget=lambda self: self._style,
        fset=_set_style,
        doc="The ScrollStyle of the Scroll."
    )

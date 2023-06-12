import pygame
import inspect
import copy
from typing import Union, TYPE_CHECKING, Optional, Sequence, TypeVar
from ember import log

from ember.event import TRANSITIONFINISHED, ELEMENTUNFOCUSED, ELEMENTFOCUSED

if TYPE_CHECKING:
    from ember.ui.view import View, ViewLayer
    from ember.transition.transition import Transition, TransitionController
    from ...style.style import Style

from ember.size import Size, SizeType, SequenceSizeType, create_range, SizeRange
from ember.position import PositionType, SequencePositionType, Position, CENTER

from ... import common as _c


class Element:
    """
    The base element class. All UI elements in the library inherit from this class.
    """

    def __init__(
        self,
        rect: Union[pygame.rect.RectType, Sequence, None] = None,
        pos: Optional[SequencePositionType] = None,
        x: Optional[PositionType] = None,
        y: Optional[PositionType] = None,
        size: Optional[SequenceSizeType] = None,
        width: Optional[SizeType] = None,
        height: Optional[SizeType] = None,
        default_size: Optional[Sequence[SizeType]] = None,
        can_focus: bool = True,
    ):
        self.layer: Optional[ViewLayer] = None
        """
        The View that the Element is (directly or indirectly) attributed to.
        """

        self.parent: Optional[Element] = None
        """
        The Element or View that the Element is directly attributed to. For example, if the Element is placed 
        inside of a VStack, it's :code:`parent` would be that VStack object.
        """

        self.is_visible: bool = True
        """
        Is :code:`True` when any part of the element is visible on the screen. Read-only.
        """

        self.rect = pygame.FRect(0, 0, 0, 0)
        """
        A :code:`pygame.FRect` object containing the absolute position and size of the element. Read-only.
        """

        self._int_rect = pygame.Rect(0, 0, 0, 0)

        self._can_focus: bool = can_focus

        if rect is not None:
            x, y, width, height = rect[:]

        if pos is not None:
            if isinstance(pos, Sequence):
                x, y = pos
            else:
                x, y = pos, pos

        self.set_pos(x, y, _update=False)

        if default_size is None:
            default_size = self._style.size

        if size is None:
            if width is None:
                width = default_size[0]
            if height is None:
                height = default_size[1]
        else:
            if isinstance(size, Sequence):
                width, height = size
            else:
                width, height = size, size

        self.set_size(width, height, _update=False)

        self._transition: Optional["TransitionController"] = None

    def _update_rect(self, x: float, y: float, w: float, h: float) -> None:
        self.rect.update(x, y, w, h)
        self._int_rect.update(
            round(self.rect.x),
            round(self.rect.y),
            round(self.rect.w),
            round(self.rect.h),
        )

    def _update_rect_chain_down(
        self,
        surface: pygame.Surface,
        pos: tuple[float, float],
        max_size: tuple[float, float],
        _ignore_fill_width: bool = False,
        _ignore_fill_height: bool = False,
    ) -> None:
        """
        Used internally by the library. Calling this method calls the same method for the element's child elements.
        """

        self._update_rect(
            *pos,
            self.get_ideal_width(max_size[0], _ignore_fill_width=_ignore_fill_width),
            self.get_ideal_height(max_size[1], _ignore_fill_height=_ignore_fill_height),
        )

        log.size.info(self, f"Chain down {self.rect[:]}, visible = {self.is_visible}.")

    def _update_rect_chain_up(self) -> None:
        """
        Used internally by the library. Calling this method calls the same method for the container that the element
        is inside.
        """
        pass

    @staticmethod
    def _chain_up_decorator(func: callable) -> callable:
        def wrapper(self) -> None:
            old_width, old_height = self._fit_width, self._fit_height
            log.size.info(self, "Chain up.")
            cut_chain = False

            func(self)

            if old_width != self._fit_width and old_height != self._fit_height:
                log.size.info(
                    self,
                    f"Fit size changed from {(old_width, old_height)} to "
                    f"{self._fit_width, self._fit_height}.",
                )
            elif old_width != self._fit_width:
                log.size.info(
                    self, f"Fit width changed from {old_width} to {self._fit_width}."
                )
            elif old_height != self._fit_height:
                log.size.info(
                    self, f"Fit height changed from {old_height} to {self._fit_height}."
                )
            else:
                cut_chain = True

            if self.parent:
                if cut_chain:
                    if self._fit_width == 1 or self._fit_height == 1:
                        log.size.info(self, "Size wasn't changed - cutting chain...")
                    else:
                        log.size.info(
                            self, "Element doesn't have FIT size - cutting chain..."
                        )
                else:
                    log.size.info(self, f"-> parent {self.parent}.")
                    with log.size.indent:
                        self.parent._update_rect_chain_up()
            else:
                log.size.info(self, "No parent - cutting chain...")
                return

            if self.layer:
                if self.layer._chain_down_from is None:
                    log.size.info(self, "Starting chain down next tick...")
                self.layer._chain_down_from = self.parent
            else:
                log.size.info(self, "No layer - check_size was not set.")

        return wrapper

    def _render_a(
        self, surface: pygame.Surface, offset: tuple[int, int], alpha: int = 255
    ) -> None:
        """
        Used internally by the libray. Renders the element, with transitions taken into consideration.
        :param offset:
        :param surface:
        :param alpha:
        :return:
        """

        if self._transition is not None:
            self._transition.render(surface, offset, alpha=alpha)
        else:
            self._render(surface, offset, alpha=alpha)

    def _render(
        self, surface: pygame.Surface, offset: tuple[int, int], alpha: int = 255
    ) -> None:
        """
        Used intenally by the library.
        """
        pass

    def _update_a(self) -> None:
        """
        Used internally by the library. Updates the element, with transitions taken into consideration.
        """
        if self._transition is not None:
            self._transition.update()
            if self._transition.timer <= 0:
                new_event = pygame.event.Event(
                    TRANSITIONFINISHED, element=self, controller=self._transition
                )
                self._transition = None
                pygame.event.post(new_event)
        else:
            self._update()

    def _update(self) -> None:
        """
        Used intenally by the library.
        """
        pass

    def _set_layer_chain(self, layer: "ViewLayer") -> None:
        """
        Sets the 'layer' attribute of the element, and all of its children, to the specified ViewLayer.
        """
        log.layer.info(self, f"Set layer to {layer}")
        self.layer = layer

    def _focus_chain(
        self, direction: _c.FocusDirection, previous: Optional["Element"] = None
    ) -> "Element":
        # 'previous' is used for going back up the chain - it is set to None when going downwards

        if direction in {
            _c.FocusDirection.IN,
            _c.FocusDirection.IN_FIRST,
            _c.FocusDirection.SELECT,
        }:
            log.nav.info(self, "Returning self.")
            return self
        elif self.parent:
            # Go up a level and try again
            log.nav.info(self, f"-> Parent {self.parent}.")
            return self.parent._focus_chain(direction, previous=self)

    def _event(self, event: pygame.event.Event) -> bool:
        """
        Called by the parent of the element for each Pygame event,
        with the pygame event object passed to the method.
        """
        return False

    def _on_unfocus(self) -> None:
        """
        Called by ViewLayer when the element is unfocused. For internal use only.
        """
        pass

    def _set_parent(self, parent: Union["Element", "ViewLayer"]) -> None:
        """
        Used internally by the library. You don't need to call this.
        """
        self.parent = parent

    def _get_style(self, style: Optional["Style"], *classes):
        """
        Used interally by the library.
        """
        if style is None:
            for cls in classes if classes else inspect.getmro(type(self)):
                if cls in _c.default_styles:
                    return _c.default_styles[cls]
            raise _c.Error(
                f"Tried to find a style for {type(self).__name__}, but no style was found."
            )
        else:
            return style

    def set_pos(self, *pos: SequencePositionType, _update=True) -> None:
        """
        Set the position of the element.
        """
        if isinstance(pos[0], Sequence):
            pos = pos[0]

        self._x: Position = (
            Position(pos[0]) if isinstance(pos[0], (int, float)) else pos[0]
        )
        self._y: Position = (
            Position(pos[1]) if isinstance(pos[1], (int, float)) else pos[1]
        )
        if _update:
            self._update_rect_chain_up()

    def set_x(self, value: PositionType, _update=True) -> None:
        """
        Set the x position of the element.
        """
        self._x: Position = (
            Position(value) if isinstance(value, (int, float)) else value
        )
        if _update:
            self._update_rect_chain_up()

    def set_y(self, value: PositionType, _update=True) -> None:
        """
        Set the y position of the element.
        """
        self._y: Position = (
            Position(value) if isinstance(value, (int, float)) else value
        )
        if _update:
            self._update_rect_chain_up()

    def set_size(self, *size: SequenceSizeType, _update=True) -> None:
        """
        Set the size of the element.
        """
        if isinstance(size[0], Sequence):
            size = size[0]

        self._w: SizeRange = create_range(size[0])
        self._h: SizeRange = create_range(size[1])

        if _update:
            self._update_rect_chain_up()

    def set_width(self, value: SizeType, _update=True) -> None:
        """
        Set the width of the element.
        """
        self._w: SizeRange = create_range(value)
        if _update:
            self._update_rect_chain_up()

    def set_height(self, value: SizeType, _update=True) -> None:
        """
        Set the height of the element.
        """
        self._h: SizeRange = create_range(value)
        if _update:
            self._update_rect_chain_up()

    def get_size(self) -> tuple[SizeRange, SizeRange]:
        """
        Get the size of the element. Returns ember.size.Size objects.
        If you want float sizes, use get_abs_size() instead.
        """
        return self._w, self._h

    def get_width(self) -> SizeRange:
        """
        Get the width of the element. Returns ember.size.Size object.
        If you want the width as a float, use get_ideal_width() instead.
        """
        return self._w

    def get_height(self) -> SizeRange:
        """
        Get the height of the element. Returns ember.size.Size object.
        If you want the height as a float, use get_ideal_height() instead.
        """
        return self._h

    def get_ideal_width(
        self, max_width: float = 0, _ignore_fill_width: bool = False
    ) -> float:
        """
        Get the width of the element as a float, given the maximum width to fill.
        """
        return self._w._ideal.get(self, max_width, _ignore_fill_width, mode="width")

    def get_ideal_height(
        self, max_height: float = 0, _ignore_fill_height: bool = False
    ) -> float:
        """
        Get the height of the element as a float, given the maximum height to fill.
        """
        return self._h._ideal.get(self, max_height, _ignore_fill_height, mode="height")

    def focus(self) -> None:
        """
        Focuses the element. Only works if the element is inside a ViewLayer.
        """
        if self.layer:
            if self.layer.element_focused is not self:
                self.layer.element_focused = self
                event = pygame.event.Event(ELEMENTFOCUSED, element=self)
                pygame.event.post(event)
        else:
            raise _c.Error(
                f"Cannot focus {self} because element is not inside of a ViewLayer."
            )

    def unfocus(self) -> None:
        """
        Unfocuses the element.
        """
        if self.layer:
            if self.layer.element_focused is self:
                self.layer.element_focused = None
                self._on_unfocus()
                event = pygame.event.Event(ELEMENTUNFOCUSED, element=self)
                pygame.event.post(event)
        else:
            raise _c.Error(
                f"Cannot unfocus {self} because element is not inside of a ViewLayer."
            )

    def get_parent_tree(self) -> list["Element"]:
        """
        Returns a list of ancestors, starting with the element's parent, then it's grandparent, and so on.
        """
        parents = [self.parent]
        while True:
            if not hasattr(parents[-1], "parent"):
                break
            next_parent = parents[-1].parent
            if not hasattr(next_parent, "parent"):
                break
            parents.append(next_parent)
        return parents

    def copy(self) -> "Element":
        new = copy.copy(self)
        new.rect = self.rect.copy()
        return new


ElementStrType = Union[str, Element, None]

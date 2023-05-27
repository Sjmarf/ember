import pygame
import copy
from typing import Union, TYPE_CHECKING, Optional, Sequence, TypeVar
from ember import log

from ember.event import TRANSITIONFINISHED, ELEMENTUNFOCUSED, ELEMENTFOCUSED

if TYPE_CHECKING:
    from ember.ui.view import View, ViewLayer
    from ember.transition.transition import Transition, TransitionController

from ember.size import Size, SizeType, SequenceSizeType
from ember.position import PositionType, Position

from ember import common as _c


class Element:
    """
    The base element class. All UI elements in the library inherit from this class.
    """

    def __init__(
            self,
            position: PositionType = None,
            size: SequenceSizeType = (20, 20),
            width: SizeType = 20,
            height: SizeType = 20,
            default_size: Sequence[SizeType] = (20, 20),
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

        self.rect: pygame.Rect
        """
        A :code:`pygame.Rect` object containing the position and size of the element. Read-only.
        """

        if _c.is_ce:
            self.rect = pygame.FRect(0, 0, 0, 0)
        else:
            self.rect = pygame.Rect(0, 0, 0, 0)

        self._draw_rect = pygame.Rect(0, 0, 0, 0)

        self.position: tuple[Position, Position] = (position, position) if isinstance(position, Position) else position
        """
        The position of the Element. Referenced if the element is inside of a :py:class:`ember.ui.Layout` container.
        """

        self._transition: Optional[TransitionController] = None
        self._can_focus: bool = can_focus

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

        self.set_size(width, height, _update_rect_chain_up=False)

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
                self._transition = None
                new_event = pygame.event.Event(TRANSITIONFINISHED, element=self)
                pygame.event.post(new_event)
        else:
            self._update()

    def _update(self) -> None:
        """
        Used intenally by the library.
        """
        pass

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

        if _c.is_ce:
            self.rect.update(
                *pos,
                self.get_abs_width(max_size[0], _ignore_fill_width=_ignore_fill_width),
                self.get_abs_height(
                    max_size[1], _ignore_fill_height=_ignore_fill_height
                ),
            )
        else:
            self.rect.update(
                round(pos[0]),
                round(pos[1]),
                round(
                    self.get_abs_width(
                        max_size[0], _ignore_fill_width=_ignore_fill_width
                    )
                ),
                round(
                    self.get_abs_height(
                        max_size[1], _ignore_fill_height=_ignore_fill_height
                    )
                ),
            )

        self._draw_rect.update(
            round(self.rect.x),
            round(self.rect.y),
            round(self.rect.w),
            round(self.rect.h),
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
                        log.size.info(self, "Element doesn't have FIT size - cutting chain...")
                else:
                    log.size.info(self, f"-> parent {self.parent}.")
                    with log.size.indent:
                        self.parent._update_rect_chain_up()
            else:
                log.size.info(self, "No parent - cutting chain...")
            if self.layer:
                if not self.layer._check_size:
                    log.size.info(self, "Starting chain down next tick...")
                    self.layer._check_size = True
            else:
                log.size.info(self, "No layer - check_size was not set.")

        return wrapper

    def _set_layer_chain(self, layer: "ViewLayer") -> None:
        """
        Sets the 'layer' attribute of the element, and all of its children, to the specified ViewLayer.
        """
        log.layer.info(self, f"Set layer to {layer}")
        self.layer = layer

    def _focus_chain(
            self, previous: "Element" = None, direction: str = "in"
    ) -> "Element":
        """
        Used internally by the library to manage keyboard/controller navigation.
        """
        # 'previous' is used for going back up the chain - it is set to None when going downwards
        if direction in {"in", "in_first"}:
            log.nav.info(self, "Returning self.")
            return self
        elif self.parent:
            # Go up a level and try again
            log.nav.info(self, f"-> Parent {self.parent}.")
            return self.parent._focus_chain(self, direction=direction)

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

    def set_size(
            self, *size: Union[Sequence[SizeType], SizeType], _update_rect_chain_up=True
    ) -> None:
        """
        Set the size of the element.
        """
        if isinstance(size[0], Sequence):
            size = size[0]

        self._width: Size = (
            Size(size[0]) if isinstance(size[0], (int, float)) else size[0]
        )
        self._height: Size = (
            Size(size[-1]) if isinstance(size[1], (int, float)) else size[1]
        )
        if _update_rect_chain_up:
            self._update_rect_chain_up()

    def set_width(self, value: SizeType, _update_rect_chain_up=True) -> None:
        """
        Set the width of the element.
        """
        self._width: Size = Size(value) if isinstance(value, (int, float)) else value
        if _update_rect_chain_up:
            self._update_rect_chain_up()

    def set_height(self, value: SizeType, _update_rect_chain_up=True) -> None:
        """
        Set the height of the element.
        """
        self._height: Size = Size(value) if isinstance(value, (int, float)) else value
        if _update_rect_chain_up:
            self._update_rect_chain_up()

    def get_size(self) -> tuple[Size, Size]:
        """
        Get the size of the element. Returns ember.size.Size objects.
        If you want float sizes, use get_abs_size() instead.
        """
        return self._width, self._height

    def get_width(self) -> Size:
        """
        Get the width of the element. Returns ember.size.Size object.
        If you want the width as a float, use get_abs_width() instead.
        """
        return self._width

    def get_height(self) -> Size:
        """
        Get the height of the element. Returns ember.size.Size object.
        If you want the height as a float, use get_abs_height() instead.
        """
        return self._height

    def get_abs_size(
            self, max_size: Sequence[Optional[float]] = (None, None)
    ) -> tuple[float, float]:
        """
        Get the size of the element as floats, given the maximum space to fill.
        """
        return self.get_abs_width(max_size[0]), self.get_abs_height(max_size[1])

    def get_abs_width(
            self, max_width: float = 0, _ignore_fill_width: bool = False
    ) -> float:
        """
        Get the width of the element as a float, given the maximum width to fill.
        """
        return self._width.get(self, max_width, _ignore_fill_width, mode="width")

    def get_abs_height(
            self, max_height: float = 0, _ignore_fill_height: bool = False
    ) -> float:
        """
        Get the height of the element as a float, given the maximum height to fill.
        """
        return self._height.get(self, max_height, _ignore_fill_height, mode="height")

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
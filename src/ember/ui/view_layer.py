import pygame
from .. import event as ember_event
from .. import common as _c
from ..common import DEFAULT, DefaultType
from .. import log
from typing import Optional, TYPE_CHECKING, Any, Sequence, Union, TypeVar

if TYPE_CHECKING:
    from .view import View

from ..base.element import Element
from ember.base.single_element_container import SingleElementContainer

from ..base.scroll import Scroll

from ..size import SizeType, OptionalSequenceSizeType, FILL
from ember.position import (
    PositionType,
    CENTER,
    SequencePositionType,
    OptionalSequencePositionType,
)

T = TypeVar("T", bound="Element", covariant=True)


class ViewLayer(SingleElementContainer[T]):
    def __init__(
        self,
        element: Optional["Element"],
        view: Optional["View"] = None,
        focused: Optional["Element"] = None,
        listen_for_exit: Union[DefaultType, bool] = DEFAULT,
        clamp: bool = True,
        exit_on_click_off: bool = False,
        rect: Union[pygame.rect.RectType, Sequence, None] = None,
        pos: Optional[SequencePositionType] = CENTER,
        x: Optional[PositionType] = None,
        y: Optional[PositionType] = None,
        size: OptionalSequenceSizeType = None,
        w: Optional[SizeType] = None,
        h: Optional[SizeType] = None,
        content_pos: OptionalSequencePositionType = None,
        content_x: Optional[PositionType] = None,
        content_y: Optional[PositionType] = None,
        content_size: OptionalSequenceSizeType = None,
        content_w: Optional[SizeType] = None,
        content_h: Optional[SizeType] = None,
    ):
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        self.view: "View" = view
        """
        The View containing the ViewLayer.
        """

        self.clamp: bool = clamp
        """
        Whether the layer should be kept inside of the view.
        """

        self.exit_on_click_off: bool = exit_on_click_off
        """
        Exit the ViewLayer when the user clicks outside of its rect.
        """

        self.element_focused: Optional["Element"] = focused
        """
        The element that is currently focused.
        """

        super().__init__(
            element=element,
            rect=rect,
            pos=pos,
            x=x,
            y=y,
            size=size,
            w=w,
            h=h,
            content_pos=content_pos,
            content_x=content_x,
            content_y=content_y,
            content_size=content_size,
            content_w=content_w,
            content_h=content_h,
            layer=self,
        )

        self.listen_for_exit: bool = listen_for_exit
        """
        If True, the ViewLayer triggers its exit transition when the Escape key 
        (or the equivalent controller button) is pressed. 
        You can trigger the exit transition yourself by calling ViewLayer.exit() if you prefer.
        """

        self.can_focus_update_queue: list[Element] = []
        self.min_size_update_queue: list[tuple[Element, bool]] = []
        self.rect_update_queue: list[Element] = []

        self._exit_cause: Optional[Element] = None
        self._exit_kwargs: dict[Any:Any] = {}

        self._joy_axis_motion: Sequence[int] = [0, 0]
        """
        The rect of the bottommost layer.
        """

    def __repr__(self) -> str:
        return f"<ViewLayer>"

    def _process_queues(self, surface: pygame.Surface) -> None:
        while self.min_size_update_queue:
            element, must_update_parent = self.min_size_update_queue.pop(0)
            log.size.line_break()
            with log.size.indent(f"Starting min size update from element {element}."):
                element.update_min_size(must_update_parent=must_update_parent)

        i = 0
        while self.rect_update_queue:
            self.rect_update_queue.sort(key=lambda a: len(a.ancestry))
            element = self.rect_update_queue.pop(0)
            log.size.line_break()

            if i > 0:
                log.size.info(
                    f"Starting rect update again (iteration {i + 1}) from element {element}.",
                )
            else:
                log.size.info(f"Starting rect update from element {element}.")

            with log.size.indent():
                element._update_rect(
                    surface,
                    element.rect.x,
                    element.rect.y,
                    element.rect.w,
                    element.rect.h,
                )

            log.size.info("Rect update finished.")
            i += 1
            if i > 300:
                raise _c.Error(
                    "The maximimum number of update_rect calls from a ViewLayer on a single tick (300) was exceeded."
                )

    def _event(self, event: pygame.event.Event) -> bool:
        if self._element is not None and self._element._event(event):
            return True

        if event.type == pygame.MOUSEBUTTONDOWN and self.view._layers[0] is not self:
            if event.button == 1 and self.exit_on_click_off:
                self._exit_menu()

        return False

    def _focus_element(self, new_element: Optional["Element"]) -> None:
        if self.element_focused is not new_element:
            if self.element_focused is not None:
                self.element_focused.unfocus()

            if new_element is None:
                event = pygame.event.Event(
                    ember_event.ELEMENTUNFOCUSED, element=self.element_focused
                )
                pygame.event.post(event)
                self.element_focused = None
            else:
                new_element.focus()

    def _focus_chain(
        self, direction: _c.FocusDirection, previous: Optional["Element"] = None
    ) -> "Element":
        log.nav.info(self, "Reached ViewLayer. Focus wasn't changed.")
        if direction == _c.FocusDirection.OUT:
            self._exit_pressed()
        return self.element_focused

    def _exit_pressed(self) -> bool:
        if self.element_focused is not None:
            self._focus_element(None)
            return True
        elif self.listen_for_exit:
            self._exit_menu()
            return True
        return False

    def _exit_menu(self) -> None:
        """
        Finish transitioning.
        """
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        new_event = pygame.event.Event(
            ember_event.VIEWEXITFINISHED,
            view=self.view,
            layer=self,
            index=self.view._layers.index(self),
            cause=self._exit_cause,
            **self._exit_kwargs,
        )
        pygame.event.post(new_event)
        if self.view._layers[0] is not self:
            self.view._layers.remove(self)

    def start_manual_update(self) -> None:
        """
        Starts the update chain on the next tick. You shouldn't need to call this manually, it exists incase the
        library misses something.
        """
        self.rect_update_queue.append(self)

    def update_can_focus(self) -> None:
        pass

    def shift_focus(
        self, direction: _c.FocusDirection, element: Optional["Element"] = None
    ) -> None:
        """
        Shift the focus in a direction.
        """
        if self.element_focused is None:
            with log.nav.indent(
                f"Starting focus chain for {self._element} with direction "
                f"{_c.FocusDirection.SELECT}.",
                self,
            ):
                new_element = self._element._focus_chain(_c.FocusDirection.SELECT)
        else:
            if element is None:
                element = self.element_focused
            with log.nav.indent(
                f"Starting focus chain for {element} with direction {direction}.", self
            ):
                new_element = element._focus_chain(direction)

        self._focus_element(new_element)

        log.nav.info(f"Focus chain ended. Focused {self.element_focused}.")

        # Determine if the element being selected is inside a Scroll
        if self.element_focused is not None:
            for element in self.element_focused.ancestry:
                if isinstance(element, Scroll):
                    pass
                    # If the element isn't fully visible in the frame, scroll to that element
                    # element.scroll_to_element(self.element_focused)

    def update_rect_next_tick(self) -> None:
        if self not in self.layer.rect_update_queue:
            self.layer.rect_update_queue.append(self)

    @property
    def index(self) -> int:
        return self.view._layers.index(self)

ViewLayer.w_.default_value = FILL
ViewLayer.h_.default_value = FILL

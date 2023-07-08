import pygame
from .. import event as ember_event
from .. import common as _c
from ..common import INHERIT, InheritType
from .. import log
from typing import Optional, TYPE_CHECKING, Any, Sequence, Union, Callable

if TYPE_CHECKING:
    from ..transition.transition import Transition
    from .view import View
    from ..style.view_style import ViewStyle

from .base.element import Element
from .base.single_element_container import SingleElementContainer

from .base.scroll import Scroll
from ember.state.state import State, load_background, StateType

from ..size import FIT, FILL, SizeType, OptionalSequenceSizeType
from ..position import (
    PositionType,
    CENTER,
    SequencePositionType,
    OptionalSequencePositionType,
)

from ..state.state_controller import StateController


class ViewLayer(SingleElementContainer):
    def __init__(
        self,
        element: "Element",
        view: Optional["View"] = None,
        focused: Optional["Element"] = None,
        material: StateType = None,
        listen_for_exit: Union[InheritType, bool] = INHERIT,
        transition: Union[InheritType, "Transition", None] = INHERIT,
        transition_in: Union[InheritType, "Transition", None] = INHERIT,
        transition_out: Union[InheritType, "Transition", None] = INHERIT,
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
        style: Optional["ViewStyle"] = None,
    ):
        self.layer = self

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

        self._element: Element = element

        super().__init__(
            material,
            rect,
            pos,
            x,
            y,
            size,
            w,
            h,
            content_pos,
            content_x,
            content_y,
            content_size,
            content_w,
            content_h,
            style,
        )

        self.listen_for_exit: bool = (
            self._style.listen_for_exit
            if listen_for_exit is INHERIT
            else listen_for_exit
        )
        """
        If True, the ViewLayer triggers its exit transition when the Escape key 
        (or the equivalent controller button) is pressed. 
        You can trigger the exit transition yourself by calling ViewLayer.exit() if you prefer.
        """

        self.material: Optional[State] = load_background(self, material)
        """
        The State to use for the background of the ViewLayer. Overrides the default state from the ViewStyle.
        """

        self.transition_in: Optional["Transition"]
        """
        The :py:class`Transition<ember.transition.Transition>` to use when the ViewLayer is transitioning in.
        """
        if transition_in is not INHERIT:
            self.transition_in = transition_in
        elif transition is not INHERIT:
            self.transition_in = transition
        elif self._style:
            self.transition_in = self._style.transition_in
        else:
            self.transition_in = None

        self.transition_out: Optional["Transition"]
        """
        The :py:class`Transition<ember.transition.Transition>` to use when the ViewLayer is transitioning out.
        """
        if transition_out is not INHERIT:
            self.transition_out = transition_out
        elif transition is not INHERIT:
            self.transition_out = transition
        elif self._style:
            self.transition_out = self._style.transition_out
        else:
            self.transition_out = None

        log.size.line_break()
        log.size.info(self, "ViewLayer created, starting chain down next tick...")
        self._chain_down_from = self._element
        """
        When True, _update_rect_chain_down will be started on the next tick
        """

        log.layer.line_break()
        log.layer.info(self, "ViewLayer created - starting chain...")
        with log.layer.indent:
            element._set_layer_chain(self)
        element._set_parent(self)

        self._prev_rect: tuple[float, float, float, float] = (0, 0, 0, 0)
        self._waiting_for_transition_finish = False

        self._exit_cause: Optional[Element] = None
        self._exit_kwargs: dict[Any:Any] = {}

        self._joy_axis_motion: Sequence[int] = [0, 0]
        """
        The rect of the bottommost layer.
        """

        self.state_controller: StateController = StateController(self)
        """
        The :py:class:`ember.state.StateController` object responsible for managing the ViewLayer's states.
        """

        if self.transition_in:
            self._block_rendering = True
        else:
            self._block_rendering = False

        if self._style.auto_transition_in:
            self.start_transition_in()

    def __repr__(self) -> str:
        return f"<ViewLayer({self._element})>"

    def _render_elements(
        self,
        surface: pygame.Surface,
        offset: tuple[int, int],
        alpha: int = 255,
    ) -> None:
        if self._element and not self._block_rendering:
            self._element._render_a(surface, (0, 0), alpha)

    def _update(self) -> None:
        self._element._update_a()

    def _update_rect_chain_down(
        self, surface: pygame.Surface, x: float, y: float, w: float, h: float
    ) -> None:
        self.rect.update(x, y, w, h)
        self._int_rect.update(
            round(x),
            round(y),
            round(w),
            round(h),
        )

        i = 0
        while self._chain_down_from is not None:
            log.size.line_break()

            if i > 0:
                log.size.info(
                    self,
                    f"Starting chain down again (iteration {i + 1}).",
                )
            else:
                log.size.info(self, f"Starting chain down.")

            self._chain_down_from = None

            with log.size.indent:
                super()._update_rect_chain_down(surface, x, y, w, h)

            log.size.info(self, "Chain finished.")
            i += 1
            if i > 30:
                raise _c.Error("Maximimum chain-down count exceeded.")

    def _event(self, event: pygame.event.Event) -> bool:
        if self._element._event(event):
            return True

        if event.type == pygame.MOUSEBUTTONDOWN and self.view._layers[0] is not self:
            if event.button == 1 and self.exit_on_click_off:
                if not pygame.Rect(self._prev_rect).collidepoint(_c.mouse_pos):
                    self.start_transition_out()

        elif event.type == ember_event.TRANSITIONFINISHED:
            if event.controller.old is self:
                self._exit_menu()

        return False

    def _focus_element(self, new_element: Optional["Element"]) -> None:
        if self.element_focused is not new_element:
            if self.element_focused is not None:
                self.element_focused._on_unfocus()

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
            if self.transition_out:
                self.start_transition_out()
            else:
                self._exit_menu()
            return True
        return False

    def _exit_menu(self) -> None:
        """
        Finish transitioning.
        """
        self._block_rendering = True
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
        self._chain_down_from = self._element

    def start_transition_in(self, transition: Optional["Transition"] = None) -> None:
        """
        Start transitioning the ViewLayer in.
        """
        if transition is None:
            transition = self.transition_in
        if transition is not None:
            self._transition = transition._new_element_controller()
            self._transition.new = self
            self._block_rendering = False

    def start_transition_out(
        self, transition: Optional["Transition"] = None, cause: Any = None, **kwargs
    ) -> None:
        """
        Start transitioning the ViewLayer out. When the transition is finished, an ember.MENUEXIT event will be posted.
        This event will have the 'cause' attribute, the value of which can be specified in the 'cause'
        parameter of this method. You can also specify any other keyword argument(s) - they'll be added to the
        event too.
        """
        if transition or self.transition_out:
            transition = transition if transition else self.transition_out
            self._transition = transition._new_element_controller()
            self._transition.old = self
            self._exit_cause = cause
            self._exit_kwargs = kwargs

        else:
            self._exit_menu()

        new_event = pygame.event.Event(
            ember_event.VIEWEXITSTARTED,
            cause=cause,
            index=self.view._layers.index(self),
            layer=self,
            **kwargs,
        )
        pygame.event.post(new_event)

    def shift_focus(
        self, direction: _c.FocusDirection, element: Optional["Element"] = None
    ) -> None:
        """
        Shift the focus in a direction.
        """
        if self.element_focused is None:
            log.nav.info(
                self,
                f"Starting focus chain for {self._element} with direction"
                f" {_c.FocusDirection.SELECT}.",
            )
            with log.nav.indent:
                new_element = self._element._focus_chain(_c.FocusDirection.SELECT)
        else:
            if element is None:
                element = self.element_focused
            log.nav.info(
                self,
                f"Starting focus chain for {element} with direction {direction}.",
            )
            with log.nav.indent:
                new_element = element._focus_chain(direction)

        self._focus_element(new_element)

        log.nav.info(self, f"Focus chain ended. Focused {self.element_focused}.")

        # Determine if the element being selected is inside a Scroll
        if self.element_focused is not None:
            for element in self.element_focused.get_parent_tree():
                if isinstance(element, Scroll):
                    # If the element isn't fully visible in the frame, scroll to that element
                    element.scroll_to_element(self.element_focused)

    @property
    def index(self) -> int:
        return self.view._layers.index(self)

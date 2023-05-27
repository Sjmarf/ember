import pygame
from .. import event as ember_event
from .. import common as _c
from .. import log
from typing import Optional, TYPE_CHECKING, Any, Sequence

if TYPE_CHECKING:
    from ..transition.transition import Transition
    from .base.element import Element
    from .view import View

from .base.scroll import Scroll
from ..style.view_style import ViewStyle
from ..style.load_style import load as load_style
from ..style.get_style import _get_style
from ember.state.state import State, load_background, StateType

from ..state.state_controller import StateController

class ViewLayer:
    def __init__(
        self,
        element: "Element",
        view: Optional["View"] = None,
        rect: Optional[pygame.rect.RectType] = None,
        focused: Optional["Element"] = None,
        background: StateType = None,
        listen_for_exit: bool = True,
        transition: Optional["Transition"] = None,
        transition_in: Optional["Transition"] = None,
        transition_out: Optional["Transition"] = None,
        clamp: bool = True,
        close_when_click_off: bool = True,
        style: Optional["ViewStyle"] = None
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

        self.close_when_click_off: bool = close_when_click_off
        """
        Exit the ViewLayer when the user clicks outside of its rect.
        """

        self.element_focused: Optional["Element"] = focused
        """
        The element that is currently focused.
        """

        self.listen_for_exit: bool = listen_for_exit
        """
        Whether pressing escape should exit the menu.
        """

        self.set_style(style)

        self.background: Optional[State] = load_background(self, background)
        """
        The State to use for the background of the ViewLayer. Overrides the default state from the ViewStyle.
        """

        self.transition_in: Optional["Transition"]
        """
        The :py:class`Transition<ember.transition.Transition>` to use when the ViewLayer is transitioning in.
        """
        if transition_in:
            self.transition_in = transition_in
        elif transition:
            self.transition_in = transition
        elif self._style and self._style.transition_in:
            self.transition_in = self._style.transition_in
        else:
            self.transition_in = None

        self.transition_out: Optional["Transition"]
        """
        The :py:class`Transition<ember.transition.Transition>` to use when the ViewLayer is transitioning out.
        """
        if transition_out:
            self.transition_out = transition_out
        elif transition:
            self.transition_out = transition
        elif self._style and self._style.transition_out:
            self.transition_out = self._style.transition_out
        else:
            self.transition_out = None

        self._element: Element = element
        element._set_parent(self)
        log.layer.line_break()
        log.layer.info(self, "ViewLayer created - starting chain...")
        with log.layer.indent:
            element._set_layer_chain(self)

        if self.transition_in:
            element._transition = self.transition_in._new_element_controller()
            element._transition.new_element = element

        log.size.info(self, "ViewLayer created, starting chain down next tick...")
        self._check_size = True
        """
        When True, _update_rect_chain_down will be started on the next tick
        """

        self._prev_rect: tuple[float, float, float, float] = (0, 0, 0, 0)
        self._waiting_for_transition_finish = False
        self._block_rendering = False
        self._exit_cause: Optional[Element] = None

        self._joy_axis_motion: Sequence[int] = [0, 0]
        """
        The rect of the bottommost layer.
        """

        self.rect: pygame.Rect = pygame.Rect(rect) if rect is not None else None
        """
        The rect within which to draw the view.
        """

        self.state_controller: StateController = StateController(self)
        """
        The :py:class:`ember.state.StateController` object responsible for managing the ViewLayer's states.
        """

        self._rect: pygame.Rect = pygame.Rect(0,0,0,0)

    def __repr__(self) -> str:
        return f"<ViewLayer({self._element})>"

    def _update_positions(
        self, surface: pygame.Surface, rect: Optional[pygame.rect.RectType] = None
    ) -> None:

        if isinstance(rect, (Sequence, pygame.Rect)):
            pos = (
                rect[0] + rect[2] // 2 - self._element.get_abs_width(rect[2]) // 2,
                rect[1] + rect[3] // 2 - self._element.get_abs_height(rect[3]) // 2,
                *rect[2:],
            )
            self._rect.update(rect)

        elif self.rect:
            if self.clamp:
                if rect is not None:
                    pos = tuple(self.rect.clamp(rect))
                else:
                    pos = tuple(self.rect.clamp((0,0,*surface.get_size())))
            else:
                pos = tuple(self.rect)
            self._rect.update(self.rect)

        else:
            pos = (
                surface.get_width() // 2
                - self._element.get_abs_width(surface.get_width()) // 2,
                surface.get_height() // 2
                - self._element.get_abs_height(surface.get_height()) // 2,
                *surface.get_size(),
            )
            self._rect.update(0,0,*surface.get_size())

        if self._prev_rect != pos:
            self._prev_rect = pos
            if not self._check_size:
                log.size.info(self, "ViewLayer rect changed size, starting chain down next tick...")
                self._check_size = True

        i = 0
        while self._check_size:
            log.size.line_break()
            if i > 0:
                log.size.info(self, f"Starting chain down again (iteration {i + 1}).")
            else:
                log.size.info(self, f"Starting chain down.")

            self._check_size = False

            with log.size.indent:
                self._element._update_rect_chain_down(surface, pos[:2], pos[2:])

            log.size.info(self, "Chain finished.")
            i += 1
            if i > 30:
                raise _c.Error("Maximimum chain-down count exceeded.")

    def _render(self, surface: pygame.Surface, alpha: int) -> None:
        self.state_controller.render(
            self._style.state_func(self),
            surface,
            (
                self._rect.x,
                self._rect.y,
            ),
            self._rect.size,
            alpha,
        )
        if not self._block_rendering:
            self._element._render_a(surface, (0, 0), alpha)

    def _event(self, event: pygame.event.Event, layer: int) -> bool:
        if self._element._event(event):
            return True

        if event.type == pygame.MOUSEBUTTONDOWN and layer > 0:
            if event.button == 1 and self.close_when_click_off:
                if not pygame.Rect(self._prev_rect).collidepoint(_c.mouse_pos):
                    self.start_transition_out()
                    self._waiting_for_transition_finish = True

        elif event.type == ember_event.TRANSITIONFINISHED:
            if event.element is self._element:
                if self._waiting_for_transition_finish:
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

    def _update_rect_chain_up(self) -> None:
        pass

    def _focus_chain(
        self, previous: "Element" = None, direction: str = ""
    ) -> "Element":
        log.nav.info(self, "Reached ViewLayer. Focus wasn't changed.")
        if direction == "out":
            self._exit_pressed()
        return self.element_focused

    def _exit_pressed(self) -> bool:
        if self.element_focused is not None:
            self._focus_element(None)
            return True
        elif self.listen_for_exit:
            if self.transition_out:
                self.start_transition_out()
                self._waiting_for_transition_finish = True
            else:
                self._exit_menu()
            return True
        return False

    def _exit_menu(self) -> None:
        """
        Start fading out the ViewLayer.
        """
        self._block_rendering = True
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        new_event = pygame.event.Event(
            ember_event.MENUEXITFINISHED, view=self.view, layer=self, cause=self._exit_cause
        )
        pygame.event.post(new_event)

    def set_element(self, element: "Element") -> None:
        """
        Replace the ViewLayer's element with the specified element.
        """
        self._element = element
        element._set_parent(self)
        log.layer.line_break()
        log.layer.info(self, "Element added to ViewLayer - starting chain...")
        with log.layer.indent:
            element._set_layer_chain(self)

    def start_transition_out(
        self, transition: Optional["Transition"] = None, cause: Any = None
    ) -> None:
        """
        Start transitioning the view out. When the transition is finished, an ember.MENUEXIT event will be posted.
        This event will have the 'cause' attribute, the value of which can be specified in the 'cause'
        parameter of this method.
        """
        if (
            transition
            or self.transition_out
            and not self._waiting_for_transition_finish
        ):
            self._waiting_for_transition_finish = True
            transition = transition if transition else self.transition_out
            self._element._transition = transition._new_element_controller()
            self._element._transition.old_element = self._element
            self._exit_cause = cause

            new_event = pygame.event.Event(ember_event.MENUEXITSTARTED, cause=cause)
            pygame.event.post(new_event)

    def shift_focus(self, direction: str) -> None:
        """
        Shift the focus in a direction. Directions can be 'left', 'right', 'up', 'down', 'foward'
        (equivalent to pressing tab), 'backward' (equivalent to pressing shift + tab), 'in'
        (equivalent to pressing enter), or 'out' (equivalent to pressing escape).
        """
        if self.element_focused is None:
            log.nav.info(
                self,
                f"Starting focus chain for {self._element} with direction"
                f" 'select'.",
            )
            with log.nav.indent:
                new_element = self._element._focus_chain(None)
        else:
            log.nav.info(
                self,
                f"Starting focus chain for {self.element_focused} with direction '{direction}'.",
            )
            with log.nav.indent:
                new_element = self.element_focused._focus_chain(
                    None, direction=direction
                )

        self._focus_element(new_element)

        log.nav.info(self, f"Focus chain ended. Focused {self.element_focused}.")

        # Determine if the element being selected is inside a VScroll
        if self.element_focused is not None:
            for element in self.element_focused.get_parent_tree():
                if isinstance(element, Scroll):
                    # If the element isn't fully visible in the frame, scroll to that element
                    element.scroll_to_element(self.element_focused)

    def _set_style(self, style: Optional["ViewStyle"]) -> None:
        self.set_style(style)

    def set_style(self, style: Optional["ViewStyle"]) -> None:
        """
        Sets the ViewStyle of the ViewLayer.
        """
        self._style: ViewStyle = _get_style(style, "view")

    style: "ViewStyle" = property(
        fget=lambda self: self._style,
        fset=_set_style,
        doc="The ViewStyle of the ViewLayer. Synonymous with the set_style() method.",
    )

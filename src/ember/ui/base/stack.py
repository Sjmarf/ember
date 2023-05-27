import pygame
from typing import Optional, Sequence, Union

from ember.common import InheritType, INHERIT
from ember import log
from ember.ui.base.element import Element
from ember.size import SizeType
from ember.position import PositionType

from ember.state.state_controller import StateController
from ember.state.state import State, load_background

from ember.style.container_style import ContainerStyle
from ember.material.material import Material

from ember.ui.base.multi_element_container import MultiElementContainer


class Stack(MultiElementContainer):
    """
    A Stack is a collection of Elements. There are two subclasses of Stack - :py:class:`ember.ui.VStack`
    and :py:class:`ember.ui.HStack`. This base class should not be instantiated directly.
    """
    def __init__(
        self,
        style: ContainerStyle,
        background: Union[State, Material, None],
        spacing: Union[InheritType, int],
        min_spacing: Union[InheritType, int],
        focus_self: Union[InheritType, bool],
        position: PositionType,
        size: Sequence[SizeType],
        width: SizeType,
        height: SizeType,
        default_size: Sequence[SizeType] = (20, 20),
    ):
        """
        The base class for VStack and HStack.
        """

        self._fit_width: int = 0
        self._fit_height: int = 0

        self.set_style(style)

        self.background: Optional[State] = load_background(self, background)
        """
        The State to use for the background of the Stack. Overrides the states from the ContainerStyle.
        """

        self.spacing: Optional[int] = (
            self._style.spacing if spacing is INHERIT else spacing
        )
        """
        The spacing between the elements. If spacing is set to None, the elements will 
        be spaced evenly the fill the whole Stack. If no spacing is specified, the 
        spacing from the ContainerStyle is used.
        """

        self.min_spacing: int
        """
        The minimum spacing between the elements. Only effective if the 'spacing' attribute is None.
        """

        if self.spacing:
            self.min_spacing = self.spacing
        else:
            self.min_spacing = (
                self._style.min_spacing if min_spacing is INHERIT else min_spacing
            )

        self.focus_self: bool = (
            self._style.focus_self if focus_self is INHERIT else focus_self
        )
        """
        Modifies how the Stack behaves with keyboard / controller navigation. If set to True, the Stack itself 
        is focusable. If you press enter when the Stack is focused, the first child of the Stack is focused.
        """

        self._first_visible_element: Optional[Element] = None

        self.state_controller: StateController = StateController(self)
        """
        The :py:class:`ember.state.StateController` object is responsible for managing the Stack's 
        background states.
        """

        super().__init__(position, size, width, height, default_size=default_size)

    def _render_elements(
        self,
        surface: pygame.Surface,
        offset: tuple[int, int],
        alpha: int = 255,
    ) -> None:
        for n, i in enumerate(self._elements[self._first_visible_element :]):
            if not i.is_visible:
                break
            i._render_a(surface, offset, alpha=alpha)

    def _update(self) -> None:
        for i in self._elements[self._first_visible_element :]:
            i._update_a()
            if not i.is_visible:
                break

    def _event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self.layer.element_focused is self:
                    log.nav.info(self, "Enter key pressed, starting focus chain.")
                    with log.nav.indent:
                        self.layer._focus_element(
                            self._enter_in_first_element(
                                "in_first", ignore_self_focus=True
                            )
                        )
                    log.nav.info(
                        self,
                        f"Focus chain ended. Focused {self.layer.element_focused}.",
                    )
                    return True

        for i in self._elements[self._first_visible_element :]:
            if i._event(event):
                return True
            if not i.is_visible:
                break
        return False

    def _enter_in_first_element(
        self, key: str, ignore_self_focus: bool = False
    ) -> Optional[Element]:
        pass

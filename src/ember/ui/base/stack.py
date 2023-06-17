import pygame

from typing import Optional, Sequence, Union, Literal, TYPE_CHECKING

from ember.common import InheritType, INHERIT, FocusType
from ember import log
from ember.ui.base.element import Element
from ember.size import SizeType, SequenceSizeType
from ember.position import PositionType, SequencePositionType

from ember.state.state_controller import StateController
from ember.state.background_state import BackgroundState

from ember.material.material import Material

from ember.ui.base.multi_element_container import MultiElementContainer

if TYPE_CHECKING:
    from ember.style.container_style import ContainerStyle


class Stack(MultiElementContainer):
    """
    A Stack is a collection of Elements. There are two subclasses of Stack - :py:class:`ember.ui.VStack`
    and :py:class:`ember.ui.HStack`. This base class should not be instantiated directly.
    """

    def __init__(
        self,
        style: "ContainerStyle",
        material: Union[BackgroundState, Material, None],
        spacing: Union[InheritType, int],
        min_spacing: Union[InheritType, int],
        focus_on_entry: Union[InheritType, FocusType],
        rect: Union[pygame.rect.RectType, Sequence, None],
        pos: Optional[SequencePositionType],
        x: Optional[PositionType],
        y: Optional[PositionType],
        size: Optional[SequenceSizeType],
        width: Optional[SizeType],
        height: Optional[SizeType],
    ):
        """
        The base class for VStack and HStack.
        """

        self._min_w: int = 0
        self._min_h: int = 0

        self.set_style(style)

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

        self._first_visible_element: Optional[Element] = None

        self.state_controller: StateController = StateController(self)
        """
        The :py:class:`ember.state.StateController` object is responsible for managing the Stack's 
        background states.
        """
        super().__init__(material, rect, pos, x, y, size, width, height, focus_on_entry)

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

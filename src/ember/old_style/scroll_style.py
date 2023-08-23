from typing import Optional, Sequence, Callable

from .style import Style

from ember.utility.load_material import MaterialType
from ember.style.state import State
from ember.style.state import BackgroundState
from ember.style.state import ScrollbarState


from ..size import SizeType, SequenceSizeType, OptionalSequenceSizeType
from ember.position.position import SequencePositionType, Position, CENTER
from ..ui.base.scroll import Scroll


class ScrollStyle(Style):
    _ELEMENT = Scroll

    @staticmethod
    def default_state_func(scroll: "Scroll") -> BackgroundState:
        if scroll._state:
            return scroll._state
        return scroll._style.default_state

    @staticmethod
    def default_scrollbar_state_func(scroll: "Scroll") -> ScrollbarState:
        if scroll.scrollbar_grabbed:
            return scroll._style.click_scrollbar_state
        elif scroll.scrollbar_hovered:
            return scroll._style.hover_scrollbar_state
        else:
            return scroll._style.default_scrollbar_state

    def __init__(
        self,
        size: SequenceSizeType = (300, 300),
        width: SizeType = None,
        height: SizeType = None,
        content_pos: SequencePositionType = CENTER,
        content_size: OptionalSequenceSizeType = None,
        default_state: Optional[BackgroundState] = None,
        default_scrollbar_state: Optional[ScrollbarState] = None,
        hover_scrollbar_state: Optional[ScrollbarState] = None,
        click_scrollbar_state: Optional[ScrollbarState] = None,
        default_material: Optional[MaterialType] = None,
        default_handle_material: Optional[MaterialType] = None,
        hover_handle_material: Optional[MaterialType] = None,
        click_handle_material: Optional[MaterialType] = None,
        scrollbar_size: int = 3,
        padding: int = 10,
        scroll_speed: int = 5,
        over_scroll: tuple[int, int] = (0, 0),
        material_transition: Optional["Transition"] = None,
        base_material_transition: Optional["Transition"] = None,
        handle_material_transition: Optional["Transition"] = None,
        state_func: Callable[["Scroll"], "BackgroundState"] = default_state_func,
        scrollbar_state_func: Callable[
            ["Scroll"], "State"
        ] = default_scrollbar_state_func,
    ):
        self.size: tuple[SizeType, SizeType] = self.load_size(size, width, height)
        """
        The size of the Element if no size is specified in the Element constructor.
        """

        if not isinstance(content_pos, Sequence):
            content_pos = (content_pos, content_pos)

        self.content_pos: Sequence[Position] = content_pos
        """
        The alignment of elements within the container.
        """

        if not isinstance(content_size, Sequence):
            content_size = (content_size, content_size)

        self.content_size: Sequence[Optional[Size]] = content_size
        """
        The size of elements within the container.
        """

        self.default_state: BackgroundState = BackgroundState._load(
            default_state, default_material
        )
        """
        The default background State.
        """

        self.default_scrollbar_state: ScrollbarState = ScrollbarState._load(
            default_scrollbar_state, None, default_handle_material
        )
        """
        The default State of the scrollbar.
        """

        self.hover_scrollbar_state: ScrollbarState = ScrollbarState._load(
            hover_scrollbar_state, None, hover_handle_material
        )
        """
        Shows when the scrollbar is hovered hover. Uses the default scrollbar state if no state is specified.
        """

        self.click_scrollbar_state: ScrollbarState = ScrollbarState._load(
            click_scrollbar_state, None, click_handle_material
        )
        """
        Shows when the scrollbar is grabbed. Uses the scrollbar hover state if no state is specified.
        """

        self.scrollbar_size: int = scrollbar_size
        self.padding: int = padding

        self.scroll_speed: int = scroll_speed
        """
        The speed at which using the scrollwheel moves the scrollbar.
        """

        self.over_scroll: tuple[int, int] = over_scroll
        """
        The distance in pixels that the user can scroll past the child element. tuple[top, bottom].
        """

        self.material_transition: Optional["Transition"] = material_transition
        """
        The Transition to use when changing background States.
        """

        self.base_material_transition: Optional["Transition"] = base_material_transition
        """
        The Transition to use when changing scrollbar base States.
        """

        self.handle_material_transition: Optional[
            Transition
        ] = handle_material_transition
        """
        The Transition to use when changing scrollbar handle States.
        """

        self.state_func: Callable[["Scroll"], "BackgroundState"] = state_func
        """
        The function that determines which background state is active. Can be replaced for more control over the Scroll's states.
        """

        self.scrollbar_state_func: Callable[
            ["Scroll"], "BackgroundState"
        ] = scrollbar_state_func
        """
        The function that determines which scrollbar state is active. Can be replaced for more control over the scrollbar's states.
        """

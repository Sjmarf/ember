from typing import Optional, Sequence, TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from ember.ui.base.scroll import Scroll

from .. import common as _c
from .style import Style

from .load_material import MaterialType
from ..state.state import State, load_state

from ..transition.transition import Transition
from . import defaults


def default_state_func(scroll: "Scroll") -> State:
    if scroll.background:
        return scroll.background
    elif scroll.layer.element_focused is scroll:
        return scroll._style.focus_state
    elif (
        scroll.layer.element_focused is not None
        and scroll in scroll.layer.element_focused.get_parent_tree()
    ):
        return scroll._style.focus_child_state
    else:
        return scroll._style.default_state


def default_base_state_func(scroll: "Scroll") -> State:
    return scroll._style.default_base_state


def default_handle_state_func(scroll: "Scroll") -> State:
    if scroll.scrollbar_grabbed:
        return scroll._style.click_handle_state
    elif scroll.scrollbar_hovered:
        return scroll._style.hover_handle_state
    else:
        return scroll._style.default_handle_state


class ScrollStyle(Style):
    def __init__(
        self,
        default_state: Optional[State] = None,
        focus_state: Optional[State] = None,
        focus_child_state: Optional[State] = None,
        default_base_state: Optional[State] = None,
        default_handle_state: Optional[State] = None,
        hover_handle_state: Optional[State] = None,
        click_handle_state: Optional[State] = None,
        default_material: MaterialType = None,
        focus_material: MaterialType = None,
        focus_child_material: MaterialType = None,
        default_base_material: MaterialType = None,
        default_handle_material: MaterialType = None,
        hover_handle_material: MaterialType = None,
        click_handle_material: MaterialType = None,
        scrollbar_size: int = 3,
        padding: int = 10,
        scroll_speed: int = 5,
        over_scroll: tuple[int, int] = (0, 0),
        focus_self: bool = False,
        align_element_v: Sequence[str] = ("center", "center"),
        align_element_h: Sequence[str] = ("center", "center"),
        material_transition: Optional[Transition] = None,
        base_material_transition: Optional[Transition] = None,
        handle_material_transition: Optional[Transition] = None,
        state_func: Optional[Callable[["Scroll"], "State"]] = None,
        base_state_func: Optional[Callable[["Scroll"], "State"]] = None,
        handle_state_func: Optional[Callable[["Scroll"], "State"]] = None,
    ):
        self.default_state: State = load_state(default_state, default_material, None)
        """
        The default background State.
        """

        self.focus_state: State = load_state(
            focus_state, focus_material, self.default_state
        )
        """
        Shown when the Scroll is focused. Uses the default state if no state is specified.
        """
        self.focus_child_state: State = load_state(
            focus_child_state, focus_child_material, self.focus_state
        )
        """
        Shown when any descendant of the Scroll is focused. Uses the focus state if no state is specified.
        """
        self.default_base_state: State = load_state(
            default_base_state, default_base_material, None
        )
        """
        The default State of the scrollbar base.
        """

        self.default_handle_state: State = load_state(
            default_handle_state, default_handle_material, None
        )
        """
        The default State of the scrollbar handle.
        """

        self.hover_handle_state: State = load_state(
            hover_handle_state, hover_handle_material, self.default_handle_state
        )
        """
        Shows when the scrollbar handle is hovered hover. Uses the default handle state if no state is specified.
        """

        self.click_handle_state: State = load_state(
            click_handle_state, click_handle_material, self.hover_handle_state
        )
        """
        Shows when the scrollbar handle is grabbed. Uses the handle hover state if no state is specified.
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

        self.focus_self: bool = focus_self
        """
        Modifies how the Scroll behaves with keyboard / controller navigation. If set to True, the Scroll itself 
        is focusable. If you press enter when the Scroll is focused, the first child of the Scroll is focused.
        """

        self.align_element_v: list[str] = list(align_element_v)
        """
        How elements should be aligned in VScrolls.
        """
        self.align_element_h: list[str] = list(align_element_h)
        """
        How elements should be aligned in HScrolls.
        """

        self.material_transition: Optional[Transition] = material_transition
        """
        The Transition to use when changing background States.
        """
        self.base_material_transition: Optional[Transition] = base_material_transition
        """
        The Transition to use when changing scrollbar base States.
        """
        self.handle_material_transition: Optional[
            Transition
        ] = handle_material_transition
        """
        The Transition to use when changing scrollbar handle States.
        """

        self.state_func: Callable[["Scroll"], "State"] = (
            state_func if state_func is not None else default_state_func
        )
        """
        The function that determines which background state is active. Can be replaced for more control over the Scroll's states.
        """
        self.base_state_func: Callable[["Scroll"], "State"] = (
            base_state_func if base_state_func is not None else default_base_state_func
        )
        """
        The function that determines which scrollbar base state is active. Can be replaced for more control over the Scroll's states.
        """
        self.handle_state_func: Callable[["Scroll"], "State"] = (
            handle_state_func
            if handle_state_func is not None
            else default_handle_state_func
        )
        """
        The function that determines which scrollbar handle state is active. Can be replaced for more control over the Scroll's states.
        """

    def set_as_default(self) -> "ScrollStyle":
        defaults.scroll = self
        return self

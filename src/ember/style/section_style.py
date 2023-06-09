from typing import Optional, Literal, TYPE_CHECKING, Callable, Sequence

if TYPE_CHECKING:
    pass

from .. import common as _c
from ..common import MaterialType
from .style import Style

from ..transition.transition import Transition

from ..state.state import State
from ..state.background_state import BackgroundState
from ..size import SizeType, SequenceSizeType, FIT, OptionalSequenceSizeType
from ..position import SequencePositionType, CENTER, Position
from ..ui.section import Section


class SectionStyle(Style):
    _ELEMENT = Section

    @staticmethod
    def default_state_func(section: "Section") -> BackgroundState:
        if section._state:
            return section._state
        if section.layer.element_focused is section:
            return section._style.focus_state
        return section._style.default_state

    def __init__(
        self,
        size: SequenceSizeType = (FIT, FIT),
        content_pos: SequencePositionType = CENTER,
        content_size: OptionalSequenceSizeType = None,
        width: SizeType = None,
        height: SizeType = None,
        default_state: Optional[BackgroundState] = None,
        focus_state: Optional[BackgroundState] = None,
        default_material: Optional[MaterialType] = None,
        focus_material: Optional[MaterialType] = None,
        material_transition: Optional[Transition] = None,
        state_func: Callable[["Section"], "BackgroundState"] = default_state_func,
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
        The default State.
        """

        self.focus_state: BackgroundState = BackgroundState._load(
            focus_state, focus_material, fallback_state=self.default_state
        )
        """
        The State used when the Section is focused.
        """

        self.material_transition: Optional[Transition] = material_transition
        """
        The Transition to use when changing States.
        """

        self.state_func: Callable[["Section"], "BackgroundState"] = state_func
        """
        The function that determines which state is active. Can be replaced for more control over the Section's states.
        """

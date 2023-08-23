from typing import Optional, TYPE_CHECKING, Callable, Sequence

if TYPE_CHECKING:
    pass

from ..common import MaterialType, FocusType, FOCUS_CLOSEST
from .style import Style



from ..size import SizeType, SequenceSizeType, FIT, OptionalSequenceSizeType, Size
from ember.position.position import Position, CENTER, SequencePositionType
from ember.base.container import Container


class ContainerStyle(Style):
    _ELEMENT = Container

    @staticmethod
    def default_state_func(container: "Container") -> BackgroundState:
        if container._state:
            return container._state
        return container._style.default_state

    def __init__(
        self,
        size: SequenceSizeType = (FIT, FIT),
        width: SizeType = None,
        height: SizeType = None,
        content_pos: SequencePositionType = CENTER,
        content_size: OptionalSequenceSizeType = None,
        default_state: Optional[BackgroundState] = None,
        default_material: Optional[MaterialType] = None,
        spacing: Optional[int] = None,
        min_spacing: int = 20,
        focus_on_entry: FocusType = FOCUS_CLOSEST,
        material_transition: Optional["Transition"] = None,
        state_func: Callable[["Container"], "BackgroundState"] = default_state_func,
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

        self.spacing: Optional[int] = spacing
        """
        The spacing between the elements. If set to None, the elements will 
        be spaced evenly the fill the whole Container. 
        """

        self.min_spacing: int = min_spacing
        """
        The minimum spacing between the elements. Only effective if the 'spacing' attribute is None.
        """

        self.focus_on_entry: FocusType = focus_on_entry
        """
        Whether the ember.CLOSEST or ember.FIRST element of the container should be focused 
        when the container is entered. 
        """

        self.material_transition: Optional["Transition"] = material_transition
        """
        The Transition to use when changing States.
        """

        self.state_func: Callable[["Container"], "State"] = state_func
        """
        The function that determines which state is active. Can be replaced for more control over the Container's states.
        """

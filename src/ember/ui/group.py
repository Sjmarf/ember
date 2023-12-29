from .multi_element_container import MultiElementContainer
from .has_geometry import HasGeometry


class Group(MultiElementContainer):
    def unpack(self) -> tuple["HasGeometry",...]:
        return self._elements
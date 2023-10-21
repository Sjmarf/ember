from typing import NewType

Axis = NewType("Axis", int)

HORIZONTAL = Axis(0)
VERTICAL = Axis(1)
axis: Axis = HORIZONTAL

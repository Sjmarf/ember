.. _custom_material_guide:

Custom Materials
===================================================

This guide assumes that you're comptetent at using Ember.

Introduction
------------------------

You can implement a custom material in Ember by inheriting from the :py:class:`Material<ember.material.Material>` ABC.

You are required to implement the :py:meth:`Material.render()<ember.material.Material.render()` method when you do this.
The signature of this method is shown below:

.. code-block:: python

    def render(
        self,
        element: ember.Element,
        surface: pygame.Surface,
        pos: tuple[float, float],
        size: tuple[float, float],
        alpha: int,
    ) -> Optional[pygame.Surface]:
        pass

This method is called every tick while the surface is on-screen. The method should return a pygame Surface object that is **exactly** the size specified in the :code:`size` parameter of the function.

Additionally, you can choose to override the :py:meth:`Material.draw()<ember.material.Material.draw()` method. This method is responsible for actually drawing the material to a surface. Here is its signature:

.. code-block:: python

    def draw(
        self,
        element: "Element",
        surface: pygame.Surface,
        pos: tuple[int, int],
        size: tuple[int, int],
        alpha: int,
    ) -> None:
        pass

By default, this function just calls the :py:meth:`Material.render()<ember.material.Material.render()` method as shown below.

.. code-block:: python

    def draw(
        self,
        element: "Element",
        surface: pygame.Surface,
        pos: tuple[int, int],
        size: tuple[int, int],
        alpha: int,
    ) -> None:
        surf = self.render(element, surface, pos, size, alpha)
        if surf is not None:
            surface.blit(surf, pos)

However, there are certain situations where replacing the draw logic may be more performant. However, implementing :code:`draw` does *not* mean that you shouldn't implement :code:`render` - it's still called inside of certain Transitions.

Material Subclasses
--------------------------
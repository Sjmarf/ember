.. _transition_guide:

Transitions
===================================================

This page assumes that you've read the :ref:`Element Guide<element_guide>`.

Introduction
------------------------

Consider this basic View:

.. code-block:: python

    text = ember.Text("Hello")
    view = ember.View(text)

We can modify the contents of the Text element using the :py:meth:`Text.set_text()<ember.ui.Text.set_text()>` method.

.. code-block:: python

    text.set_text("World")


.. image:: _static/transition_guide/fade.gif
  :width: 160
  :align: right

When we do this, the text changes from "Hello" to "World" instantly. If we want to modify this behaviour, we can use a **Transition** object. The :py:class:`Fade<ember.transition.Fade>` transition fades between the two surfaces over a given duration.

.. code-block:: python

    transition = ember.transition.Fade(duration=0.5)
    text.set_text("World", transition=transition)

You can use transitions in other element methods, too - :py:meth:`Text.set_color()<ember.ui.Text.set_color()>` and :py:meth:`Surface.set_surface()<ember.ui.Surface.set_surface()>`, for example. Additionally, transitions are supported when modifying the contents of a container through methods such as :py:meth:`MultiElementContainer.set_elements()<ember.ui.base.MultiElementContainer.set_elements()>` and :py:meth:`MultiElementContainer.append()<ember.ui.base.MultiElementContainer.append()>`.

Types of Transition
----------------------

Currently, there are two types of transition. I'll be adding more options in future, though.

The :py:class:`Fade<ember.transition.Fade>` transition performs the transition by slowly decreasing the opacity of the old text and increasing the opacity of the new text.

.. figure:: _static/transition_guide/surface_fade.gif
  :width: 160
  :align: right

  SurfaceFade

This works well in most cases - but it has a flaw. If there is a pixel that remains opaque on both the first and second surface, the pixel will *not* remain at 100% opacity throughout the transition. This is because, at half-way through the transition, both surfaces are rendered at 50% opacity. 0.5 x 0.5 is 0.75, so the opacity will dip slightly. In some cases, this could be noticable to the user.

To solve this, you can use the :py:class:`SurfaceFade<ember.transition.SurfaceFade>` transition instead. Unlike Fade, this transition works by blending the outgoing and incoming surfaces using numpy. This solves the transparency issue. However, it is more resource-intensive and only works in some cases.

Reusing Transitions
----------------------

You can pass the same Transition object to as many methods as you like, and it'll be handled correctly. You don't need to create a new transition each time if you don't want to.

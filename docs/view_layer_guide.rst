.. _view_layer_guide:

Using ViewLayers
===================================================

This page assumes that you've read the :ref:`Element Guide<element_guide>`.

How a View *really* works
----------------------------

Views are made up of a number of :py:class:`ViewLayer<ember.ui.ViewLayer>` objects. The View renders its layers from first to last when :py:meth:`View.update()<ember.ui.View.update()>` is called. Each layer can have a single element attributed to it.

When you create a View as shown below, a ViewLayer is created internally and the element you pass to the View constructor is attributed to that ViewLayer.

.. code-block:: python

    view = ember.View(
        ember.VStack(
            ember.Button(),
            ember.Button()
        )
    )

That is just a quick shortcut - you can initialise the ViewLayer yourself instead if you so wish.

.. code-block:: python

    layer = ember.ViewLayer(
        ember.VStack(
            ember.Button(),
            ember.Button()
        )
    )

    view = ember.View(layer)

Adding more layers
----------------------

We can add more layers to our View using the :py:meth:`View.add_layer()<ember.ui.View.add_layer()>` method.

.. code-block:: python

    new_layer = ember.ViewLayer(
        ember.Button("Second layer!")
    )

    view.add_layer(new_layer)

Similarly to the View constructor, you can pass an element directly to the add_layer() method instead if you so wish.

.. code-block:: python

    view.add_layer(ember.Button("Second layer!"))

When you do this, the second layer will be rendered over the top of the first layer. Only the topmost ViewLayer accepts input from the user. You can modify the ViewLayer's position and size within the parent View by adjusting it's :code:`position` and :code:`size` parameters. This works in exactly the same way as :ref:`Layout element positioning<element_positioning>`.

.. _style_guide:

Styles
===================================================

This page assumes that you've read the :ref:`Element Guide<element_guide>`.

The Problem
------------------------
We've seen that we can create an element and render it on the screen by wrapping it in a :py:class:`View<ember.ui.View>`. In this example, I've created a :py:class:`Text<ember.ui.Text>` element that reads "Hello world", is red, and expands to fill the available space on the x axis.

.. code-block:: python

    view = ember.View(
        ember.Text(
            "Hello world",
            color="red",
            width=ember.FILL
        )
    )

We've also seen that you can arrange multiple elements vertically using a :py:class:`VStack<ember.ui.VStack>` Container:

.. code-block:: python

    view = ember.View(
        ember.Text(
            "Hello",
            color="red",
            width=ember.FILL
        ),
        ember.Text(
            "Goodbye",
            color="red",
            width=ember.FILL
        )
    )

Both Text elements in the code above share the :code:`color` and :code:`width` parameters. If we want **all** Text elements in the stack to look the same, we have to specify these parameters for *every* Text element that we add to the stack. This could get cumbersome if we add lots of Text elements.

The Solution
------------------------
This is where **styles** come in. The term 'style' refers to a type of class that lets you consolidate some of the elements' parameters into a single place.

Each type of Element has a corresponding Style class. You can use :py:class:`TextStyle<ember.style.TextStyle>` to style Text objects as shown below:

.. code-block:: python

    text_style = ember.TextStyle(
        color="red",
        width=ember.FILL
    )

    view = ember.View(
        ember.Text(
            "Hello",
            style=text_style
        ),
        ember.Text(
            "Goodbye",
            style=text_style
        )
    )

This is much better!

Default Styles
------------------------

If no :code:`style` parameter is specified in an element's constructor, a default Style will be applied. These default styles are set when you call :py:func:`ember.style.load()` at the start of your program. If you like, you can override a default style by calling :py:meth:`Style.set_as_default()<ember.style.Style.set_as_default()>`. Doing so will set the Style object as the default for every element type that uses that Style type.

For example:

.. code-block:: python

    text_style = ember.TextStyle(
        color="red",
        width=ember.FILL
    )

    # Set text_style as the default TextStyle for all Text objects
    text_style.set_as_default()

    view = ember.View(
        ember.Text("Hello"),
        ember.Text("Goodbye")
    )

If you pass an element type to :code:`set_as_default`, the style will be set as default for only that Element and subclasses of that Element. For example - calling :code:`ContainerStyle.set_as_default(ember.Stack)` will set the Style as the default for *exclusively* VStack and HStack elements, as opposed to all container elements.

You can access existing Style defaults by calling :code:`ember.default_styles.get()` as shown below. This will return the Style object that would be used as the default for the specified element type.

.. code-block:: python
    ember.default_styles.get(ember.Stack)

Alternatively, you can access the defaults using properties. Each property just calls :code:`.get()` under the hood, but the property is typehinted to allow for code completion in your IDE.

.. code-block:: python
    ember.default_styles.view
    ember.default_styles.button
    ember.default_styles.text_field
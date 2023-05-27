.. _element_guide:

Element Guide
===================================================

This page is an in-depth explanation of what Elements are and how you can use them to create menus. All elements can be found under the :code:`ember.ui` module or straight from :code:`ember`, and all inherit from the base :py:class:`ember.ui.Element` class.

**This page assumes a strong knowledge of Python (including OOP) and Pygame.**

Basic Setup
------------------------
To do anything in Ember, you must first call these functions at the start of your project:

.. code-block:: python

clock = pygame.time.Clock()
ember.init(clock)
ember.style.load("pixel_dark")

You must pass the clock that you will use to control your project framerate to :py:func:`ember.init`. The first argument of :py:func:`ember.style.load` controls what your UI will look like. You can load any style from the list of built-in styles listed below, or load your own custom style.

Built-in styles (pixel art styles are prefixed with :code:`pixel_`):

- :code:`dark`
- :code:`pixel_dark`
- :code:`pixel_plastic`
- :code:`pixel_stone`

In addition to the steps described above, you must also call :code:`ember.update` each game tick where Ember is used.

Creating a UI
------------------------

The most basic element is the :py:class:`Text` element. Given a string, it will render that string as text on the screen. To display an element on the screen, it must be contained within a :py:class:`ember.ui.View` object like this:

.. code-block:: python

view = ember.View(
    ember.Text("Hello world")
)

You must call :py:meth:`ember.ui.View.update` each tick, and :py:meth:`ember.ui.View.update` for each event in the Pygame event stack. An example script is shown below, with ember-related code highlighted:

.. code-block:: python
   :linenos:
   :emphasize-lines: 6,7,11,12,13,16,21,22

    import pygame
    import ember

    pygame.init()
    clock = pygame.time.Clock()
    ember.init(clock)
    ember.style.load("dark")

    screen = pygame.display.set_mode((600, 600))

    view = ember.View(
        ember.Text("Hello world")
    )

    is_running = True

    while is_running:
        for event in pygame.event.get():
            view.event(event)
            if event.type == pygame.QUIT:
                is_running = False

        screen.fill("black")
        ember.update()
        view.update(screen)

        clock.tick(60)
        pygame.display.flip()

    pygame.quit()

.. _element-positioning:

Displaying multiple elements on the screen
---------------------------------------------
A View can only hold one element at a time. If we want to display more than one element in a View, we have to wrap the elements in a **container**. Containers are a type of element that can hold other elements.

The first container we'll look at is the :py:class:`ember.ui.VStack` container. You can pass any number of elements to this container, and they will be displayed in a vertical list on the screen.

.. code-block:: python

view = ember.View(
    ember.VStack(
        ember.Text("Hello")
        ember.Text("World")
    )
)

Similarly, the :py:class:`ember.ui.HStack` container displays elements in a horizontal list:

.. code-block:: python

view = ember.View(
    ember.HStack(
        ember.Text("Hello")
        ember.Text("World")
    )
)

Remember, containers such as the VStack and HStack are also elements. This means that you can nest them inside of each other, like this:

view = ember.View(
    ember.VStack(
        ember.Text("1")
        ember.HStack(
            ember.Text("2")
            ember.Text("3")
        )
    )
)

Buttons
------------------------

Lets look at our first interactive element - the :py:class:`Button<ember.ui.Button>`.

.. code-block:: python

view = ember.View(
    ember.Button()
)

Just like a container, you can pass any element to the Button constructor. This element will then be displayed on the surface of the button.

.. code-block:: python

view = ember.View(
    ember.Button(
        Text("Hello world")
    )
)

If you pass a string to the Button instead of an Element, a Text object will be created for you.

.. code-block:: python

# This code is equivalent to the previous code
view = ember.View(
    ember.Button("Hello world")
)

When the user clicks the button, an `ember.BUTTONCLICKED` event is emitted. You can listen for this event in the Pygame event stack just like you would with any pygame event. The event object will have the following attributes:

- :code:`button` - The Button element that posted the event.
- :code:`text` - The text displayed on the element (a string) *if* the child of the Button is a Text object.

.. _element-sizing:
Element Sizing
------------------------
All elements have a size. You can change the size of an element using the :code:`size`, :code:`width` and :code:`height` parameters when you intialise the element.

 The :code:`size` element takes either a sequence of sizes or a single size. If you pass a sequence of sizes, the contents of the sequence will be used for the width and height of the element. If you pass a single size, it will be used for *both* the width and height of the element.

If no size is specified, a default will be used. This default is determined by the element's :ref:`style`.

.. code-block:: python

    # 20 pixels wide, and the default height.
    ember.Button(width=20)

    # 20 pixels high, and the default width.
    ember.Button(height=20)

    # 50 pixels wide and 20 pixels high.
    ember.Button(size=(50,20))

    # 30 pixels wide and 30 pixels high.
    ember.Button(size=30)

There are other ways to describe size, too.

- You can pass :code:`ember.FILL` as a size value, and the element will expand to fill the maximum space available.

- You can use :code:`ember.FIT` as a size value, and the element will shrink to fit the size of any child elements it may have.

.. code-block:: python

    # The button expands to fill the available space on the x axis.
    ember.Button("Hello world", width=ember.FILL)

    # The button shrinks on the x-axis to the width of it's text.
    ember.Button("Hello world", width=ember.FIT)

Both :code:`ember.FILL` and :code:`ember.FIT` support the :code:`+-*/` operators. This allows you to use them in interesting ways, as shown below:

.. code-block:: python

    # The button's width is the maximum available space, minus 10 pixels.
    ember.Button("Hello world", width=ember.FILL - 10)

    # The button's width is half of the maximum available space.
    ember.Button("Hello world", width=ember.FILL / 2)

    # The button's width is the width of the text 'Hello world', but with a padding of 10 pixels.
    ember.Button("Hello world", width=ember.FIT + 10)

Element Positioning
------------------------

In Ember, element positioning is handled by the container that it is in. The exception is the :py:class:`ember.ui.Layout` container, which *does* allow you to specify absolute values. You can do this by specifying the :code:`position` parameter when you conteuct the element:

.. code-block:: python

    # 10 pixels on the x-axis and 5 pixels on the y-axis
    button = ember.Button(position=(10,5))

    view = ember.View(
        ember.Layout(
            button
        )
    )

Alternatively, you can also pass an anchor as the position. For example:

.. code-block:: python

    # Locked to the top-left
    ember.Button(position=ember.TOPLEFT)

    # Locked to the bottom-right
    ember.Button(position=ember.BOTTOMRIGHT)

    # 50 pixels on the x-axis, and locked to the bottom of the Layout
    ember.Button(position=(50, ember.BOTTOM))

These anchors support the :code:`+-` operators, meaning that you can add padding like this:

.. code-block:: python

    # 10 pixels from the bottom-right on both the x and y axes
    ember.Button(position=(ember.RIGHT-10, ember.BOTTOM-10))

Here is a full list of anchors that you can use:

    - LEFT
    - RIGHT
    - TOP
    - BOTTOM
    - CENTER

    - TOPLEFT = (LEFT, TOP)
    - TOPRIGHT = (RIGHT, TOP)
    - BOTTOMLEFT = (LEFT, BOTTOM)
    - BOTTOMRIGHT = (BOTTOM, RIGHT)

    - MIDLEFT = (LEFT, CENTER)
    - MIDRIGHT = (RIGHT, CENTER)
    - MIDTOP = (CENTER, TOP)
    - MIDBOTTOM = (CENTER, BOTTOM)
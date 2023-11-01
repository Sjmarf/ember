.. _style_guide:

Styling Elements
===================================================

Ember comes with a number of 'ui styles' built-in. Each style is stored as a submodule of :code:`ember.style`, and must be imported explicitly to be used. Each style contains a number of Element classes similar to those found under :code:`ember.ui`. These classes inherit from :code:`ember.ui` elements, and extend them to provide additional functionality.

You can import a UI style as shown below. The only style available right now is :code:`pixel_dark`, which is a pixel-art style. By release, we'll have a wider range of both pixel-art and non-pixel-art styles to choose from.

.. code-block:: python

    from ember.style import pixel_dark as ui

In this chapter, we'll cover how to use the built-in styles. In later chapters, we'll cover how you can create styles yourself.

Generic setup
----------------

The :code:`pixel_dark` style is a pixel art style. Because the pixel art is rendered at a small scale, we'll have to create an intermediate surface to draw the UI on, which we will then scale and draw to the display surface. This is standard practise when creating pixel art games in Pygame.

Here's an example showing how you might do this. Note the :code:`ember.set_display_zoom` call, which is highlighted. This tells ember how much it should scale the mouse position readings by. It does not affect how ember renders the UI.

Every style has a :code:`background_color` attribute that you may wish to use as a background for your menus.

.. code-block:: python
   :linenos:
   :emphasize-lines: 16, 24

    import pygame
    import ember
    from ember.style import pixel_dark as ui

    pygame.init()
    clock = pygame.time.Clock()

    ember.init()
    ember.set_clock(clock)

    ZOOM = 3
    DISPLAY_SIZE = (150, 100)

    screen = pygame.display.set_mode((DISPLAY_SIZE[0]*ZOOM, DISPLAY_SIZE[1]*ZOOM))
    display = pygame.Surface(DISPLAY_SIZE)
    ember.set_display_zoom(ZOOM)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        display.fill(ui.background_color)
        screen.blit(pygame.transform.scale(display, screen.get_size()), (0,0))
        clock.tick(60)
        pygame.display.flip()

    pygame.quit()


Text
--------------------

The :code:`ui.Text` class inherits from `ember.Text`. Unlike `ember.Text`, you don't need to specify a font for this element. The default value for the :code:`font` parameter is a pixel-art font that fits the style. This makes creating many Text objects much more concise!

.. code-block:: python

    with ember.View() as view:
        ui.Text("Hello, world!")

Button
-------------------

Previously, we've created buttons with backgrounds by adding a :py:class:`Panel<ember.ui.Panel>` element followed by a :py:class:`Text<ember.ui.Text>` element:

.. code-block:: python

    font = ember.PygameFont("arial", 40)

    with ember.View() as view:
        with ember.Button(size=(200, 50)):
            with ember.ZStack():
                ember.Panel("red")
                ember.Text("Click me!", color="white", font=font)


:py:class:`ui.Button<ember.style.pixel_dark.Button>` makes this syntax much simpler. It creates a :py:class:`Panel<ember.ui.Panel>` internally when you create the button, so that you don't have to specify it yourself.

We've only seen how to apply solid colors to a Panel so far, but there are several other options too. :py:class:`ui.Button<ember.style.pixel_dark.Button>` uses a more advanced type of Panel that renders a :code:`pygame.Surface` texture rather than a solid color. We'll look more at this later.

.. note::
    The default size for the basic :py:class:`ember.Button` element that we looked at previously is :code:`ember.FIT`, which means that it will shrink to fit the size of it's contents by default. :py:class:`ui.Button<ember.style.pixel_dark.Button>` has a different default size of 70 x 21 pixels, which is a size that looks nice at this scale.

    If you don't like the default button size and want to set a new default, it's easy to do so:

    .. code-block:: python

        ui.Button.w.default_value = 100
        ui.Button.h.default_value = 20


    This works on every other element too.

Here's what our syntax looks like now, by using both the :py:class:`ui.Text<ember.style.pixel_dark.Text>` :py:class:`ui.Button<ember.style.pixel_dark.Button>` elements.

.. code-block:: python

    with ember.View() as view:
        with ui.Button():
            ui.Text("Click me!")

This is much cleaner, right? But we can improve this even more! If you pass a string to the :py:class:`ui.Button<ember.style.pixel_dark.Button>` constructor, it'll create an instance of :py:class:`ui.Text<ember.style.pixel_dark.Text>` automatically!

.. code-block:: python

    with ember.View() as view:
        ui.Button("Click me!")


ToggleButton
-------------------

:py:class:`ember.ToggleButton<ember.ui.ToggleButton>` is a subclass of :py:class:`ember.Button<ember.ui.Button>`, and adds an :code:`active` property that is toggled between :code:`True` and :code:`False` by the button when it is clicked.

The :code:`pixel_dark` style currently offers two different subclasses of :py:class:`ember.ToggleButton<ember.ui.ToggleButton>` - :py:class:`ui.ToggleButton<ember.style.pixel_dark.ToggleButton>` and :py:class:`ui.Switch<ember.style.pixel_dark.Switch>`.

.. code-block:: python

    with ember.View() as view:
        with ember.VStack(spacing=6):
            ui.Button("Click me!")
            ui.ToggleButton("Click me!")
            ui.Switch()


Because these element types are subclasses of :py:class:`ember.Button<ember.ui.Button>`, you can listen for :code:`ember.CLICKEDDOWN` events to detect when they are clicked. In addition, you can listen for :code:`ember.TOGGLEON` and :code:`ember.TOGGLEOFF` to detect specific states.

Stacks
-----------

Styles provide subclasses of :py:class:`ember.VStack<ember.ui.VStack>` and :py:class:`ember.HStack<ember.ui.HStack>` too. In the case of :code:`pixel_dark`, the minimum spacing of the Stacks has been increased from 0 to 6.

You can add :py:class:`ui.Divider<ember.style.pixel_dark.Divider>` elements to nicely separate your elements. The orientation of the Divider will change automatically depending on whether it is inside of a :py:class:`ember.VStack<ember.ui.VStack>` or :py:class:`ember.HStack<ember.ui.HStack>`.

Here's a more complex UI:

.. code-block:: python

    with ember.View() as view:
        with ui.VStack(w=140):
            ui.Text("Options")
            ui.Divider()
            for i in range(1, 4):
                with ui.HStack(w=ember.FILL):
                    ui.Text(f"Option {i}")
                    ui.Switch()
            ui.Divider()
            with ui.HStack(w=ember.FILL):
                ui.Button("Cancel", w=ember.FILL)
                ui.Button("Save", w=ember.FILL)
.. _style_guide:

Styling Elements
===================================================

Ember comes with a number of 'ui styles' built-in. Each style is stored as a submodule of :code:`ember.style`, and must be imported explicitly to be used. You can import a UI style as shown below. The only style available right now is :code:`pixel_dark` - by release, we'll have a wider range of styles to choose from.

.. code-block:: python

    from ember.style import pixel_dark as ui

In this chapter, we'll cover how to use the built-in styles. In later chapters, we'll cover how you can create styles yourself.

Each style module contains a number of Element classes similar to those found under :code:`ember.ui`. These classes inherit from :code:`ember.ui` elements, and extend them to provide additional functionality.

Generic setup
----------------

The :code:`pixel_dark` style is a pixel art style. In future, we'll have a range of both pixel-art and non pixel-art styles. Because the pixel art style is rendered at a small scale, we'll have to create an intermediate surface to draw the UI on, which we will then scale and draw to the display surface. This is standard practise when creating pixel art games in Pygame.

Here's an example showing how you might do this. Note the :code:`ember.set_display_zoom` call, which is highlighted. This tells ember how much it should scale it's mouse position readings by. It does not affect how ember renders the UI.

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
            ember.Panel("red")
            ember.Text("Click me!", color="white", font=font)


:py:class:`ui.Button<ember.style.pixel_dark.Button>` makes this syntax much simpler. Firstly, it creates a :py:class:`Panel<ember.ui.Panel>` internally when you create the button, so that you don't have to specify it yourself.

We've only seen how to apply solid colors to a Panel so far, but there are several other options too. :py:class:`ui.Button<ember.style.pixel_dark.Button>` uses a more advanced type of Panel that renders a :code:`pygame.Surface` texture rather than a solid color. We'll look more at this later.

.. note::
    The default size for the basic :py:class:`ember.Button` element that we looked at previously is :code:`ember.FIT`, which means that it will shrink to fit the size of it's contents by default. :py:class:`ui.Button<ember.style.pixel_dark.Button>` has a different default size of 70 x 21 pixels, which is a size that looks nice at this scale. You can, of course, override this preset when creating an instance of :py:class:`ui.Button<ember.style.pixel_dark.Button>` by specifying :code:`size`/:code:`w`/:code:`h` parameters in the Button constructor.

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


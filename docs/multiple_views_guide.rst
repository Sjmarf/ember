.. _multiple_views_guide:

Managing Multiple Views
===========================

This page assumes that you've read the :ref:`Element Guide<element_guide>`, :ref:`Style Guide<style_guide>`, :ref:`Transition Guide<transition_guide>` and :ref:`ViewLayer Guide<view_layer_guide>`.

If you have more than one menu in your project, it's usually best to create a separate View for each menu rather than using a single View. Below is a basic example that could be suitable for smaller projects. For large-scale projects with lots of menus, you should consider using a class system instead.

.. code-block:: python
   :linenos:

    import pygame
    import ember

    pygame.init()
    clock = pygame.time.Clock()
    ember.init(clock)
    ember.style.load("dark")

    screen = pygame.display.set_mode((400, 400))


    view1 = ember.View(ember.Button("Switch to View 2"))
    view2 = ember.View(ember.Button("Switch to View 1"))

    current_view = view1

    while True:
        for event in pygame.event.get():
            current_view.event(event)

            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == ember.BUTTONCLICKED:
                current_view = view2 if (current_view is view1) else view1

        screen.fill("black")
        ember.update()
        current_view.update(screen)

        clock.tick(60)
        pygame.display.flip()

Transitioning Between Views
---------------------------

:py:class:`ViewLayer<ember.ui.ViewLayer>` objects support transitions when appearing and disappearing. You can start these transitions by calling :py:meth:`ViewLayer.start_transition_in()<ember.ui.ViewLayer.start_transition_in()>` and :py:meth:`ViewLayer.start_transition_out()<ember.ui.ViewLayer.start_transition_out()>` respectively. The parent :py:class:`View<ember.ui.View>` object also has these methods; calling them will start a transition for the topmost layer of the View.

.. code-block:: python

    view = ember.View(
        ember.Button("Hello world")
    )

    view.start_transition_in(ember.transition.Fade(0.5))

If you don't pass a transition to :code:`start_transition_in()`, the value of the ViewLayer's :code:`transition_in` attribute will be used:

.. code-block:: python

    view = ember.View(
        ember.Button("Hello world"),
        transition_in=ember.transition.Fade(0.5)
    )

    view.start_transition_in()

If :code:`transition_in` is not specified, the ViewLayer will inherit the transition from its :py:class:`ViewStyle<ember.style.ViewStyle>`.

.. code-block:: python

    ember.default_styles.view.transition_in = ember.transition.Fade(0.5)

    view = ember.View(
        ember.Button("Hello world")
    )

    view.start_transition_in()

(All this applies to :code:`transition_out` too, by the way).

You can set :code:`ViewStyle.auto_transition_in` to True to call :code:`ViewLayer.start_transition_in()` automatically when the ViewLayer is initialised.

.. code-block:: python

    ember.default_styles.view.transition_in = ember.transition.Fade(0.5)
    ember.default_styles.view.auto_transition_in = True

    view = ember.View(
        ember.Button("Hello world")
    )

View Transition Events
---------------------------

There are some events to help you with transitioning Views.

When a ViewLayer's exit transition finishes, the :code:`ember.VIEWEXITFINISHED` event is posted. We can listen for this event and perform an action when it appears in the stack. Consider this example code:

.. code-block:: python

    class MainMenu:
        def __init__(self):
            self.new_game_button = ember.Button("New Game")

            self.view = ember.View(
                self.new_game_button,
                transition_out=ember.transition.Fade(0.5)
            )

        # This method is called every tick.
        def render(self):
            self.view.render(screen)

        # This method is called for every event that appears in the Pygame event stack.
        def event(self, event: pygame.event.Event):
            self.view.event(event)

            if event.type == ember.BUTTONCLICKED:
                self.view.start_transition_out()

            elif event.type == ember.VIEWEXITFINISHED:
                # Switch to a different menu
                pass

This works great. But there's a problem - we can't distinguish where the :code:`ember.VIEWEXITFINISHED` event was posted from. To demonstrate the problem, lets add a second button to our View:

.. code-block:: python

    class MainMenu:
        def __init__(self):
            self.new_game_button = ember.Button("New Game")
            self.settings_button = ember.Button("Settings")

            self.view = ember.View(
                ember.VStack(
                    self.new_game_button,
                    self.settings_button
                ),
                transition_out=ember.transition.Fade(0.5)
            )

        # This method is called every tick.
        def render(self):
            self.view.render(screen)

        # This method is called for every event that appears in the Pygame event stack.
        def event(self, event: pygame.event.Event):
            self.view.event(event)

            if event.type == ember.BUTTONCLICKED:
                # We can distinguish between the two buttons here.
                if event.element is self.new_game_button:
                    print("New Game")
                elif event.element is self.settings_button:
                    print("Settings")

                # But this distinction is lost when we call start_transition_out!
                self.view.start_transition_out()

            elif event.type == ember.VIEWEXITFINISHED:
                # We don't know which button was clicked at this point.
                pass

Luckily, we can preserve this information using the :code:`cause` parameter of :code:`start_transition_out`. If you pass a value for this parameter, it will be included as an attribute of the :code:`ember.VIEWEXITFINISHED` event.

.. code-block:: python

    # This method is called for every event that appears in the Pygame event stack.
    def event(self, event: pygame.event.Event):
        self.view.event(event)

        if event.type == ember.BUTTONCLICKED:
            self.view.start_transition_out(cause=event.element)

        elif event.type == ember.VIEWEXITFINISHED:
            if event.cause is self.new_game_button:
                # Go to the New Game menu.
                pass
            elif event.cause is self.settings_button:
                # Go to the Settings menu.
                pass

If you don't specify a value for :code:`cause`, :code:`None` will be used.

Additionally, you can specify as many keyword arguments as you like in :code:`start_transition_out` and they'll be passed along to the :code:`ember.VIEWEXITFINISHED` event.
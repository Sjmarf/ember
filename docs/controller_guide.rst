.. _controller_guide:

Controller Navigation
===================================================

Ember supports controller input for navigating menus via the `pygame.joystick module <https://pyga.me/docs/ref/joystick.html>`_. The new Pygame CE `pygame.controller module <https://pyga.me/docs/ref/sdl2_controller.html>`_ module is not yet supported.

Ember is currently in alpha, and this feature is not yet fully fleshed-out. Notably, Button remappings are not yet possible. Additionally, I'm only able to test this feature with a PS4 controller, so you may notice some unexpected behaviour if using a different controller. If you do, let me know on Discord or Github.

You need to populate the :code:`ember.joysticks` list with your :code:`pygame.joystick.Joystick` objects in order for Ember to recognise your controller's input.

Example usage:

.. code-block:: python

    # Create pygame joystick objects
    pygame.joystick.init()
    joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
    # Populate ember's list of active joysticks
    ember.joysticks = joysticks


Disabling controller navigation for a View
----------------------------------------------

Controller and Keyboard navigation can be disabled by setting :code:`keyboard_nav = False` for a View.

.. code-block:: python

    view = ember.View(
        ember.Button(),
        keyboard_nav = False
    )
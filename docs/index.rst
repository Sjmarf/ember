Ember Documentation
===================================================

**THIS LIBRARY AND THIS DOCUMENTATION AND ARE A WIP. DO NOT USE THIS LIBRARY (for now).**

Ember is a free and open-source UI library built for `Pygame CE <https://github.com/pygame-community/pygame-ce>`_.
Ember aims to be as easy to use, unrestrictive, and performant as possible.

Ember is currently in alpha, and is likely to be unstable. If you find a bug, or there's a particular feature you want to see, 
feel free to `create an issue on GitHub <https://github.com/Sjmarf/ember/issues>`_ if one does not already exist. 
We make no promises of backwards compatibility at this time - features may be changed or removed without warning.

Features
---------------
- Readable, compact syntax.
- Integration with Pygame's event system for fluid handling of UI interactions.
- An easy-to-use animation API.
- Extensive customisation, with the ability to create custom UI elements and animation logic with ease.
- Built with pixel art in mind. Ember offers several built-in pixel art styles, as well as the ability to load your own pixel-art fonts from a spritesheet.
- Support for keyboard and controller navigation.

Getting Started
---------------
To get started with Ember, follow through the series of articles listed below. These should be read in order.

- :ref:`element_guide`
- :ref:`style_guide`

Support
---------
If you have any questions or need help, you can find me (@sjmarf) on the `Pygame Discord Server <https://discord.gg/pygame>`_.

Alternative Pygame UI libraries
---------------------------
- `Pygame GUI <https://pygame-gui.readthedocs.io/en/latest/>`_
- `Pygame Menu <https://github.com/ppizarror/pygame-menu/>`_


Contributing
---------------------
I'm open to contributions. You are of course free to fork, modify and redistribute the library under the terms of the license if you so wish. If you have any questions, feel free to DM me `on Discord <https://discord.gg/pygame>`_ @sjmarf.

To install the module in a developer environment, run :code:`python3 -m build` followed by :code:`pip install . --force-reinstall` in the project directory.

If you'd rather avoid reinstalling ember every time you make a change, you can add the :code:`src` folder to :code:`sys.path` manually. Here's how you can do this for scripts running from the :code:`examples` directory, for example:

.. code-block:: python

        path = os.getcwd().replace(f"examples", "src")
        sys.path.append(path)
        import ember

.. toctree::
   :caption: Getting Started
   :hidden:

   element_guide
   style_guide

.. toctree::
   :caption: API Reference
   :hidden:

   ui
   material

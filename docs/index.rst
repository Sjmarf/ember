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
- :ref:`material_guide`
- :ref:`transition_guide`
- :ref:`state_guide`
- :ref:`font_guide`

Support
---------
If you have any questions or need help, you can find me (@sjmarf) on the `Pygame Discord Server <https://discord.gg/pygame>`_.

Performance
-----------------

Due to Ember’s high-level design and large feature-set, it is less performant than if you were to implement just the features you need in a custom UI system. Whether Ember is a good fit for you depends on your use case.

In most cases, Ember runs fine. I was able to run the `complex.py` example at a stable 60fps on a low-power PC. This example program includes a dense layout of Ember UI elements, large bodies of text and animations; all rendered on a large surface. If you want to run this example yourself, you can find it under the ‘examples’ folder in your Ember directory.

Alternative Pygame UI libraries
---------------------------
- `Pygame GUI <https://pygame-gui.readthedocs.io/en/latest/>`_
- `Pygame Menu <https://github.com/ppizarror/pygame-menu/>`_


Contributing
---------------------
I'm open to contributions. You are of course free to fork, modify and redistribute the library under the terms of the license if you so wish. If you have any questions, feel free to DM me `on Discord<https://discord.gg/pygame>`_ @sjmarf.

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

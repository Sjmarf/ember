.. _font_guide:

Fonts
===================================================


This page assumes that you've read all the previous guides in the 'getting started' section of the sidebar.

Basic Fonts
----------------

Lets create a :py:class:`Text<ember.ui.Text>` element with a custom :py:class:`TextStyle<ember.style.TextStyle>`.

.. code-block:: python

	text_style = ember.TextStyle()

	text = ember.Text("Hello World", style=text_style)

We can change the font by specifying an :py:class:`ember.Font<ember.font.Font>` object as the :code:`font` parameter
in the TextStyle constructor. The ember.Font object wraps a pygame Font object for use in Ember.
We can create an ember.Font object like this:

.. code-block:: python
	
	font = ember.Font(pygame.Font("arial", 36))
	
Or alternatively, like this:

.. code-block:: python
	
	font = ember.Font("arial", 36)
	

ember.Font exists to store additional attributes that pygame.Font doesn't support.
For example, you can adjust the line spacing by modifying the :code:`line_spacing` argument.

.. code-block:: python
	
	font = ember.Font("arial", 36, line_spacing=30)
	
There are other keyword arguments, too, but you probably won't need them. Consult the API reference for :py:class:`ember.font.Font` 
for a full list.

Pixel Fonts
--------------

For pixel-art projects, it is possible to load a pixel art TTF font using the :py:class:`ember.Font<ember.font.Font>` class as described above. As an alternative option, Ember offers the :py:class:`ember.PixelFont<ember.font.PixelFont>` class, which can be used to load a pixel art font from a PNG sprite sheet. This section describes the use of the PixelFont class.

PixelFont makes it easier to create and load your own pixel art fonts, and also allows for additional functionality that the regular ember.Font object does not support. However, it should be noted that PixelFont doesn't support languages that require text shaping, such as arabic.

Default PixelFonts
......................

Ember offers a number of built-in fonts that use the PixelFont system:

TODO

Creating your own PixelFont
.................................

See :ref:`custom_font_guide`.
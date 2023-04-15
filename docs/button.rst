.. _ui-button:

==================
:mod:`ember.ui.Button`
==================

.. currentmodule:: ember.ui

.. autoclass:: Button

    A Button is an interactive :ref:`element`. Buttons can hold exactly one child element, usually a :ref:`ui-text` object, which is rendered on the button.

    When you construct a Button, you can pass any element as the first argument and it will be used as the button's child element. If you want the button to have no child element, you can pass :code:`None` instead. If you pass *several* elements to the Button constructor, they will be placed in a :ref:`HStack<ui-stack>` for you. If you pass a string, it will be converted into a :ref:`ui-text` object.

    .. code-block:: python

        # Button with no child element.
        ember.Button(None)

        # Button with the text "Hello world".
        ember.Button(ember.Text("Hello world"))

        # Is equivalent to ember.Button(ember.Text("Hello world")).
        ember.Button("Hello world")

        # If you pass multiple elements, they will be wrapped with a HStack automatically.
        ember.Button("Hello", ember.Icon("tick"))

    When the button is clicked, it will post the :code:`ember.BUTTONCLICKED` event. You can listen for this event in the event stack. The :code:`Event` object has the following attributes:

    - :code:`element`: Element - The Button that posted the event.
    - :code:`text`: str - The text on the button as a string, if the Button's child element is an :ref:`ui-text` object.

    Attributes
    ................

    .. autoattribute:: can_hold
    .. autoattribute:: hold_delay
    .. autoattribute:: hold_start_delay
    .. autoattribute:: focus_when_clicked
    .. autoattribute:: root
    .. autoattribute:: parent
    .. autoattribute:: is_hovered
    .. autoattribute:: is_clicked
    .. autoattribute:: is_visible
    .. autoattribute:: rect
    .. autoattribute:: material_controller

    Properties
    ................

    .. autoattribute:: element
    .. autoattribute:: style
    .. autoattribute:: disabled

    Methods
    ................

    .. automethod:: set_element
    .. automethod:: set_style
    .. automethod:: set_disabled
    .. automethod:: get_size
    .. automethod:: get_abs_size
    .. automethod:: set_size
    .. automethod:: get_width
    .. automethod:: get_abs_width
    .. automethod:: set_width
    .. automethod:: get_height
    .. automethod:: get_abs_height
    .. automethod:: set_height

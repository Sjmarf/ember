.. _ui-stack:

==================
:mod:`ember.ui.VStack` / :mod:`ember.ui.HStack`
==================

.. currentmodule:: ember.ui

.. autoclass:: VStack
.. autoclass:: HStack

    A Stack is a collection of :ref:`Elements<ui-element>`. There are two types of Stack - VStack and HStack. VStacks arrange their elements vertically, whereas HStacks arrange their elements horizontally. Other than that, the behaviours of the two classes are identical.

    Attributes
    ................

    .. autoattribute:: root
    .. autoattribute:: parent
    .. autoattribute:: is_visible
    .. autoattribute:: rect
    .. autoattribute:: material_controller

    Properties
    ................

    .. autoattribute:: elements
    .. autoattribute:: style

    Methods
    ................

    .. automethod:: set_elements
    .. automethod:: set_style
    .. automethod:: get_size
    .. automethod:: get_abs_size
    .. automethod:: set_size
    .. automethod:: get_width
    .. automethod:: get_abs_width
    .. automethod:: set_width
    .. automethod:: get_height
    .. automethod:: get_abs_height
    .. automethod:: set_height

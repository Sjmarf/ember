.. _ui-list:

==================
:mod:`ember.ui.VList` / :mod:`ember.ui.HList`
==================

.. currentmodule:: ember.ui

.. autoclass:: VList
.. autoclass:: HList

    Lists are subclasses of :ref:`Stacks<ui-stack>` There are two types of List - VList and HList. VLists arrange their elements vertically, whereas HLists arrange their elements horizontally. Other than that, the behaviours of the two classes are identical.

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
    .. autoattribute:: list_style

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

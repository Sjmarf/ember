# Style guide for Elements

This style guide is intended for developer use, and does not concern users of the library. 

When writing code for UI Elements:

## Parameters

Parameters should be ordered as follows:

- The parameters that aren't common to all elements, in order of importance.
- disabled (if applicable)
- position
- size
- width
- height
- style

## Methods

Methods that should never be called by the user should be protected (_single_undescore), *even if* they are called by other classes within Ember.

Methods should be defined in this order, for consistency:
  - \_\_init__
  - \_\_repr__
  - Any other magic methods
  - \_render
  - \_update
  - \_update_rect_chain_down
  - \_update_rect_chain_up
  - \_set_layer_chain 
  - \_focus_chain
  - \_event
  - \_on_unfocus
  - Any other protected methods
  - Any public methods, and property proxy methods
  - Properties, if applicable
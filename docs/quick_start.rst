.. _quick-start:

Quick Start Guide
=================

This guide assumes a strong knowledge of Python (including OOP) and Pygame.

Here's a basic Pygame structure:

.. code-block:: python
   :linenos:

    import pygame
    pygame.init()

    screen = pygame.display.set_mode((600, 600))
    clock = pygame.time.Clock()
    is_running = True

    while is_running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False

        clock.tick(60)
        pygame.display.flip()

    pygame.quit()

import pygame

FOCUSED = pygame.event.custom_type()
UNFOCUSED = pygame.event.custom_type()

HOVERED = pygame.event.custom_type()
UNHOVERED = pygame.event.custom_type()

DISABLED = pygame.event.custom_type()
ENABLED = pygame.event.custom_type()

CLICKEDDOWN = pygame.event.custom_type()
CLICKEDUP = pygame.event.custom_type()

ACTIVATED = pygame.event.custom_type()
DEACTIVATED = pygame.event.custom_type()

TOGGLEDON = pygame.event.custom_type()
TOGGLEDOFF = pygame.event.custom_type()

VALUEMODIFIED = pygame.event.custom_type()

VIEWEXITSTARTED = pygame.event.custom_type()
VIEWEXITFINISHED = pygame.event.custom_type()

TRANSITIONSTARTED = pygame.event.custom_type()
TRANSITIONFINISHED = pygame.event.custom_type()

TEXTFIELDMODIFIED = pygame.event.custom_type()
TEXTFIELDCLOSED = pygame.event.custom_type()

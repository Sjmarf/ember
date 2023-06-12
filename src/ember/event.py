import pygame

VIEWEXITSTARTED = pygame.event.custom_type()
VIEWEXITFINISHED = pygame.event.custom_type()

ELEMENTFOCUSED = pygame.event.custom_type()
ELEMENTUNFOCUSED = pygame.event.custom_type()

TRANSITIONSTARTED = pygame.event.custom_type()
TRANSITIONFINISHED = pygame.event.custom_type()

BUTTONCLICKED = pygame.event.custom_type()
TOGGLECLICKED = pygame.event.custom_type()
SLIDERMOVED = pygame.event.custom_type()
TEXTFIELDMODIFIED = pygame.event.custom_type()
TEXTFIELDCLOSED = pygame.event.custom_type()

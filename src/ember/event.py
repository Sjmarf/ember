import pygame

MENUEXITSTARTED = pygame.event.custom_type()
MENUEXITFINISHED = pygame.event.custom_type()

ELEMENTFOCUSED = pygame.event.custom_type()
ELEMENTUNFOCUSED = pygame.event.custom_type()

TRANSITIONSTARTED = pygame.event.custom_type()
TRANSITIONFINISHED = pygame.event.custom_type()

BUTTONCLICKED = pygame.event.custom_type()
TOGGLECLICKED = pygame.event.custom_type()
LISTITEMSELECTED = pygame.event.custom_type()
TEXTFIELDMODIFIED = pygame.event.custom_type()
TEXTFIELDCLOSED = pygame.event.custom_type()

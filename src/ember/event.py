import pygame

ELEMENTFOCUSED = pygame.event.custom_type()
ELEMENTUNFOCUSED = pygame.event.custom_type()

ELEMENTHOVERED = pygame.event.custom_type()
ELEMENTUNHOVERED = pygame.event.custom_type()

ELEMENTDISABLED = pygame.event.custom_type()
ELEMENTENABLED = pygame.event.custom_type()

BUTTONDOWN = pygame.event.custom_type()
BUTTONUP = pygame.event.custom_type()

TOGGLEON = pygame.event.custom_type()
TOGGLEOFF = pygame.event.custom_type()

SLIDERMOVED = pygame.event.custom_type()
SLIDERCONTROLACTIVATED = pygame.event.custom_type()
SLIDERCONTROLDEACTIVATED = pygame.event.custom_type()

SCROLLMOVED = pygame.event.custom_type()

VIEWEXITSTARTED = pygame.event.custom_type()
VIEWEXITFINISHED = pygame.event.custom_type()

TRANSITIONSTARTED = pygame.event.custom_type()
TRANSITIONFINISHED = pygame.event.custom_type()

TEXTFIELDMODIFIED = pygame.event.custom_type()
TEXTFIELDCLOSED = pygame.event.custom_type()

import pygame
import ember
import os
import sys
import abc

os.chdir(__file__.replace("example2.py", ""))

try:
    path = os.getcwd().replace(f"examples", "src")
    sys.path.append(path)
    print("PATH1", str(path))
    import ember  # noqa
except ModuleNotFoundError:
    path = os.path.join(os.getcwd(), "src")
    sys.path.append(str(path))
    print("PATH2", str(path))
    import ember  # noqa


pygame.init()
clock = pygame.time.Clock()
ember.init(clock)
ember.style.load("dark")

screen = pygame.display.set_mode((400, 400))


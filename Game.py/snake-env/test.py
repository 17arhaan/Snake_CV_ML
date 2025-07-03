import os
import pygame
# os.environ['SDL_AUDIODRIVER'] = 'dummy'  # Use a dummy audio driver
pygame.init()
# Block irrelevant events
pygame.event.set_blocked(None)  # Block all events
pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN])  # Allow only QUIT and KEYDOWN events

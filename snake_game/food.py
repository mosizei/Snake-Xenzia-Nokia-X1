import pygame
import random

class Food:
    def __init__(self, screen_width, screen_height, block_size):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.block_size = block_size
        self.color = (255, 0, 0)
        self.position = (0, 0)
        self.respawn()

    def respawn(self):
        x = random.randrange(0, self.screen_width, self.block_size)
        y = random.randrange(0, self.screen_height, self.block_size)
        self.position = (x, y)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.position[0], self.position[1], self.block_size, self.block_size))

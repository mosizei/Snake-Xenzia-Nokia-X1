import pygame

class Snake:
    def __init__(self, x, y):
        self.body = [(x, y), (x - 10, y), (x - 20, y)]
        self.direction = "RIGHT"
        self.head_color = (0, 255, 0)
        self.body_color = (0, 200, 0)
        self.block_size = 10

    def move(self):
        x, y = self.body[0]
        if self.direction == "UP":
            y -= self.block_size
        elif self.direction == "DOWN":
            y += self.block_size
        elif self.direction == "LEFT":
            x -= self.block_size
        elif self.direction == "RIGHT":
            x += self.block_size

        self.body.insert(0, (x, y))
        self.body.pop()

    def grow(self):
        self.body.append(self.body[-1])

    def draw(self, surface):
        for index, pos in enumerate(self.body):
            color = self.head_color if index == 0 else self.body_color
            pygame.draw.rect(surface, color, (pos[0], pos[1], self.block_size, self.block_size))

    def change_direction(self, direction):
        if direction == "UP" and self.direction != "DOWN":
            self.direction = "UP"
        elif direction == "DOWN" and self.direction != "UP":
            self.direction = "DOWN"
        elif direction == "LEFT" and self.direction != "RIGHT":
            self.direction = "LEFT"
        elif direction == "RIGHT" and self.direction != "LEFT":
            self.direction = "RIGHT"

    def get_head_position(self):
        return self.body[0]

    def collides_with_self(self):
        return self.get_head_position() in self.body[1:]

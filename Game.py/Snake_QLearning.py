import numpy as np
import random

class LearnSnake:
    def __init__(self):
        # Initialization code...
        self.screen_width = 600
        self.screen_height = 400
        self.snake_size = 10
        self.snake_coords = [(self.screen_height // 2 // self.snake_size, self.screen_width // 2 // self.snake_size)]
        self.snake_length = 1
        self.direction = "right"
        self.food_r, self.food_c = self.generate_food()
        self.board = np.zeros((self.screen_height // self.snake_size, self.screen_width // self.snake_size))
        self.game_close = False

    def get_state(self):
        head_r, head_c = self.snake_coords[-1]
        state = [
            int(self.direction == "left"),
            int(self.direction == "right"),
            int(self.direction == "up"),
            int(self.direction == "down"),
            int(self.food_r < head_r),  # Food is above
            int(self.food_r > head_r),  # Food is below
            int(self.food_c < head_c),  # Food is left
            int(self.food_c > head_c),  # Food is right
            self.is_collision(head_r + 1, head_c),  # Down collision
            self.is_collision(head_r - 1, head_c),  # Up collision
            self.is_collision(head_r, head_c + 1),  # Right collision
            self.is_collision(head_r, head_c - 1)   # Left collision
        ]
        return tuple(state)

    def is_collision(self, row, col):
        return not (0 <= row < self.screen_height // self.snake_size and 0 <= col < self.screen_width // self.snake_size) or \
               (row, col) in self.snake_coords

    def step(self, action):
        # Update direction
        if action == 0:  # Left
            self.direction = "left"
        elif action == 1:  # Right
            self.direction = "right"
        elif action == 2:  # Up
            self.direction = "up"
        elif action == 3:  # Down
            self.direction = "down"

        # Move snake
        head_r, head_c = self.snake_coords[-1]
        if self.direction == "left":
            head_c -= 1
        elif self.direction == "right":
            head_c += 1
        elif self.direction == "up":
            head_r -= 1
        elif self.direction == "down":
            head_r += 1

        if self.is_collision(head_r, head_c):
            self.game_close = True
            return self.get_state(), -10, True  # Negative reward for dying

        self.snake_coords.append((head_r, head_c))

        if (head_r, head_c) == (self.food_r, self.food_c):
            self.snake_length += 1
            self.food_r, self.food_c = self.generate_food()
            return self.get_state(), 1, False  # Reward for eating

        if len(self.snake_coords) > self.snake_length:
            self.snake_coords.pop(0)

        return self.get_state(), 0, False  # Neutral reward for survival

    def generate_food(self):
        while True:
            food_r = random.randint(0, (self.screen_height - self.snake_size) // self.snake_size)
            food_c = random.randint(0, (self.screen_width - self.snake_size) // self.snake_size)
            if (food_r, food_c) not in self.snake_coords:
                return food_r, food_c

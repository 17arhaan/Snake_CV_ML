# SnakeGame.py 

import pygame
import random
import numpy as np
import time

class Color:
    def __init__(self):
        self.white = (255, 255, 255)
        self.black = (0, 0, 0)
        self.neon_red = (255, 0, 0)
        self.cyan = (0, 255, 255)
        self.blue = (0, 0, 255)

class SnakeGame:
    def __init__(self, width, height, padding, speed, player_name):
        self.scale = 2
        self.width = width
        self.height = height
        self.padding = padding
        self.speed = speed
        self.snake_size = int(10 * self.scale)
        self.food_size = int(10 * self.scale)
        self.snake_coords = []
        self.snake_length = 1
        self.direction = "right"
        self.board = np.zeros((self.height // self.snake_size, self.width // self.snake_size))
        self.game_close = False
        self.x = self.width / 2
        self.y = self.height / 2 + self.padding
        self.row, self.col = self.coord_to_idx(self.x, self.y)
        self.board[self.row][self.col] = 1
        self.col_change = 1
        self.row_change = 0
        self.food_row, self.food_col = self.generate_food()
        self.board[self.food_row][self.food_col] = 2
        self.survival_time = 0
        self.player_name = player_name
        self.color = Color()
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height + self.padding))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("bahnschrift", int(18 * self.scale))

    def show_score(self, score):
        text = self.font.render(f"Score: {score}", True, self.color.white)
        self.screen.blit(text, [500 * self.scale, 10])
        player_text = self.font.render(f"Player: {self.player_name}", True, self.color.white)
        self.screen.blit(player_text, [10, 10])

    def draw_snake(self):
        for i in range(len(self.snake_coords) - 1, -1, -1):
            row, col = self.snake_coords[i]
            x, y = self.idx_to_coord(row, col)
            if i == len(self.snake_coords) - 1:
                pygame.draw.rect(self.screen, self.color.blue, [x, y, self.snake_size, self.snake_size])  # Head
            else:
                pygame.draw.rect(self.screen, self.color.cyan, [x, y, self.snake_size, self.snake_size])  # Body

    def game_over_message(self):
        msg = self.font.render("Game over!", True, self.color.neon_red)
        self.screen.blit(msg, [2 * self.width / 5, 2 * self.height / 5 + self.padding])

    def generate_food(self):
        col = int(round(random.randrange(0, self.width - self.food_size) / self.food_size))
        row = int(round(random.randrange(0, self.height - self.food_size) / self.food_size))
        if self.board[row][col] != 0:
            row, col = self.generate_food()
        return row, col

    def coord_to_idx(self, x, y):
        row = int((y - self.padding) // self.snake_size)
        col = int(x // self.snake_size)
        return (row, col)

    def idx_to_coord(self, row, col):
        x = col * self.snake_size
        y = row * self.snake_size + self.padding
        return (x, y)

    def step(self, action="None"):
        if action == "None":
            action = random.choice(["left", "right", "up", "down"])
        else:
            action = ["left", "right", "up", "down"][action]

        self.last_direction = self.direction
        if action == "left" and (self.direction != "right" or self.snake_length == 1):
            self.col_change = -1
            self.row_change = 0
            self.direction = "left"
        elif action == "right" and (self.direction != "left" or self.snake_length == 1):
            self.col_change = 1
            self.row_change = 0
            self.direction = "right"
        elif action == "up" and (self.direction != "down" or self.snake_length == 1):
            self.row_change = -1
            self.col_change = 0
            self.direction = "up"
        elif action == "down" and (self.direction != "up" or self.snake_length == 1):
            self.row_change = 1
            self.col_change = 0
            self.direction = "down"

        if self.col >= self.width // self.snake_size or self.col < 0 or self.row >= self.height // self.snake_size or self.row < 0:
            self.game_close = True

        self.col += self.col_change
        self.row += self.row_change
        self.screen.fill(self.color.black)
        pygame.draw.rect(self.screen, self.color.white, (0, self.padding, self.width, self.height), 1)
        food_x, food_y = self.idx_to_coord(self.food_row, self.food_col)
        pygame.draw.rect(self.screen, self.color.neon_red, [food_x, food_y, self.food_size, self.food_size])
        self.snake_coords.append((self.row, self.col))
        if 0 <= self.row < len(self.board) and 0 <= self.col < len(self.board[0]):
            self.board[self.row][self.col] = 1
        if len(self.snake_coords) > self.snake_length:
            r_del, c_del = self.snake_coords[0]
            del self.snake_coords[0]
            if 0 <= r_del < len(self.board) and 0 <= c_del < len(self.board[0]):
                self.board[r_del][c_del] = 0
        for r, c in self.snake_coords[:-1]:
            if r == self.row and c == self.col:
                self.game_close = True

        self.draw_snake()
        self.show_score(self.snake_length - 1)
        pygame.display.update()

        if self.col == self.food_col and self.row == self.food_row:
            self.food_row, self.food_col = self.generate_food()
            self.board[self.food_row][self.food_col] = 2
            self.snake_length += 1

        self.survival_time += 1

    def run(self):
        current_length = 2
        unchanged_steps = 0
        while not self.game_close:
            self.step()
            self.clock.tick(self.speed)
            if self.snake_length != current_length:
                unchanged_steps = 0
                current_length = self.snake_length
            else:
                unchanged_steps += 1
            if unchanged_steps == 1000:
                break

        if self.game_close:
            self.screen.fill(self.color.black)
            pygame.draw.rect(self.screen, self.color.white, (0, self.padding, self.width, self.height), 1)
            self.game_over_message()
            self.show_score(self.snake_length - 1)
            pygame.display.update()
            time.sleep(2)
        pygame.quit()
        return self.snake_length - 1

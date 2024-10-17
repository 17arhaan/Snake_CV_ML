import pygame
import time
import random
import numpy as np
import pickle
from SnakeQAgent import SnakeQAgent


class SnakeGame:
    def __init__(self, mode="manual"):
        pygame.init()
        self.scale = 2
        self.width = 600 * self.scale
        self.height = 400 * self.scale
        self.pad = 30 * self.scale
        self.snake_size = 10 * self.scale
        self.food_size = 10 * self.scale
        self.speed = 20
        self.mode = mode

        self.snake_coords = [(self.height // 2 // self.snake_size, self.width // 2 // self.snake_size)]
        self.snake_len = 1
        self.direction = "right"
        self.board = np.zeros((self.height // self.snake_size, self.width // self.snake_size))
        self.food_r, self.food_c = self.generate_food()

        self.score = 0
        self.game_over = False

        self.screen = pygame.display.set_mode((self.width, self.height + self.pad))
        pygame.display.set_caption("Snake Game")
        self.font = pygame.font.SysFont("bahnschrift", int(18 * self.scale))
        self.clock = pygame.time.Clock()

    def draw_snake(self):
        for coord in self.snake_coords:
            pygame.draw.rect(self.screen, (0, 255, 0), [coord[1] * self.snake_size, coord[0] * self.snake_size + self.pad, self.snake_size, self.snake_size])

    def generate_food(self):
        food_r = random.randint(0, (self.height - self.food_size) // self.food_size)
        food_c = random.randint(0, (self.width - self.food_size) // self.food_size)
        return food_r, food_c

    def reset_game(self):
        self.snake_coords = [(self.height // 2 // self.snake_size, self.width // 2 // self.snake_size)]
        self.snake_len = 1
        self.direction = "right"
        self.board = np.zeros((self.height // self.snake_size, self.width // self.snake_size))
        self.food_r, self.food_c = self.generate_food()
        self.score = 0
        self.game_over = False

    def step(self, action=None):
        # Handle snake direction based on AI or manual inputs
        if self.mode == "manual":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT and self.direction != "right":
                        action = "left"
                    elif event.key == pygame.K_RIGHT and self.direction != "left":
                        action = "right"
                    elif event.key == pygame.K_UP and self.direction != "down":
                        action = "up"
                    elif event.key == pygame.K_DOWN and self.direction != "up":
                        action = "down"
        else:
            # AI mode: action is passed from QAgent
            if action is None:
                action = random.choice(["left", "right", "up", "down"])
            else:
                action = ["left", "right", "up", "down"][action]

        # Move the snake based on the direction
        if action == "left":
            self.snake_coords.append((self.snake_coords[-1][0], self.snake_coords[-1][1] - 1))
        elif action == "right":
            self.snake_coords.append((self.snake_coords[-1][0], self.snake_coords[-1][1] + 1))
        elif action == "up":
            self.snake_coords.append((self.snake_coords[-1][0] - 1, self.snake_coords[-1][1]))
        elif action == "down":
            self.snake_coords.append((self.snake_coords[-1][0] + 1, self.snake_coords[-1][1]))

        # Collision checks
        head_r, head_c = self.snake_coords[-1]
        if head_r < 0 or head_r >= self.height // self.snake_size or head_c < 0 or head_c >= self.width // self.snake_size:
            self.game_over = True

        if (head_r, head_c) in self.snake_coords[:-1]:
            self.game_over = True

        # Food collision
        if head_r == self.food_r and head_c == self.food_c:
            self.snake_len += 1
            self.score += 1
            self.food_r, self.food_c = self.generate_food()

        # Keep snake length
        if len(self.snake_coords) > self.snake_len:
            self.snake_coords.pop(0)

        # Update game screen
        self.screen.fill((0, 0, 0))
        pygame.draw.rect(self.screen, (255, 0, 0), [self.food_c * self.food_size, self.food_r * self.food_size + self.pad, self.food_size, self.food_size])
        self.draw_snake()

        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, [10, 10])

        pygame.display.update()

    def run(self, agent=None, episodes=1):
        for episode in range(episodes):
            while not self.game_over:
                if self.mode == "ai" and agent:
                    state = agent.env.get_state()
                    action = agent.choose_action(state)
                else:
                    action = None

                self.step(action)
                self.clock.tick(self.speed)

            if self.mode == "ai" and agent:
                agent.train()

            self.reset_game()


if __name__ == "__main__":
    mode = input("Choose mode (manual/ai): ")
    game = SnakeGame(mode=mode)

    if mode == "ai":
        agent = SnakeQAgent(episodes=10000)
        game.run(agent=agent, episodes=10)
    else:
        game.run()

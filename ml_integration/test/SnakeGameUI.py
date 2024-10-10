# SnakeGameUI.py 

import pygame
import pickle
import random
import numpy as np
import time
from Leaderboard import Leaderboard


class Color:
    def __init__(self):
        self.white = (255, 255, 255)
        self.black = (0, 0, 0)
        self.neon_red = (255, 0, 0)
        self.cyan = (0, 255, 255)
        self.blue = (0, 0, 255)

class SnakeGameUI:
    def __init__(self):
        self.scale = 2
        self.width = int(600 * self.scale)
        self.height = int(400 * self.scale)
        self.padding = int(30 * self.scale)
        self.speed = 20
        self.color = Color()
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height + self.padding))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("bahnschrift", int(18 * self.scale))
        self.mode = "menu"
        self.leaderboard = Leaderboard()
        self.run_game()

    def draw_menu(self):
        self.screen.fill(self.color.black)
        title = self.font.render("Snake Game", True, self.color.white)
        manual_button = self.font.render("Manual Mode (Press 1)", True, self.color.cyan)
        ai_button = self.font.render("AI Mode (Press 2)", True, self.color.cyan)
        leaderboard_button = self.font.render("Leaderboard (Press 3)", True, self.color.cyan)
        self.screen.blit(title, [self.width / 2 - 50, self.height / 4])
        self.screen.blit(manual_button, [self.width / 2 - 50, self.height / 2])
        self.screen.blit(ai_button, [self.width / 2 - 50, self.height / 2 + 30])
        self.screen.blit(leaderboard_button, [self.width / 2 - 50, self.height / 2 + 60])
        pygame.display.update()

    def run_game(self):
        running = True
        player_name = ""
        while running:
            if self.mode == "menu":
                self.draw_menu()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_1:
                            self.mode = "manual"
                            player_name = input("Enter Player Name: ")
                        elif event.key == pygame.K_2:
                            self.mode = "ai"
                            player_name = "AI"
                        elif event.key == pygame.K_3:
                            self.mode = "leaderboard"

            elif self.mode == "manual" or self.mode == "ai":
                game = SnakeGame(self.width, self.height, self.padding, self.speed, player_name)
                score = game.run()
                self.leaderboard.update_leaderboard(player_name, score)
                self.mode = "menu"

            elif self.mode == "leaderboard":
                self.leaderboard.display_leaderboard(self.screen, self.font, self.color, self.width, self.height, self.padding)
                self.mode = "menu"

if __name__ == "__main__":
    SnakeGameUI()

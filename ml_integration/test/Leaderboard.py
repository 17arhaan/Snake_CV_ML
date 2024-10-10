# Leaderboard.py

import time
import pygame

class Leaderboard:
    def __init__(self):
        self.leaderboard_data = {}

    def update_leaderboard(self, player_name, score):
        if player_name in self.leaderboard_data:
            self.leaderboard_data[player_name] = max(self.leaderboard_data[player_name], score)
        else:
            self.leaderboard_data[player_name] = score

    def display_leaderboard(self, screen, font, color, width, height, pad):
        screen.fill(color.black)
        title = font.render("Leaderboard", True, color.white)
        screen.blit(title, [width / 2 - 50, pad])
        y_offset = 50
        for player, score in self.leaderboard_data.items():
            text = font.render(f"{player}: {score}", True, color.cyan)
            screen.blit(text, [width / 2 - 100, y_offset])
            y_offset += 30
        pygame.display.update()
        time.sleep(5)
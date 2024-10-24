import random
import numpy as np
import pygame
import pickle
import time
import json

class Color:
    def __init__(self):
        self.white = (255, 255, 255)
        self.black = (0, 0, 0)
        self.neon_red = (255, 0, 0)
        self.cyan = (0, 255, 255)
        self.blue = (0, 0, 255)
        self.green = (0, 255, 0)
        self.beige = (245, 245, 220)
        self.dark_brown = (101, 67, 33)
        self.selected_brown = (139, 69, 19)
        self.tail_glow = (150, 75, 0)
        self.blink_red = (255, 69, 0)

def interpolate_color(color1, color2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(color1, color2))

class SnakeGame:
    def __init__(self, mode='manual', difficulty='medium'):
        self.mode = mode
        self.difficulty = difficulty
        self.scale = 2
        self.w = int(600 * self.scale)
        self.h = int(400 * self.scale)
        self.pad = int(30 * self.scale)
        self.sn_size = int(10 * self.scale)
        self.fd_size = int(10 * self.scale)
        self.sn_coords = [(self.h // self.sn_size // 2, self.w // self.sn_size // 2)]
        self.sn_len = 1
        self.dir = "right"
        self.board = np.zeros((self.h // self.sn_size, self.w // self.sn_size))
        self.game_close = False
        self.x = self.w / 2
        self.y = self.h / 2 + self.pad
        self.r, self.c = self.coord_to_idx(self.x, self.y)
        self.board[self.r][self.c] = 1
        self.col_chg = 1
        self.row_chg = 0
        self.fd_r, self.fd_c = self.mk_food()
        self.board[self.fd_r][self.fd_c] = 2
        self.surv = 0
        self.player_name = "Snake Agent" if mode == 'ai' else ""
        self.latest_ai_score = 0
        self.replay_data = []
        self.menu_selection = 0
        pygame.init()
        self.color = Color()
        self.screen = pygame.display.set_mode((self.w, self.h + self.pad))
        pygame.display.set_caption("Serpentine")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("bahnschrift", int(18 * self.scale))
        self.last_dir = None

    def handle_blocks(self):
        if self.difficulty == 'medium' and self.sn_len in {10, 20, 30, 40}:
            self.add_block()
        elif self.difficulty == 'hard' and self.sn_len in {5, 10, 15, 20}:
            self.add_block()

    def add_block(self):
        free_positions = [(r, c) for r in range(len(self.board)) for c in range(len(self.board[0])) if self.board[r][c] == 0]
        if free_positions:
            block_r, block_c = random.choice(free_positions)
            self.board[block_r][block_c] = 3  # Assuming 3 represents a block

    def change_difficulty(self):
        difficulties = ["Easy", "Medium", "Hard"]
        diff_menu = True
        current_selection = 0
        while diff_menu:
            self.screen.fill(self.color.white)
            for i, difficulty in enumerate(difficulties):
                color = self.color.green if i == current_selection else self.color.black
                text = self.font.render(f"{difficulty}", True, color)
                self.screen.blit(text, [self.w / 3, self.h / 3 + i * 40])

            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        current_selection = (current_selection - 1) % len(difficulties)
                    elif event.key == pygame.K_DOWN:
                        current_selection = (current_selection + 1) % len(difficulties)
                    elif event.key == pygame.K_RETURN:
                        self.difficulty = difficulties[current_selection].lower()
                        diff_menu = False

    def game_menu(self):
        options = ["Start Game", "Change Difficulty", "Quit"]
        menu = True
        while menu:
            self.screen.fill(self.color.white)
            for i, option in enumerate(options):
                color = self.color.selected_brown if i == self.menu_selection else self.color.dark_brown
                text = self.font.render(f"{option}", True, color)
                self.screen.blit(text, [self.w / 3, self.h / 3 + i * 40])

            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.menu_selection = (self.menu_selection - 1) % len(options)
                    elif event.key == pygame.K_DOWN:
                        self.menu_selection = (self.menu_selection + 1) % len(options)
                    elif event.key == pygame.K_RETURN:
                        if options[self.menu_selection] == "Start Game":
                            menu = False
                            self.reset_game()
                            self.run()
                        elif options[self.menu_selection] == "Change Difficulty":
                            self.change_difficulty()
                        elif options[self.menu_selection] == "Quit":
                            pygame.quit()
                            quit()

    def show_score(self, score):
        text = self.font.render(f"Score: {score}", True, self.color.dark_brown)
        self.screen.blit(text, [500 * self.scale, 10])

    def show_player_name(self):
        if self.player_name:
            text = self.font.render(f"Player : {self.player_name}", True, self.color.dark_brown)
            self.screen.blit(text, [10, 10])

    def draw_snake(self):
        num_segments = len(self.sn_coords)
        for i in range(num_segments):
            row, col = self.sn_coords[i]
            x, y = self.idx_to_coord(row, col)
            t = i / (num_segments - 1) if num_segments > 1 else 0
            segment_color = interpolate_color(self.color.dark_brown, self.color.selected_brown, t)
            pygame.draw.rect(self.screen, segment_color, [x, y, self.sn_size, self.sn_size])

    def game_end_msg(self):
        msg = self.font.render("Game over!", True, self.color.dark_brown)
        self.screen.blit(msg, [2 * self.w / 5, 2 * self.h / 5 + self.pad])

    def is_unsafe(self, row, col):
        if self.valid_idx(row, col):
            if self.board[row][col] == 1:
                return 1
            return 0
        else:
            return 1

    def get_state(self):
        hr, hc = self.sn_coords[-1]
        state = []
        state.append(int(self.dir == "left"))
        state.append(int(self.dir == "right"))
        state.append(int(self.dir == "up"))
        state.append(int(self.dir == "down"))
        state.append(int(self.fd_r < hr))
        state.append(int(self.fd_r > hr))
        state.append(int(self.fd_c < hc))
        state.append(int(self.fd_c > hc))
        state.append(self.is_unsafe(hr + 1, hc))
        state.append(self.is_unsafe(hr - 1, hc))
        state.append(self.is_unsafe(hr, hc + 1))
        state.append(self.is_unsafe(hr, hc - 1))
        return tuple(state)

    def valid_idx(self, row, col):
        return 0 <= row < len(self.board) and 0 <= col < len(self.board[0])

    def idx_to_coord(self, row, col):
        x = col * self.sn_size
        y = row * self.sn_size + self.pad
        return (x, y)

    def coord_to_idx(self, x, y):
        row = int((y - self.pad) // self.sn_size)
        col = int(x // self.sn_size)
        return (row, col)

    def mk_food(self):
        col = int(round(random.randrange(0, self.w - self.fd_size) / self.fd_size))
        row = int(round(random.randrange(0, self.h - self.fd_size) / self.fd_size))
        if self.board[row][col] != 0:
            row, col = self.mk_food()
        return row, col

    def game_over(self):
        return self.game_close

    def step(self, action="None"):
        if self.mode == 'manual':
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_close = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT and self.dir != "right":
                        action = "left"
                    elif event.key == pygame.K_RIGHT and self.dir != "left":
                        action = "right"
                    elif event.key == pygame.K_UP and self.dir != "down":
                        action = "up"
                    elif event.key == pygame.K_DOWN and self.dir != "up":
                        action = "down"
        else:
            if action == "None":
                action = random.choice(["left", "right", "up", "down"])
            else:
                action = ["left", "right", "up", "down"][action]

        self.last_dir = self.dir
        if action == "left" and (self.dir != "right" or self.sn_len == 1):
            self.col_chg = -1
            self.row_chg = 0
            self.dir = "left"
        elif action == "right" and (self.dir != "left" or self.sn_len == 1):
            self.col_chg = 1
            self.row_chg = 0
            self.dir = "right"
        elif action == "up" and (self.dir != "down" or self.sn_len == 1):
            self.row_chg = -1
            self.col_chg = 0
            self.dir = "up"
        elif action == "down" and (self.dir != "up" or self.sn_len == 1):
            self.row_chg = 1
            self.col_chg = 0
            self.dir = "down"

        if self.c >= self.w // self.sn_size or self.c < 0 or self.r >= self.h // self.sn_size or self.r < 0:
            self.game_close = True

        self.c += self.col_chg
        self.r += self.row_chg

        # Store step for replay
        self.replay_data.append((self.sn_coords.copy(), self.fd_r, self.fd_c))

        self.screen.fill(self.color.beige)
        pygame.draw.rect(self.screen, self.color.dark_brown, (0, self.pad, self.w, self.h), 1)
        fd_x, fd_y = self.idx_to_coord(self.fd_r, self.fd_c)
        pygame.draw.rect(self.screen, self.color.neon_red, [fd_x, fd_y, self.fd_size, self.fd_size])

        self.sn_coords.append((self.r, self.c))
        if self.valid_idx(self.r, self.c):
            self.board[self.r][self.c] = 1

        if len(self.sn_coords) > self.sn_len:
            r_del, c_del = self.sn_coords[0]
            del self.sn_coords[0]
            if self.valid_idx(r_del, c_del):
                self.board[r_del][c_del] = 0

        for r, c in self.sn_coords[:-1]:
            if r == self.r and c == self.c:
                self.game_close = True

        self.draw_snake()
        self.show_player_name()
        self.show_score(self.sn_len - 1)
        pygame.display.update()

        if self.c == self.fd_c and self.r == self.fd_r:
            self.fd_r, self.fd_c = self.mk_food()
            self.board[self.fd_r][self.fd_c] = 2
            self.sn_len += 1

        self.surv += 1

    def run(self, ep=None):
        running = True
        while running and not self.game_close:
            self.step()
            pygame.time.wait(100)  # Control frame rate for manual mode
        if self.game_close:
            print("Game Over")
            running = False
            self.show_score(self.sn_len - 1)
            pygame.display.update()
            time.sleep(2)
            self.reset_game()
            self.game_menu()

    def reset_game(self):
        self.sn_coords = [(self.h // self.sn_size // 2, self.w // self.sn_size // 2)]
        self.sn_len = 1
        self.dir = "right"
        self.board = np.zeros((self.h // self.sn_size, self.w // self.sn_size))
        self.game_close = False
        self.r, self.c = self.coord_to_idx(self.x, self.y)
        self.board[self.r][self.c] = 1
        self.col_chg = 1
        self.row_chg = 0
        self.fd_r, self.fd_c = self.mk_food()
        self.board[self.fd_r][self.fd_c] = 2
        self.surv = 0
        self.replay_data = []

if __name__ == "__main__":
    game = SnakeGame()
    game.game_menu()

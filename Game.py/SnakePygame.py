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
    def __init__(self, mode='ml'):
        self.mode = mode
        self.show_episode = True
        self.episode = None
        self.scale = 2
        self.w = int(600 * self.scale)
        self.h = int(400 * self.scale)
        self.pad = int(30 * self.scale)
        self.sn_size = int(10 * self.scale)
        self.fd_size = int(10 * self.scale)
        self.spd = 5 if mode == 'manual' else 40
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
        self.player_name = "Snake Agent" if mode == 'ml' else ""
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

    def show_score(self, score):
        text = self.font.render(f"Score: {score}", True, self.color.dark_brown)
        self.screen.blit(text, [500 * self.scale, 10])

    def show_player_name(self):
        # Display the player name on the screen
        if self.mode == 'ml':
            self.player_name = "Snake Agent"
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
        pygame.display.update()
        time.sleep(2)
        print("Game over! Score:", self.sn_len - 1)

    def is_unsafe(self, row, col):
        if self.valid_idx(row, col):
            if self.board[row][col] == 1:
                return 1
            return 0
        else:
            return 1

    def get_state(self):
        # Get the current state of the game for ML Mode
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
        # Check if the given row and column indices are valid
        return 0 <= row < len(self.board) and 0 <= col < len(self.board[0])

    def idx_to_coord(self, row, col):
        # Convert board indices to screen coordinates
        x = col * self.sn_size
        y = row * self.sn_size + self.pad
        return (x, y)

    def coord_to_idx(self, x, y):
        # Convert screen coordinates to board indices
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
        # Perform a step in the game based on the action
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

        # Fill background and draw game elements
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
            # Increase snake length and generate new food
            self.fd_r, self.fd_c = self.mk_food()
            self.board[self.fd_r][self.fd_c] = 2
            self.sn_len += 1

        self.surv += 1

    def run(self, ep):
        # Run the game loop
        if self.mode == 'ml':
            self.show_episode = True
            self.episode = ep
            pygame.display.update()
            fname = f"Game.py\Q_table_results/{ep}.pickle"
            try:
                with open(fname, 'rb') as file:
                    table = pickle.load(file)
            except FileNotFoundError:
                print("Q-table file not found. Please check the path.")
                return
            time.sleep(5)
            cur_len = 2
            unchanged_steps = 0
            while not self.game_over():
                if self.sn_len != cur_len:
                    unchanged_steps = 0
                    cur_len = self.sn_len
                else:
                    unchanged_steps += 1
                state = self.get_state()
                action = np.argmax(table[state])
                if unchanged_steps == 1000:
                    break
                self.step(action)
                self.clock.tick(self.spd)
        else:
            while not self.game_over():
                self.step()
                self.clock.tick(self.spd)
        if self.game_over():
            self.update_leaderboard(self.player_name, self.sn_len - 1)
            self.screen.fill(self.color.beige)
            pygame.draw.rect(self.screen, self.color.white, (0, self.pad, self.w, self.h), 1)
            self.game_end_msg()
            self.show_score(self.sn_len - 1)
            pygame.display.update()
            time.sleep(2)
            self.ask_for_replay()
            self.reset_game()
            self.game_menu()

    def ask_for_replay(self):
        # Prompt the player if they want to watch the replay
        replay_prompt = True
        while replay_prompt:
            self.screen.fill(self.color.beige)
            replay_text = self.font.render("Do you want to watch the replay? (Y/N)", True, self.color.dark_brown)
            self.screen.blit(replay_text, [(self.w - replay_text.get_width()) / 2, self.h / 3])
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    thanks_msg = self.font.render("Thanks For Playing !!", True, self.color.dark_brown)
                    self.screen.fill(self.color.beige)
                    self.screen.blit(thanks_msg, [(self.w - thanks_msg.get_width()) / 2, self.h / 2])
                    pygame.display.update()
                    time.sleep(2)
                    quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_y:
                        self.play_replay()
                        replay_prompt = False
                    elif event.key == pygame.K_n:
                        replay_prompt = False

    def play_replay(self):
        # Play the replay of the game
        for step_index, step in enumerate(self.replay_data):
            sn_coords, fd_r, fd_c = step
            self.screen.fill(self.color.beige)
            pygame.draw.rect(self.screen, self.color.dark_brown, (0, self.pad, self.w, self.h), 1)
            fd_x, fd_y = self.idx_to_coord(fd_r, fd_c)
            pygame.draw.rect(self.screen, self.color.neon_red, [fd_x, fd_y, self.fd_size, self.fd_size])
            score = len(sn_coords) - 1
            self.show_score(score)  # Showing dynamic score in replay
            for i in range(len(sn_coords) - 1, -1, -1):
                row, col = sn_coords[i]
                x, y = self.idx_to_coord(row, col)
                pygame.draw.rect(self.screen, self.color.tail_glow, [x, y, self.sn_size, self.sn_size])
            if step_index % 10 < 5:  # Blinking effect
                pygame.draw.circle(self.screen, self.color.blink_red, (self.w // 2, self.pad // 2), 10)
            pygame.display.update()
            self.clock.tick(self.spd * 7)  # 7x speed replay

    def reset_game(self):
        # Reset game state to initial values
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

    
    def select_difficulty(self):
        difficulty_selected = False
        difficulties = ["Easy", "Medium", "Hard"]
        difficulty_index = 0
        while not difficulty_selected:
            self.screen.fill(self.color.beige)
            title = self.font.render("Select Difficulty", True, self.color.dark_brown)
            self.screen.blit(title, [(self.w - title.get_width()) / 2, self.h / 3 - 60])

            for i, difficulty in enumerate(difficulties):
                color = self.color.selected_brown if i == difficulty_index else self.color.dark_brown
                text = self.font.render(f"--> {difficulty}", True, color)
                self.screen.blit(text, [(self.w - text.get_width()) / 2, self.h / 3 + i * 40])

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    print("Thanks For Playing !!")
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        difficulty_index = (difficulty_index - 1) % len(difficulties)
                    if event.key == pygame.K_DOWN:
                        difficulty_index = (difficulty_index + 1) % len(difficulties)
                    if event.key == pygame.K_RETURN:
                        if difficulty_index == 0:
                            self.spd = 20  # Easy
                        elif difficulty_index == 1:
                            self.spd = 30  # Medium
                        elif difficulty_index == 2:
                            self.spd = 50  # Hard
                        difficulty_selected = True

    def game_menu(self):
        # Display the game menu
        menu = True
        options = ["Manual Mode", "ML Mode", "Leaderboard", "Difficulty", "Quit"]
        while menu:
            self.screen.fill(self.color.beige)
            title = self.font.render("Serpentine", True, self.color.dark_brown)
            self.screen.blit(title, [(self.w - title.get_width()) / 2, self.h / 3 - 60])

            for i, option in enumerate(options):
                color = self.color.selected_brown if i == self.menu_selection else self.color.dark_brown
                text = self.font.render(f"--> {option}", True, color)
                self.screen.blit(text, [self.w / 3, self.h / 3 + i * 40])

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    print("Thanks For Playing !!")
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.menu_selection = (self.menu_selection - 1) % len(options)
                    if event.key == pygame.K_DOWN:
                        self.menu_selection = (self.menu_selection + 1) % len(options)
                    if event.key == pygame.K_RETURN:
                        if self.menu_selection == 0:
                            self.mode = 'manual'
                            self.get_player_name()
                            menu = False
                            self.reset_game()
                            self.run(None)
                        elif self.menu_selection == 1:
                            self.mode = 'ml'
                            menu = False
                            self.reset_game()
                            self.run(10000)
                        elif self.menu_selection == 2:
                            self.show_leaderboard()
                        elif self.menu_selection == 3:
                            self.select_difficulty()
                        elif self.menu_selection == 4:
                            pygame.quit()
                            print("Thanks For Playing !!")
                            quit()
                        elif self.menu_selection == 1:
                            self.mode = 'ml'
                            menu = False
                            self.reset_game()
                            self.run(10000)
                        elif self.menu_selection == 2:
                            self.show_leaderboard()
                        elif self.menu_selection == 3:
                            pygame.quit()
                            print("Thanks For Playing !!")
                            quit()

    def get_player_name(self):
        # Prompt the player to enter their name
        input_active = True
        player_name = ""
        while input_active:
            self.screen.fill(self.color.beige)
            prompt = self.font.render("Name : ", True, self.color.dark_brown)
            name_surface = self.font.render(player_name, True, self.color.selected_brown)
            self.screen.blit(prompt, [self.w / 3, self.h / 3])
            self.screen.blit(name_surface, [self.w / 3 + prompt.get_width() + 10, self.h / 3])
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        player_name = player_name[:-1]
                    else:
                        player_name += event.unicode
        self.player_name = player_name if player_name else "Anonymous"

    def update_leaderboard(self, player_name, score):
        # Update the leaderboard with the player's score
        leaderboard_file = "leaderboard.json"
        try:
            with open(leaderboard_file, "r") as file:
                leaderboard = json.load(file)
        except FileNotFoundError:
            leaderboard = []

        tag = "Snake Agent" if self.mode == 'ml' else "Player"
        new_entry = {"name": player_name, "score": score, "tag": tag}

        existing = next((entry for entry in leaderboard if entry['name'] == player_name and entry['tag'] == tag), None)
        if existing:
            if score > existing['score']:
                existing['score'] = score
        else:
            leaderboard.append(new_entry)

        leaderboard = sorted(leaderboard, key=lambda x: x['score'], reverse=True)[:10]

        with open(leaderboard_file, "w") as file:
            json.dump(leaderboard, file, indent=4)

    def show_leaderboard(self):
        # Display the leaderboard
        leaderboard_file = "leaderboard.json"
        try:
            with open(leaderboard_file, "r") as file:
                leaderboard = json.load(file)
        except FileNotFoundError:
            leaderboard = []

        self.screen.fill(self.color.beige)
        title = self.font.render("Leaderboard", True, self.color.dark_brown)
        self.screen.blit(title, [(self.w - title.get_width()) / 2, 50])

        if not leaderboard:
            empty_msg = self.font.render("No scores available", True, self.color.dark_brown)
            self.screen.blit(empty_msg, [(self.w - empty_msg.get_width()) / 2, self.h / 2])
        else:
            vertical_offset = 100
            gap_between_lines = 40
            leaderboard.sort(key=lambda x: x['score'], reverse=True)
            for i, entry in enumerate(leaderboard):
                name = entry['name'] if entry['name'] else "Anonymous"
                score = entry['score']
                text = self.font.render(f"{name} : {score}", True, self.color.dark_brown)
                self.screen.blit(text, [(self.w - text.get_width()) / 2, vertical_offset])
                vertical_offset += gap_between_lines

        pygame.display.update()
        time.sleep(5)

if __name__ == "__main__":
    game = SnakeGame()
    game.game_menu()
    try:
        if game.mode == 'ml':
            game.run(10000)
        else:
            game.run(None)
    except KeyboardInterrupt:
        print("\t\t\t\t\t!!!Done Already!!!")
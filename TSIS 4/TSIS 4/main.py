import pygame
import json
import sys
from game import run_game, WIDTH, HEIGHT
from db import get_top_10, get_personal_best

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
GRAY = (80, 80, 80)
BLUE = (0, 120, 255)
RED = (255, 0, 0)

class SnakeApp:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("TSIS 4 Snake Game")
        self.clock = pygame.time.Clock()
        
        self.username = ""
        self.settings = self.load_settings()
        self.running = True
        self.current_state = "menu"

    def load_settings(self):
        try:
            with open("settings.json", "r") as file:
                return json.load(file)
        except FileNotFoundError:
            # Дефолтные настройки, если файла нет
            return {"grid": True, "sound": True, "snake_color": [0, 255, 0]}

    def save_settings(self):
        with open("settings.json", "w") as file:
            json.dump(self.settings, file, indent=4)

    def draw_text(self, text, size, color, x, y, center=False):
        font = pygame.font.SysFont("arial", size)
        img = font.render(text, True, color)
        if center:
            rect = img.get_rect(center=(x, y))
            self.screen.blit(img, rect)
        else:
            self.screen.blit(img, (x, y))

    def draw_button(self, text, x, y, w, h):
        mouse = pygame.mouse.get_pos()
        rect = pygame.Rect(x, y, w, h)
        color = BLUE if rect.collidepoint(mouse) else GRAY
        
        pygame.draw.rect(self.screen, color, rect, border_radius=8)
        self.draw_text(text, 28, WHITE, rect.centerx, rect.centery, center=True)
        return rect

    def main_menu(self):
        self.screen.fill(BLACK)
        self.draw_text("SNAKE GAME TSIS 4", 48, GREEN, WIDTH // 2, 70, center=True)
        self.draw_text("Enter username:", 28, WHITE, WIDTH // 2, 160, center=True)

        pygame.draw.rect(self.screen, WHITE, (250, 200, 300, 45), 2)
        self.draw_text(self.username, 28, WHITE, 260, 207)

        play_btn = self.draw_button("Play", 300, 280, 200, 50)
        leaderboard_btn = self.draw_button("Leaderboard", 300, 350, 200, 50)
        settings_btn = self.draw_button("Settings", 300, 420, 200, 50)
        quit_btn = self.draw_button("Quit", 300, 490, 200, 50)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.username = self.username[:-1]
                elif event.key == pygame.K_RETURN:
                    if self.username.strip():
                        self.current_state = "play"
                else:
                    if len(self.username) < 15 and event.unicode.isprintable():
                        self.username += event.unicode
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_btn.collidepoint(event.pos) and self.username.strip():
                    self.current_state = "play"
                elif leaderboard_btn.collidepoint(event.pos):
                    self.current_state = "leaderboard"
                elif settings_btn.collidepoint(event.pos):
                    self.current_state = "settings"
                elif quit_btn.collidepoint(event.pos):
                    self.running = False

    def leaderboard_screen(self):
        self.screen.fill(BLACK)
        self.draw_text("LEADERBOARD TOP 10", 42, GREEN, WIDTH // 2, 50, center=True)

        try:
            rows = get_top_10()
            error = None
        except Exception as e:
            rows = []
            error = str(e)

        if error:
            self.draw_text("Database error:", 26, RED, 100, 130)
            self.draw_text(error[:70], 20, RED, 100, 170)
        else:
            headers = [("Rank", 80), ("Username", 160), ("Score", 340), ("Level", 450), ("Date", 560)]
            for text, x in headers:
                self.draw_text(text, 22, WHITE, x, 120)

            y = 160
            for rank, (user, score, level, played_at) in enumerate(rows, 1):
                self.draw_text(str(rank), 20, WHITE, 90, y)
                self.draw_text(user, 20, WHITE, 160, y)
                self.draw_text(str(score), 20, WHITE, 350, y)
                self.draw_text(str(level), 20, WHITE, 460, y)
                self.draw_text(str(played_at.date()), 20, WHITE, 560, y)
                y += 35

        back_btn = self.draw_button("Back", 300, 520, 200, 50)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN and back_btn.collidepoint(event.pos):
                self.current_state = "menu"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.current_state = "menu"

    def settings_screen(self):
        self.screen.fill(BLACK)
        self.draw_text("SETTINGS", 48, GREEN, WIDTH // 2, 70, center=True)

        grid_text = f"Grid: {'ON' if self.settings['grid'] else 'OFF'}"
        sound_text = f"Sound: {'ON' if self.settings['sound'] else 'OFF'}"

        grid_btn = self.draw_button(grid_text, 280, 180, 240, 50)
        sound_btn = self.draw_button(sound_text, 280, 250, 240, 50)
        color_btn = self.draw_button("Change Snake Color", 250, 320, 300, 50)
        save_btn = self.draw_button("Save & Back", 280, 450, 240, 50)

        pygame.draw.rect(self.screen, tuple(self.settings["snake_color"]), (370, 390, 60, 40))

        colors = [[0, 255, 0], [255, 0, 0], [0, 120, 255], [255, 255, 0], [255, 0, 255]]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if grid_btn.collidepoint(event.pos):
                    self.settings["grid"] = not self.settings["grid"]
                elif sound_btn.collidepoint(event.pos):
                    self.settings["sound"] = not self.settings["sound"]
                elif color_btn.collidepoint(event.pos):
                    idx = (colors.index(self.settings["snake_color"]) + 1) % len(colors)
                    self.settings["snake_color"] = colors[idx]
                elif save_btn.collidepoint(event.pos):
                    self.save_settings()
                    self.current_state = "menu"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.current_state = "menu"

    def game_over_screen(self, score, level):
        self.screen.fill(BLACK)
        try:
            best = get_personal_best(self.username)
        except:
            best = score

        self.draw_text("GAME OVER", 56, RED, WIDTH // 2, 90, center=True)
        stats = [f"Player: {self.username}", f"Final Score: {score}", 
                 f"Level Reached: {level}", f"Personal Best: {best}"]
        
        for i, text in enumerate(stats):
            self.draw_text(text, 30, WHITE, 300, 180 + (i * 50))

        retry_btn = self.draw_button("Retry", 300, 420, 200, 50)
        menu_btn = self.draw_button("Main Menu", 300, 490, 200, 50)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if retry_btn.collidepoint(event.pos):
                    self.current_state = "play"
                elif menu_btn.collidepoint(event.pos):
                    self.current_state = "menu"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.current_state = "menu"

    def run(self):
        while self.running:
            if self.current_state == "menu":
                self.main_menu()
            elif self.current_state == "play":
                result, score, level = run_game(self.screen, self.username)
                if result == "game_over":
                    self.last_score, self.last_level = score, level
                    self.current_state = "game_over_view" # Вспомогательное состояние
                elif result == "menu":
                    self.current_state = "menu"
                elif result == "quit":
                    self.running = False
            elif self.current_state == "game_over_view":
                self.game_over_screen(self.last_score, self.last_level)
            elif self.current_state == "leaderboard":
                self.leaderboard_screen()
            elif self.current_state == "settings":
                self.settings_screen()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = SnakeApp()
    app.run()
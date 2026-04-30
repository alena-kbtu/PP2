import pygame
import sys
from ui import main_menu, username_screen, leaderboard_screen, settings_screen, game_over_screen
from racer import run_game
from persistence import load_settings

class RacerApp:
    def __init__(self):
        pygame.init()
        self.WIDTH = 500
        self.HEIGHT = 700
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("TSIS 3 Racer Game")
        
        self.clock = pygame.time.Clock()
        self.settings = load_settings()
        self.running = True

    def start_game(self):
        username = username_screen(self.screen, self.clock)

        if username is None:
            self.running = False
            return

        game_result, score, distance, coins = run_game(
            self.screen,
            self.clock,
            username,
            self.settings
        )

        if game_result == "quit":
            self.running = False
        elif game_result == "game_over":
            self.handle_game_over(score, distance, coins, username)

    def handle_game_over(self, score, distance, coins, username):
        over_action = game_over_screen(
            self.screen,
            self.clock,
            score,
            distance,
            coins
        )

        if over_action == "quit":
            self.running = False
        elif over_action == "retry":

            game_result, score, distance, coins = run_game(
                self.screen,
                self.clock,
                username,
                self.settings
            )
            if game_result == "game_over":
                self.handle_game_over(score, distance, coins, username)
        elif over_action == "menu":
            pass 

    def run(self):
        while self.running:
            action = main_menu(self.screen, self.clock)

            if action == "quit":
                self.running = False

            elif action == "play":
                self.start_game()

            elif action == "leaderboard":
                if leaderboard_screen(self.screen, self.clock) == "quit":
                    self.running = False

            elif action == "settings":
                if settings_screen(self.screen, self.clock, self.settings) == "quit":
                    self.running = False

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = RacerApp()
    app.run()
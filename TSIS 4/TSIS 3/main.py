import pygame
from ui import main_menu, username_screen, leaderboard_screen, settings_screen, game_over_screen
from racer import run_game
from persistence import load_settings


def main():
    pygame.init()

    screen = pygame.display.set_mode((500, 700))
    pygame.display.set_caption("TSIS 3 Racer Game")

    clock = pygame.time.Clock()

    settings = load_settings()

    running = True

    while running:
        action = main_menu(screen, clock)

        if action == "quit":
            running = False

        elif action == "play":
            username = username_screen(screen, clock)

            if username is None:
                running = False
            else:
                game_result, score, distance, coins = run_game(
                    screen,
                    clock,
                    username,
                    settings
                )

                if game_result == "quit":
                    running = False

                elif game_result == "game_over":
                    over_action = game_over_screen(
                        screen,
                        clock,
                        score,
                        distance,
                        coins
                    )

                    if over_action == "quit":
                        running = False

                    elif over_action == "retry":
                        game_result, score, distance, coins = run_game(
                            screen,
                            clock,
                            username,
                            settings
                        )

                    elif over_action == "menu":
                        pass

        elif action == "leaderboard":
            result = leaderboard_screen(screen, clock)

            if result == "quit":
                running = False

        elif action == "settings":
            result = settings_screen(screen, clock, settings)

            if result == "quit":
                running = False

    pygame.quit()


if __name__ == "__main__":
    main()
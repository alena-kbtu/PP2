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


def load_settings():
    with open("settings.json", "r") as file:
        return json.load(file)


def save_settings(settings):
    with open("settings.json", "w") as file:
        json.dump(settings, file, indent=4)


def draw_text(screen, text, size, color, x, y):
    font = pygame.font.SysFont("arial", size)
    img = font.render(text, True, color)
    screen.blit(img, (x, y))


def draw_button(screen, text, x, y, w, h):
    mouse = pygame.mouse.get_pos()
    rect = pygame.Rect(x, y, w, h)

    color = BLUE if rect.collidepoint(mouse) else GRAY
    pygame.draw.rect(screen, color, rect, border_radius=8)

    font = pygame.font.SysFont("arial", 28)
    img = font.render(text, True, WHITE)
    text_rect = img.get_rect(center=rect.center)
    screen.blit(img, text_rect)

    return rect


def main_menu(screen):
    clock = pygame.time.Clock()
    username = ""

    while True:
        screen.fill(BLACK)

        draw_text(screen, "SNAKE GAME TSIS 4", 48, GREEN, 200, 70)
        draw_text(screen, "Enter username:", 28, WHITE, 250, 160)

        pygame.draw.rect(screen, WHITE, (250, 200, 300, 45), 2)
        draw_text(screen, username, 28, WHITE, 260, 207)

        play_btn = draw_button(screen, "Play", 300, 280, 200, 50)
        leaderboard_btn = draw_button(screen, "Leaderboard", 300, 350, 200, 50)
        settings_btn = draw_button(screen, "Settings", 300, 420, 200, 50)
        quit_btn = draw_button(screen, "Quit", 300, 490, 200, 50)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit", username

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                elif event.key == pygame.K_RETURN:
                    if username.strip() != "":
                        return "play", username
                else:
                    if len(username) < 15 and event.unicode.isprintable():
                        username += event.unicode

            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_btn.collidepoint(event.pos):
                    if username.strip() != "":
                        return "play", username
                elif leaderboard_btn.collidepoint(event.pos):
                    return "leaderboard", username
                elif settings_btn.collidepoint(event.pos):
                    return "settings", username
                elif quit_btn.collidepoint(event.pos):
                    return "quit", username

        pygame.display.flip()
        clock.tick(60)


def leaderboard_screen(screen):
    clock = pygame.time.Clock()

    try:
        rows = get_top_10()
    except Exception as e:
        rows = []
        error = str(e)
    else:
        error = None

    while True:
        screen.fill(BLACK)

        draw_text(screen, "LEADERBOARD TOP 10", 42, GREEN, 210, 50)

        if error:
            draw_text(screen, "Database error:", 26, RED, 100, 130)
            draw_text(screen, error[:70], 20, RED, 100, 170)
        else:
            draw_text(screen, "Rank", 22, WHITE, 80, 120)
            draw_text(screen, "Username", 22, WHITE, 160, 120)
            draw_text(screen, "Score", 22, WHITE, 340, 120)
            draw_text(screen, "Level", 22, WHITE, 450, 120)
            draw_text(screen, "Date", 22, WHITE, 560, 120)

            y = 160
            rank = 1

            for row in rows:
                username, score, level, played_at = row

                draw_text(screen, str(rank), 20, WHITE, 90, y)
                draw_text(screen, username, 20, WHITE, 160, y)
                draw_text(screen, str(score), 20, WHITE, 350, y)
                draw_text(screen, str(level), 20, WHITE, 460, y)
                draw_text(screen, str(played_at.date()), 20, WHITE, 560, y)

                y += 35
                rank += 1

        back_btn = draw_button(screen, "Back", 300, 520, 200, 50)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_btn.collidepoint(event.pos):
                    return "menu"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "menu"

        pygame.display.flip()
        clock.tick(60)


def settings_screen(screen):
    clock = pygame.time.Clock()
    settings = load_settings()

    colors = [
        [0, 255, 0],
        [255, 0, 0],
        [0, 120, 255],
        [255, 255, 0],
        [255, 0, 255]
    ]

    color_index = 0

    if settings["snake_color"] in colors:
        color_index = colors.index(settings["snake_color"])

    while True:
        screen.fill(BLACK)

        draw_text(screen, "SETTINGS", 48, GREEN, 290, 70)

        grid_text = "Grid: ON" if settings["grid"] else "Grid: OFF"
        sound_text = "Sound: ON" if settings["sound"] else "Sound: OFF"

        grid_btn = draw_button(screen, grid_text, 280, 180, 240, 50)
        sound_btn = draw_button(screen, sound_text, 280, 250, 240, 50)
        color_btn = draw_button(screen, "Change Snake Color", 250, 320, 300, 50)
        save_btn = draw_button(screen, "Save & Back", 280, 450, 240, 50)

        current_color = tuple(settings["snake_color"])
        pygame.draw.rect(screen, current_color, (370, 390, 60, 40))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.MOUSEBUTTONDOWN:
                if grid_btn.collidepoint(event.pos):
                    settings["grid"] = not settings["grid"]

                elif sound_btn.collidepoint(event.pos):
                    settings["sound"] = not settings["sound"]

                elif color_btn.collidepoint(event.pos):
                    color_index = (color_index + 1) % len(colors)
                    settings["snake_color"] = colors[color_index]

                elif save_btn.collidepoint(event.pos):
                    save_settings(settings)
                    return "menu"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "menu"

        pygame.display.flip()
        clock.tick(60)


def game_over_screen(screen, username, score, level):
    clock = pygame.time.Clock()

    try:
        best = get_personal_best(username)
    except:
        best = score

    while True:
        screen.fill(BLACK)

        draw_text(screen, "GAME OVER", 56, RED, 250, 90)
        draw_text(screen, f"Player: {username}", 30, WHITE, 300, 180)
        draw_text(screen, f"Final Score: {score}", 30, WHITE, 300, 230)
        draw_text(screen, f"Level Reached: {level}", 30, WHITE, 300, 280)
        draw_text(screen, f"Personal Best: {best}", 30, WHITE, 300, 330)

        retry_btn = draw_button(screen, "Retry", 300, 420, 200, 50)
        menu_btn = draw_button(screen, "Main Menu", 300, 490, 200, 50)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.MOUSEBUTTONDOWN:
                if retry_btn.collidepoint(event.pos):
                    return "retry"
                elif menu_btn.collidepoint(event.pos):
                    return "menu"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "menu"

        pygame.display.flip()
        clock.tick(60)


def main():
    pygame.init()
    pygame.mixer.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("TSIS 4 Snake Game")

    current_screen = "menu"
    username = ""

    while True:
        if current_screen == "menu":
            action, username = main_menu(screen)

            if action == "play":
                current_screen = "play"
            elif action == "leaderboard":
                current_screen = "leaderboard"
            elif action == "settings":
                current_screen = "settings"
            elif action == "quit":
                break

        elif current_screen == "play":
            result, score, level = run_game(screen, username)

            if result == "game_over":
                current_screen = "game_over"
            elif result == "menu":
                current_screen = "menu"
            elif result == "quit":
                break

        elif current_screen == "game_over":
            action = game_over_screen(screen, username, score, level)

            if action == "retry":
                current_screen = "play"
            elif action == "menu":
                current_screen = "menu"
            elif action == "quit":
                break

        elif current_screen == "leaderboard":
            action = leaderboard_screen(screen)

            if action == "menu":
                current_screen = "menu"
            elif action == "quit":
                break

        elif current_screen == "settings":
            action = settings_screen(screen)

            if action == "menu":
                current_screen = "menu"
            elif action == "quit":
                break

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
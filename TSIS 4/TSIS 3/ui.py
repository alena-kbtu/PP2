import pygame
from persistence import load_leaderboard, save_settings

WIDTH = 500
HEIGHT = 700

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (70, 70, 70)
LIGHT_GRAY = (170, 170, 170)
BLUE = (50, 120, 255)
GREEN = (60, 180, 90)
RED = (220, 60, 60)
YELLOW = (240, 200, 60)


def draw_text(screen, text, size, color, x, y, center=True):
    font = pygame.font.SysFont("Arial", size)
    img = font.render(text, True, color)
    rect = img.get_rect()

    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)

    screen.blit(img, rect)


def draw_button(screen, text, x, y, w, h):
    mouse = pygame.mouse.get_pos()
    rect = pygame.Rect(x, y, w, h)

    if rect.collidepoint(mouse):
        pygame.draw.rect(screen, LIGHT_GRAY, rect, border_radius=10)
    else:
        pygame.draw.rect(screen, GRAY, rect, border_radius=10)

    pygame.draw.rect(screen, WHITE, rect, 2, border_radius=10)
    draw_text(screen, text, 30, WHITE, x + w // 2, y + h // 2)

    return rect


def username_screen(screen, clock):
    name = ""
    running = True

    while running:
        screen.fill(BLACK)

        draw_text(screen, "Enter your name", 38, WHITE, WIDTH // 2, 180)
        draw_text(screen, name, 36, YELLOW, WIDTH // 2, 270)
        draw_text(screen, "Press ENTER to start", 24, WHITE, WIDTH // 2, 360)

        pygame.display.update()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name.strip() != "":
                    return name

                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]

                else:
                    if len(name) < 12:
                        name += event.unicode


def main_menu(screen, clock):
    while True:
        screen.fill(BLACK)

        draw_text(screen, "RACER GAME", 48, YELLOW, WIDTH // 2, 130)

        play_btn = draw_button(screen, "Play", 150, 230, 200, 60)
        leader_btn = draw_button(screen, "Leaderboard", 150, 310, 200, 60)
        settings_btn = draw_button(screen, "Settings", 150, 390, 200, 60)
        quit_btn = draw_button(screen, "Quit", 150, 470, 200, 60)

        pygame.display.update()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_btn.collidepoint(event.pos):
                    return "play"

                if leader_btn.collidepoint(event.pos):
                    return "leaderboard"

                if settings_btn.collidepoint(event.pos):
                    return "settings"

                if quit_btn.collidepoint(event.pos):
                    return "quit"


def leaderboard_screen(screen, clock):
    data = load_leaderboard()

    while True:
        screen.fill(BLACK)

        draw_text(screen, "TOP 10 SCORES", 40, YELLOW, WIDTH // 2, 70)

        y = 140

        if len(data) == 0:
            draw_text(screen, "No scores yet", 28, WHITE, WIDTH // 2, 200)
        else:
            for i, item in enumerate(data):
                text = f"{i + 1}. {item['name']} | Score: {item['score']} | {item['distance']}m"
                draw_text(screen, text, 22, WHITE, 40, y, center=False)
                y += 40

        back_btn = draw_button(screen, "Back", 150, 600, 200, 60)

        pygame.display.update()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_btn.collidepoint(event.pos):
                    return "menu"


def settings_screen(screen, clock, settings):
    colors = ["blue", "red", "green", "yellow"]
    difficulties = ["easy", "normal", "hard"]

    while True:
        screen.fill(BLACK)

        draw_text(screen, "SETTINGS", 44, YELLOW, WIDTH // 2, 80)

        sound_text = "Sound: ON" if settings["sound"] else "Sound: OFF"
        sound_btn = draw_button(screen, sound_text, 120, 170, 260, 60)

        color_btn = draw_button(
            screen,
            f"Car color: {settings['car_color']}",
            120,
            260,
            260,
            60
        )

        diff_btn = draw_button(
            screen,
            f"Difficulty: {settings['difficulty']}",
            120,
            350,
            260,
            60
        )

        back_btn = draw_button(screen, "Back", 150, 520, 200, 60)

        pygame.display.update()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_settings(settings)
                return "quit"

            if event.type == pygame.MOUSEBUTTONDOWN:
                if sound_btn.collidepoint(event.pos):
                    settings["sound"] = not settings["sound"]
                    save_settings(settings)

                if color_btn.collidepoint(event.pos):
                    index = colors.index(settings["car_color"])
                    settings["car_color"] = colors[(index + 1) % len(colors)]
                    save_settings(settings)

                if diff_btn.collidepoint(event.pos):
                    index = difficulties.index(settings["difficulty"])
                    settings["difficulty"] = difficulties[(index + 1) % len(difficulties)]
                    save_settings(settings)

                if back_btn.collidepoint(event.pos):
                    save_settings(settings)
                    return "menu"


def game_over_screen(screen, clock, score, distance, coins):
    while True:
        screen.fill(BLACK)

        draw_text(screen, "GAME OVER", 48, RED, WIDTH // 2, 140)
        draw_text(screen, f"Score: {score}", 30, WHITE, WIDTH // 2, 230)
        draw_text(screen, f"Distance: {distance} m", 30, WHITE, WIDTH // 2, 280)
        draw_text(screen, f"Coins: {coins}", 30, WHITE, WIDTH // 2, 330)

        retry_btn = draw_button(screen, "Retry", 150, 440, 200, 60)
        menu_btn = draw_button(screen, "Main Menu", 150, 520, 200, 60)

        pygame.display.update()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.MOUSEBUTTONDOWN:
                if retry_btn.collidepoint(event.pos):
                    return "retry"

                if menu_btn.collidepoint(event.pos):
                    return "menu"
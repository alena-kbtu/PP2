import pygame
import random
import json
import os
from db import save_game_result, get_personal_best


CELL = 20
WIDTH = 800
HEIGHT = 600
ROWS = HEIGHT // CELL
COLS = WIDTH // CELL


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (45, 45, 45)
RED = (255, 0, 0)
DARK_RED = (120, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 120, 255)
PURPLE = (170, 0, 255)
ORANGE = (255, 140, 0)


def load_settings():
    with open("settings.json", "r") as file:
        return json.load(file)


def load_sound(path):
    try:
        return pygame.mixer.Sound(path)
    except:
        return None


def random_cell(snake, food, poison, obstacles, powerup):
    while True:
        pos = (
            random.randint(1, COLS - 2),
            random.randint(3, ROWS - 2)
        )

        if pos not in snake and pos != food and pos != poison and pos not in obstacles:
            if powerup is None or pos != powerup["pos"]:
                return pos


def draw_text(screen, text, size, color, x, y):
    font = pygame.font.SysFont("arial", size)
    img = font.render(text, True, color)
    screen.blit(img, (x, y))


def draw_grid(screen):
    for x in range(0, WIDTH, CELL):
        pygame.draw.line(screen, GRAY, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, CELL):
        pygame.draw.line(screen, GRAY, (0, y), (WIDTH, y))


def create_obstacles(level, snake, food, poison):
    obstacles = []

    if level < 3:
        return obstacles

    count = level * 3

    while len(obstacles) < count:
        pos = (
            random.randint(2, COLS - 3),
            random.randint(4, ROWS - 3)
        )

        head = snake[0]

        if abs(pos[0] - head[0]) <= 2 and abs(pos[1] - head[1]) <= 2:
            continue

        if pos not in snake and pos != food and pos != poison and pos not in obstacles:
            obstacles.append(pos)

    return obstacles


def run_game(screen, username):
    settings = load_settings()

    snake_color = tuple(settings["snake_color"])
    show_grid = settings["grid"]
    sound_on = settings["sound"]

    eat_sound = load_sound("assets/eat.wav")
    poison_sound = load_sound("assets/poison.mp3")
    gameover_sound = load_sound("assets/gameover.mp3")

    clock = pygame.time.Clock()

    snake = [(10, 10), (9, 10), (8, 10)]
    direction = (1, 0)
    next_direction = direction

    score = 0
    level = 1
    foods_eaten = 0

    base_speed = 8
    speed = base_speed

    food = (15, 10)
    food_weight = 1
    food_spawn_time = pygame.time.get_ticks()

    poison = (20, 15)

    powerup = None
    powerup_spawn_time = 0

    active_powerup = None
    powerup_end_time = 0
    shield = False

    obstacles = []

    personal_best = get_personal_best(username)

    running = True
    game_over = False

    while running:
        now = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit", score, level

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and direction != (0, 1):
                    next_direction = (0, -1)
                elif event.key == pygame.K_DOWN and direction != (0, -1):
                    next_direction = (0, 1)
                elif event.key == pygame.K_LEFT and direction != (1, 0):
                    next_direction = (-1, 0)
                elif event.key == pygame.K_RIGHT and direction != (-1, 0):
                    next_direction = (1, 0)
                elif event.key == pygame.K_ESCAPE:
                    return "menu", score, level

        direction = next_direction

        if now - food_spawn_time > 7000:
            food = random_cell(snake, food, poison, obstacles, powerup)
            food_weight = random.choice([1, 2, 3])
            food_spawn_time = now

        if powerup is None and random.randint(1, 120) == 1:
            powerup = {
                "pos": random_cell(snake, food, poison, obstacles, powerup),
                "type": random.choice(["speed", "slow", "shield"])
            }
            powerup_spawn_time = now

        if powerup is not None and now - powerup_spawn_time > 8000:
            powerup = None

        if active_powerup is not None and now > powerup_end_time:
            active_powerup = None
            speed = base_speed + level

        head_x, head_y = snake[0]
        new_head = (head_x + direction[0], head_y + direction[1])

        collision = False

        if (
            new_head[0] < 0 or new_head[0] >= COLS or
            new_head[1] < 2 or new_head[1] >= ROWS
        ):
            collision = True

        if new_head in snake:
            collision = True

        if new_head in obstacles:
            collision = True

        if collision:
            if shield:
                shield = False
                collision = False
                new_head = snake[0]
            else:
                game_over = True

        if game_over:
            if sound_on and gameover_sound:
                gameover_sound.play()

            save_game_result(username, score, level)
            return "game_over", score, level

        snake.insert(0, new_head)

        if new_head == food:
            score += food_weight
            foods_eaten += 1

            if sound_on and eat_sound:
                eat_sound.play()

            food = random_cell(snake, food, poison, obstacles, powerup)
            food_weight = random.choice([1, 2, 3])
            food_spawn_time = now

            if foods_eaten % 3 == 0:
                level += 1
                base_speed += 1
                speed = base_speed
                obstacles = create_obstacles(level, snake, food, poison)

        elif new_head == poison:
            if sound_on and poison_sound:
                poison_sound.play()

            for _ in range(2):
                if len(snake) > 0:
                    snake.pop()

            poison = random_cell(snake, food, poison, obstacles, powerup)

            if len(snake) <= 1:
                if sound_on and gameover_sound:
                    gameover_sound.play()

                save_game_result(username, score, level)
                return "game_over", score, level

        elif powerup is not None and new_head == powerup["pos"]:
            if powerup["type"] == "speed":
                active_powerup = "speed"
                speed = base_speed + level + 5
                powerup_end_time = now + 5000

            elif powerup["type"] == "slow":
                active_powerup = "slow"
                speed = max(4, base_speed + level - 4)
                powerup_end_time = now + 5000

            elif powerup["type"] == "shield":
                shield = True

            powerup = None

        else:
            snake.pop()

        screen.fill(BLACK)

        if show_grid:
            draw_grid(screen)

        pygame.draw.rect(screen, (25, 25, 25), (0, 0, WIDTH, CELL * 2))
        draw_text(screen, f"Player: {username}", 22, WHITE, 10, 8)
        draw_text(screen, f"Score: {score}", 22, WHITE, 180, 8)
        draw_text(screen, f"Level: {level}", 22, WHITE, 310, 8)
        draw_text(screen, f"Best: {personal_best}", 22, WHITE, 430, 8)

        if shield:
            draw_text(screen, "Shield: ON", 22, BLUE, 550, 8)

        if active_powerup:
            draw_text(screen, f"Power: {active_powerup}", 22, YELLOW, 650, 8)

        for part in snake:
            pygame.draw.rect(
                screen,
                snake_color,
                (part[0] * CELL, part[1] * CELL, CELL, CELL)
            )

        food_color = YELLOW if food_weight == 1 else ORANGE
        pygame.draw.rect(
            screen,
            food_color,
            (food[0] * CELL, food[1] * CELL, CELL, CELL)
        )
        draw_text(
            screen,
            str(food_weight),
            16,
            BLACK,
            food[0] * CELL + 6,
            food[1] * CELL + 2
        )

        pygame.draw.rect(
            screen,
            DARK_RED,
            (poison[0] * CELL, poison[1] * CELL, CELL, CELL)
        )

        if powerup is not None:
            if powerup["type"] == "speed":
                color = RED
            elif powerup["type"] == "slow":
                color = BLUE
            else:
                color = PURPLE

            px, py = powerup["pos"]
            pygame.draw.circle(
                screen,
                color,
                (px * CELL + CELL // 2, py * CELL + CELL // 2),
                CELL // 2
            )

        for block in obstacles:
            pygame.draw.rect(
                screen,
                GRAY,
                (block[0] * CELL, block[1] * CELL, CELL, CELL)
            )

        pygame.display.flip()
        clock.tick(speed)
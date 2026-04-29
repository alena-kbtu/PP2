import pygame
import random
import os
from persistence import add_score

WIDTH = 500
HEIGHT = 700

WHITE = (255, 255, 255)
YELLOW = (255, 220, 0)
RED = (220, 60, 60)
GREEN = (60, 200, 90)
BLUE = (60, 120, 255)

ROAD_X = 80
ROAD_WIDTH = 340
LANES = [135, 250, 365]

FINISH_DISTANCE = 5000


# ---------- LOAD IMAGE ----------
def load_image(name, size):
    path = os.path.join("assets", name)
    image = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(image, size)


# ---------- PLAYER ----------
class Player:
    def __init__(self):
        
        self.image = load_image("car yellow.png", (60, 90))
        self.rect = self.image.get_rect()

        
        self.rect.centerx = LANES[1]
        self.rect.bottom = HEIGHT - 20

       
        self.speed = 6

    def move(self):
        
        keys = pygame.key.get_pressed()

        
        if keys[pygame.K_LEFT] and self.rect.left > ROAD_X:
            self.rect.x -= self.speed

        
        if keys[pygame.K_RIGHT] and self.rect.right < ROAD_X + ROAD_WIDTH:
            self.rect.x += self.speed

        
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= self.speed

        
        if keys[pygame.K_DOWN] and self.rect.bottom < HEIGHT:
            self.rect.y += self.speed

    def draw(self, screen):
       
        screen.blit(self.image, self.rect)



# ---------- ENEMY ----------
class EnemyCar:
    def __init__(self, speed, player):
        self.image = load_image("enemycar.png", (60, 90))
        self.rect = self.image.get_rect()

        lane = random.choice(LANES)
        while abs(lane - player.rect.centerx) < 40:
            lane = random.choice(LANES)

        self.rect.centerx = lane
        self.rect.y = random.randint(-700, -100)
        self.speed = speed

    def update(self, road_speed):
        self.rect.y += self.speed + road_speed * 0.2

    def draw(self, screen):
        screen.blit(self.image, self.rect)


# ---------- COIN ----------
class Coin:
    def __init__(self):
        self.image = load_image("coin.png", (40, 40))
        self.rect = self.image.get_rect()
        self.rect.centerx = random.choice(LANES)
        self.rect.y = random.randint(-600, -100)
        self.value = random.choice([1, 2, 3])

    def update(self, speed):
        self.rect.y += speed

    def draw(self, screen):
        screen.blit(self.image, self.rect)


# ---------- OBSTACLE ----------
class Obstacle:
    def __init__(self, kind, player):
        self.kind = kind

        if kind == "barrier":
            self.image = load_image("barrier.png", (80, 50))
        else:
            self.image = load_image("oil.png", (50, 50))

        self.rect = self.image.get_rect()

        lane = random.choice(LANES)
        while abs(lane - player.rect.centerx) < 40:
            lane = random.choice(LANES)

        self.rect.centerx = lane
        self.rect.y = random.randint(-800, -100)

    def update(self, speed):
        self.rect.y += speed

    def draw(self, screen):
        screen.blit(self.image, self.rect)


# ---------- POWER UP ----------
class PowerUp:
    def __init__(self):
        self.kind = random.choice(["nitro", "shield", "repair"])

        if self.kind == "nitro":
            self.image = load_image("nitro.png", (50, 50))
        elif self.kind == "shield":
            self.image = load_image("shield.png", (50, 50))
        else:
            self.image = load_image("repair.png", (50, 50))

        self.rect = self.image.get_rect()
        self.rect.centerx = random.choice(LANES)
        self.rect.y = random.randint(-900, -100)

        self.spawn_time = pygame.time.get_ticks()
        self.timeout = 7000

    def update(self, speed):
        self.rect.y += speed

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def expired(self):
        return pygame.time.get_ticks() - self.spawn_time > self.timeout


# ---------- TEXT ----------
def draw_text(screen, text, size, color, x, y):
    font = pygame.font.SysFont("Arial", size)
    img = font.render(text, True, color)
    screen.blit(img, (x, y))


# ---------- GAME ----------
def run_game(screen, clock, username, settings):
    road = load_image("road.png", (WIDTH, HEIGHT))

    player = Player()

    base_speed = 6
    enemies = [EnemyCar(base_speed, player) for _ in range(3)]
    coins = [Coin() for _ in range(3)]
    obstacles = [Obstacle("barrier", player)]
    powerups = [PowerUp()]

    coin_count = 0
    distance = 0
    score = 0

    active_power = None
    power_start = 0
    power_duration = 4000

    shield = False
    nitro = False

    y1 = 0
    y2 = -HEIGHT

    while True:
        clock.tick(60)

        speed = base_speed + (4 if nitro else 0)

        distance += speed // 2
        score = coin_count * 10 + distance // 10

        # road scroll
        y1 += speed
        y2 += speed

        if y1 >= HEIGHT:
            y1 = -HEIGHT
        if y2 >= HEIGHT:
            y2 = -HEIGHT

        screen.blit(road, (0, y1))
        screen.blit(road, (0, y2))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit", score, distance, coin_count

        player.move()
        player.draw(screen)

        # ENEMIES
        for enemy in enemies[:]:
            enemy.update(speed)
            enemy.draw(screen)

            if enemy.rect.top > HEIGHT:
                enemies.remove(enemy)
                enemies.append(EnemyCar(base_speed, player))

            if player.rect.colliderect(enemy.rect):
                if shield:
                    shield = False
                    active_power = None
                    enemies.remove(enemy)
                    enemies.append(EnemyCar(base_speed, player))
                else:
                    add_score(username, score, distance, coin_count)
                    return "game_over", score, distance, coin_count

        # COINS
        for coin in coins[:]:
            coin.update(speed)
            coin.draw(screen)

            if coin.rect.top > HEIGHT:
                coins.remove(coin)
                coins.append(Coin())

            if player.rect.colliderect(coin.rect):
                coin_count += coin.value
                coins.remove(coin)
                coins.append(Coin())

        # OBSTACLES
        for obs in obstacles[:]:
            obs.update(speed)
            obs.draw(screen)

            if obs.rect.top > HEIGHT:
                obstacles.remove(obs)
                obstacles.append(Obstacle("barrier", player))

            if player.rect.colliderect(obs.rect):
                if obs.kind == "oil":
                    player.speed = 3
                else:
                    if shield:
                        shield = False
                        active_power = None
                        obstacles.remove(obs)
                        obstacles.append(Obstacle("barrier", player))
                    else:
                        add_score(username, score, distance, coin_count)
                        return "game_over", score, distance, coin_count
            else:
                player.speed = 6

        # POWERUPS
        for p in powerups[:]:
            p.update(speed)
            p.draw(screen)

            if p.expired() or p.rect.top > HEIGHT:
                powerups.remove(p)
                powerups.append(PowerUp())

            elif player.rect.colliderect(p.rect):
                if active_power is None:
                    if p.kind == "nitro":
                        nitro = True
                        active_power = "Nitro"
                        power_start = pygame.time.get_ticks()

                    elif p.kind == "shield":
                        shield = True
                        active_power = "Shield"

                    elif p.kind == "repair":
                        if obstacles:
                            obstacles.pop(0)
                        active_power = None

                powerups.remove(p)
                powerups.append(PowerUp())

        # nitro timer
        if nitro:
            if pygame.time.get_ticks() - power_start > power_duration:
                nitro = False
                active_power = None

        # UI
        draw_text(screen, f"Score: {score}", 22, WHITE, 10, 10)
        draw_text(screen, f"Coins: {coin_count}", 22, WHITE, 10, 40)
        draw_text(screen, f"Distance: {distance}", 22, WHITE, 10, 70)

        if active_power:
            draw_text(screen, f"Power: {active_power}", 22, YELLOW, 10, 100)

        if distance >= FINISH_DISTANCE:
            add_score(username, score + 500, distance, coin_count)
            return "game_over", score + 500, distance, coin_count

        pygame.display.update()
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


def load_image(name, size):
    path = os.path.join("assets", name)
    try:
        image = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(image, size)
    except pygame.error:
        surf = pygame.Surface(size)
        surf.fill(RED)
        return surf

def draw_text(screen, text, size, color, x, y):
    font = pygame.font.SysFont("Arial", size)
    img = font.render(text, True, color)
    screen.blit(img, (x, y))


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

class EnemyCar:
    def __init__(self, speed, player):
        self.image = load_image("enemycar.png", (60, 90))
        self.rect = self.image.get_rect()
        self.reset(player)
        self.speed = speed

    def reset(self, player):
        lane = random.choice(LANES)
        while abs(lane - player.rect.centerx) < 40:
            lane = random.choice(LANES)
        self.rect.centerx = lane
        self.rect.y = random.randint(-900, -100)

    def update(self, road_speed):
        self.rect.y += self.speed + road_speed * 0.2

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Coin:
    def __init__(self):
        self.image = load_image("coin.png", (40, 40))
        self.rect = self.image.get_rect()
        self.reset()

    def reset(self):
        self.rect.centerx = random.choice(LANES)
        self.rect.y = random.randint(-800, -100)
        self.value = random.choice([1, 2, 3])

    def update(self, speed):
        self.rect.y += speed

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Obstacle:
    def __init__(self, player, kind=None):
        self.kind = kind if kind else random.choice(["barrier", "oil", "cone"])
        if self.kind == "barrier":
            self.image = load_image("barrier.png", (80, 50))
        elif self.kind == "oil":
            self.image = load_image("oil.png", (50, 50))
        else: 
            self.image = load_image("cone.png", (40, 40))

        self.rect = self.image.get_rect()
        self.reset(player)

    def reset(self, player):
        lane = random.choice(LANES)
        while abs(lane - player.rect.centerx) < 40:
            lane = random.choice(LANES)
        self.rect.centerx = lane
        self.rect.y = random.randint(-1000, -200)

    def update(self, speed):
        self.rect.y += speed

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class PowerUp:
    def __init__(self):
        self.kind = random.choice(["nitro", "shield", "repair"])
        sizes = {"nitro": (50, 50), "shield": (50, 50), "repair": (50, 50)}
        self.image = load_image(f"{self.kind}.png", sizes[self.kind])
        self.rect = self.image.get_rect()
        self.spawn_time = pygame.time.get_ticks()
        self.timeout = 7000
        self.reset()

    def reset(self):
        self.rect.centerx = random.choice(LANES)
        self.rect.y = random.randint(-1200, -300)
        self.spawn_time = pygame.time.get_ticks()

    def update(self, speed):
        self.rect.y += speed

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def expired(self):
        return pygame.time.get_ticks() - self.spawn_time > self.timeout

class Decoration:
    def __init__(self):
        kind = random.choice(["tree.png", "bush.png"])
        self.image = load_image(kind, (60, 60))
        self.rect = self.image.get_rect()
        self.side = random.choice(["left", "right"])
        self.reset()

    def reset(self):
        if self.side == "left":
            self.rect.x = random.randint(0, ROAD_X - 60)
        else:
            self.rect.x = random.randint(ROAD_X + ROAD_WIDTH, WIDTH - 60)
        self.rect.y = random.randint(-800, -100)

    def update(self, speed):
        self.rect.y += speed
        if self.rect.top > HEIGHT:
            self.reset()

    def draw(self, screen):
        screen.blit(self.image, self.rect)


def run_game(screen, clock, username, settings):
    road = load_image("road.png", (WIDTH, HEIGHT))
    player = Player()

    # Инициализация групп объектов
    enemies = [EnemyCar(6, player) for _ in range(3)]
    coins = [Coin() for _ in range(3)]
    obstacles = [Obstacle(player) for _ in range(2)]
    powerups = [PowerUp()]
    decorations = [Decoration() for _ in range(6)]

    coin_count = 0
    distance = 0
    base_speed = 6
    
    active_power = None
    power_start = 0
    power_duration = 4000
    shield = False
    nitro = False

    y1, y2 = 0, -HEIGHT

    while True:
        clock.tick(60)
        current_speed = base_speed + (4 if nitro else 0)
        distance += current_speed // 2
        score = coin_count * 10 + distance // 10

        y1 += current_speed
        y2 += current_speed
        if y1 >= HEIGHT: y1 = -HEIGHT
        if y2 >= HEIGHT: y2 = -HEIGHT
        
        screen.blit(road, (0, y1))
        screen.blit(road, (0, y2))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit", score, distance, coin_count

        for deco in decorations:
            deco.update(current_speed)
            deco.draw(screen)

   
        player.move()
        player.draw(screen)

        for enemy in enemies:
            enemy.update(current_speed)
            enemy.draw(screen)
            if enemy.rect.top > HEIGHT:
                enemy.reset(player)
            if player.rect.colliderect(enemy.rect):
                if shield:
                    shield = False
                    active_power = None
                    enemy.reset(player)
                else:
                    add_score(username, score, distance, coin_count)
                    return "game_over", score, distance, coin_count

        for coin in coins:
            coin.update(current_speed)
            coin.draw(screen)
            if coin.rect.top > HEIGHT:
                coin.reset()
            if player.rect.colliderect(coin.rect):
                coin_count += coin.value
                coin.reset()

        player.speed = 6 
        for obs in obstacles:
            obs.update(current_speed)
            obs.draw(screen)
            if obs.rect.top > HEIGHT:
                obs.reset(player)
            
            if player.rect.colliderect(obs.rect):
                if obs.kind == "oil":
                    player.speed = 3
                else:
                    if shield:
                        shield = False
                        active_power = None
                        obs.reset(player)
                    else:
                        add_score(username, score, distance, coin_count)
                        return "game_over", score, distance, coin_count


        for p in powerups:
            p.update(current_speed)
            p.draw(screen)
            if p.expired() or p.rect.top > HEIGHT:
                p.reset()
            elif player.rect.colliderect(p.rect):
                if active_power is None:
                    active_power = p.kind.capitalize()
                    power_start = pygame.time.get_ticks()
                    if p.kind == "nitro": nitro = True
                    elif p.kind == "shield": shield = True
                    elif p.kind == "repair":
                
                        obstacles[0].reset(player)
                        active_power = None
                p.reset()

        if (nitro or shield) and active_power != "Repair":
            if pygame.time.get_ticks() - power_start > power_duration:
                nitro = False
                shield = False
                active_power = None

        draw_text(screen, f"Score: {score}", 22, WHITE, 10, 10)
        draw_text(screen, f"Coins: {coin_count}", 22, WHITE, 10, 40)
        draw_text(screen, f"Dist: {distance}", 22, WHITE, 10, 70)
        if active_power:
            draw_text(screen, f"Power: {active_power}", 22, YELLOW, 10, 100)

        pygame.display.update()
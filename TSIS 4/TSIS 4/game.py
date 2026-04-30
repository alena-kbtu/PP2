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

class SnakeGame:
    def __init__(self, screen, username):
        self.screen = screen
        self.username = username
        self.settings = self.load_settings()
    
        self.snake_color = tuple(self.settings["snake_color"])
        self.show_grid = self.settings["grid"]
        self.sound_on = self.settings["sound"]
       
        self.eat_sound = self.load_resource_sound("assets/eat.wav")
        self.poison_sound = self.load_resource_sound("assets/poison.mp3")
        self.gameover_sound = self.load_resource_sound("assets/gameover.mp3")
        
        self.clock = pygame.time.Clock()
        self.reset_game()

    def load_settings(self):
        try:
            with open("settings.json", "r") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"snake_color": [0, 200, 0], "grid": True, "sound": True}

    def load_resource_sound(self, path):
        try:
            return pygame.mixer.Sound(path)
        except:
            return None

    def reset_game(self):
        self.snake = [(10, 10), (9, 10), (8, 10)]
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.score = 0
        self.level = 1
        self.foods_eaten = 0
        self.base_speed = 8
        self.speed = self.base_speed
        
        self.food = (15, 10)
        self.food_weight = 1
        self.food_spawn_time = pygame.time.get_ticks()
        
        self.poison = (20, 15)
        self.obstacles = []
        self.powerup = None
        self.active_powerup = None
        self.powerup_end_time = 0
        self.shield = False
        
        self.personal_best = get_personal_best(self.username)

    def get_random_cell(self):
        while True:
            pos = (random.randint(1, COLS - 2), random.randint(3, ROWS - 2))
            if (pos not in self.snake and pos != self.food and 
                pos != self.poison and pos not in self.obstacles):
                if self.powerup is None or pos != self.powerup["pos"]:
                    return pos

    def create_obstacles(self):
        self.obstacles = []
        if self.level < 3: return
        
        count = self.level * 3
        while len(self.obstacles) < count:
            pos = (random.randint(2, COLS - 3), random.randint(4, ROWS - 3))
            head = self.snake[0]
            if abs(pos[0] - head[0]) > 2 or abs(pos[1] - head[1]) > 2:
                if (pos not in self.snake and pos != self.food and 
                    pos != self.poison and pos not in self.obstacles):
                    self.obstacles.append(pos)

    def draw_text(self, text, size, color, x, y):
        font = pygame.font.SysFont("arial", size)
        img = font.render(text, True, color)
        self.screen.blit(img, (x, y))

    def draw_grid(self):
        for x in range(0, WIDTH, CELL):
            pygame.draw.line(self.screen, GRAY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, CELL):
            pygame.draw.line(self.screen, GRAY, (0, y), (WIDTH, y))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and self.direction != (0, 1):
                    self.next_direction = (0, -1)
                elif event.key == pygame.K_DOWN and self.direction != (0, -1):
                    self.next_direction = (0, 1)
                elif event.key == pygame.K_LEFT and self.direction != (1, 0):
                    self.next_direction = (-1, 0)
                elif event.key == pygame.K_RIGHT and self.direction != (-1, 0):
                    self.next_direction = (1, 0)
                elif event.key == pygame.K_ESCAPE:
                    return "menu"
        return None

    def update(self):
        now = pygame.time.get_ticks()
        self.direction = self.next_direction

        if now - self.food_spawn_time > 7000:
            self.food = self.get_random_cell()
            self.food_weight = random.choice([1, 2, 3])
            self.food_spawn_time = now

        if self.powerup is None and random.randint(1, 120) == 1:
            self.powerup = {
                "pos": self.get_random_cell(),
                "type": random.choice(["speed", "slow", "shield"])
            }
            self.powerup_spawn_time = now

        if self.powerup and now - self.powerup_spawn_time > 8000:
            self.powerup = None

        if self.active_powerup and now > self.powerup_end_time:
            self.active_powerup = None
            self.speed = self.base_speed + self.level

     
        head_x, head_y = self.snake[0]
        new_head = (head_x + self.direction[0], head_y + self.direction[1])

     
        if (new_head[0] < 0 or new_head[0] >= COLS or 
            new_head[1] < 2 or new_head[1] >= ROWS or 
            new_head in self.snake or new_head in self.obstacles):
            if self.shield:
                self.shield = False
                new_head = self.snake[0]
            else:
                if self.sound_on and self.gameover_sound: self.gameover_sound.play()
                save_game_result(self.username, self.score, self.level)
                return "game_over"

        self.snake.insert(0, new_head)

   
        if new_head == self.food:
            self.score += self.food_weight
            self.foods_eaten += 1
            if self.sound_on and self.eat_sound: self.eat_sound.play()
            self.food = self.get_random_cell()
            self.food_weight = random.choice([1, 2, 3])
            self.food_spawn_time = now
            
            if self.foods_eaten % 3 == 0:
                self.level += 1
                self.base_speed += 1
                self.speed = self.base_speed
                self.create_obstacles()
 
        elif new_head == self.poison:
            if self.sound_on and self.poison_sound: self.poison_sound.play()
            for _ in range(2): 
                if len(self.snake) > 1: self.snake.pop()
            if len(self.snake) <= 1: return "game_over"
            self.poison = self.get_random_cell()

        elif self.powerup and new_head == self.powerup["pos"]:
            p_type = self.powerup["type"]
            if p_type == "speed":
                self.active_powerup, self.speed = "speed", self.base_speed + self.level + 5
                self.powerup_end_time = now + 5000
            elif p_type == "slow":
                self.active_powerup, self.speed = "slow", max(4, self.base_speed + self.level - 4)
                self.powerup_end_time = now + 5000
            elif p_type == "shield":
                self.shield = True
            self.powerup = None
        else:
            self.snake.pop()
            
        return None

    def draw(self):
        self.screen.fill(BLACK)
        if self.show_grid: self.draw_grid()

  
        pygame.draw.rect(self.screen, (25, 25, 25), (0, 0, WIDTH, CELL * 2))
        self.draw_text(f"Player: {self.username}", 22, WHITE, 10, 8)
        self.draw_text(f"Score: {self.score}", 22, WHITE, 180, 8)
        self.draw_text(f"Level: {self.level}", 22, WHITE, 310, 8)
        self.draw_text(f"Best: {self.personal_best}", 22, WHITE, 430, 8)
        if self.shield: self.draw_text("Shield: ON", 22, BLUE, 550, 8)
        if self.active_powerup: self.draw_text(f"Power: {self.active_powerup}", 22, YELLOW, 650, 8)

        
        for part in self.snake:
            pygame.draw.rect(self.screen, self.snake_color, (part[0]*CELL, part[1]*CELL, CELL, CELL))

      
        f_color = YELLOW if self.food_weight == 1 else ORANGE
        pygame.draw.rect(self.screen, f_color, (self.food[0]*CELL, self.food[1]*CELL, CELL, CELL))
        self.draw_text(str(self.food_weight), 16, BLACK, self.food[0]*CELL + 6, self.food[1]*CELL + 2)

    
        pygame.draw.rect(self.screen, DARK_RED, (self.poison[0]*CELL, self.poison[1]*CELL, CELL, CELL))

       
        if self.powerup:
            colors = {"speed": RED, "slow": BLUE, "shield": PURPLE}
            px, py = self.powerup["pos"]
            pygame.draw.circle(self.screen, colors[self.powerup["type"]], (px*CELL + CELL//2, py*CELL + CELL//2), CELL//2)

   
        for block in self.obstacles:
            pygame.draw.rect(self.screen, GRAY, (block[0]*CELL, block[1]*CELL, CELL, CELL))

        pygame.display.flip()

def run_game(screen, username):
    game = SnakeGame(screen, username)
    while True:
        event_result = game.handle_events()
        if event_result: return event_result, game.score, game.level
        
        update_result = game.update()
        if update_result: return update_result, game.score, game.level
        
        game.draw()
        game.clock.tick(game.speed)
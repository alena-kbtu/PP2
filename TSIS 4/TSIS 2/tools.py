import pygame
from collections import deque
from datetime import datetime


def save_canvas(canvas):
    filename = datetime.now().strftime("paint_%Y%m%d_%H%M%S.png")
    pygame.image.save(canvas, filename)


def flood_fill(surface, start_pos, fill_color):
    width, height = surface.get_size()
    x, y = start_pos

    if x < 0 or x >= width or y < 0 or y >= height:
        return

    target_color = surface.get_at((x, y))
    fill_color = pygame.Color(fill_color)

    if target_color == fill_color:
        return

    queue = deque()
    queue.append((x, y))

    while queue:
        x, y = queue.popleft()

        if x < 0 or x >= width or y < 0 or y >= height:
            continue

        if surface.get_at((x, y)) != target_color:
            continue

        surface.set_at((x, y), fill_color)

        queue.append((x + 1, y))
        queue.append((x - 1, y))
        queue.append((x, y + 1))
        queue.append((x, y - 1))


def draw_square(surface, color, start_pos, end_pos, brush_size):
    x1, y1 = start_pos
    x2, y2 = end_pos

    side = min(abs(x2 - x1), abs(y2 - y1))

    if x2 < x1:
        x1 = x1 - side

    if y2 < y1:
        y1 = y1 - side

    rect = pygame.Rect(x1, y1, side, side)
    pygame.draw.rect(surface, color, rect, brush_size)


def draw_right_triangle(surface, color, start_pos, end_pos, brush_size):
    x1, y1 = start_pos
    x2, y2 = end_pos

    points = [
        (x1, y1),
        (x1, y2),
        (x2, y2)
    ]

    pygame.draw.polygon(surface, color, points, brush_size)


def draw_equilateral_triangle(surface, color, start_pos, end_pos, brush_size):
    x1, y1 = start_pos
    x2, y2 = end_pos

    height = abs(x2 - x1) * 0.866

    points = [
        (x1, y2),
        (x2, y2),
        ((x1 + x2) // 2, y2 - height)
    ]

    pygame.draw.polygon(surface, color, points, brush_size)


def draw_rhombus(surface, color, start_pos, end_pos, brush_size):
    x1, y1 = start_pos
    x2, y2 = end_pos

    center_x = (x1 + x2) // 2
    center_y = (y1 + y2) // 2

    points = [
        (center_x, y1),
        (x2, center_y),
        (center_x, y2),
        (x1, center_y)
    ]

    pygame.draw.polygon(surface, color, points, brush_size)
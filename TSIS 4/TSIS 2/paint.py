import pygame
import sys

from tools import (
    save_canvas,
    flood_fill,
    draw_square,
    draw_right_triangle,
    draw_equilateral_triangle,
    draw_rhombus
)


pygame.init()

WIDTH = 1000
HEIGHT = 650

TOOLBAR_WIDTH = 90

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TSIS2 Paint Application")

clock = pygame.time.Clock()


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (210, 210, 210)
DARK_GRAY = (70, 70, 70)

RED = (255, 0, 0)
GREEN = (0, 200, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (160, 32, 240)

current_color = WHITE


canvas = pygame.Surface((WIDTH, HEIGHT))
canvas.fill(BLACK)

font = pygame.font.SysFont("Arial", 26)
small_font = pygame.font.SysFont("Arial", 18)

ICON_SIZE = 45


def load_icon(path):
    icon = pygame.image.load(path)
    icon = pygame.transform.scale(icon, (ICON_SIZE, ICON_SIZE))
    return icon


pencil_icon = load_icon("assets/pencil.png")
line_icon = load_icon("assets/linetool.png")
rect_icon = load_icon("assets/rectangle.png")
circle_icon = load_icon("assets/circle.png")
eraser_icon = load_icon("assets/eraser.png")
fill_icon = load_icon("assets/bucket.png")
text_icon = load_icon("assets/text.png")


tool = "pencil"
brush_size = 5

drawing = False
start_pos = None
last_pos = None

text_active = False
text_pos = None
text_value = ""


toolbar = [
    ("pencil", pencil_icon, (20, 90)),
    ("line", line_icon, (20, 145)),
    ("rectangle", rect_icon, (20, 200)),
    ("circle", circle_icon, (20, 255)),
    ("eraser", eraser_icon, (20, 310)),
    ("fill", fill_icon, (20, 365)),
    ("text", text_icon, (20, 420)),
]


color_buttons = [
    (WHITE, (15, 500)),
    (RED, (45, 500)),
    (GREEN, (15, 535)),
    (BLUE, (45, 535)),
    (YELLOW, (15, 570)),
    (PURPLE, (45, 570)),
]


def is_on_toolbar(pos):
    return pos[0] < TOOLBAR_WIDTH


def draw_toolbar():
    pygame.draw.rect(screen, GRAY, (0, 0, TOOLBAR_WIDTH, HEIGHT))

    title = small_font.render("TOOLS", True, BLACK)
    screen.blit(title, (15, 15))

    for name, icon, pos in toolbar:
        button_rect = pygame.Rect(pos[0] - 5, pos[1] - 5, ICON_SIZE + 10, ICON_SIZE + 10)

        if tool == name:
            pygame.draw.rect(screen, YELLOW, button_rect)
        else:
            pygame.draw.rect(screen, WHITE, button_rect)

        pygame.draw.rect(screen, BLACK, button_rect, 2)
        screen.blit(icon, pos)

    color_text = small_font.render("COLOR", True, BLACK)
    screen.blit(color_text, (15, 470))

    for color, pos in color_buttons:
        rect = pygame.Rect(pos[0], pos[1], 25, 25)
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, BLACK, rect, 2)

        if color == current_color:
            pygame.draw.rect(screen, ORANGE, rect, 4)

    size_text = small_font.render(f"Size: {brush_size}", True, BLACK)
    screen.blit(size_text, (10, 615))


def handle_toolbar_click(pos):
    global tool, current_color

    for name, icon, icon_pos in toolbar:
        button_rect = pygame.Rect(icon_pos[0] - 5, icon_pos[1] - 5, ICON_SIZE + 10, ICON_SIZE + 10)

        if button_rect.collidepoint(pos):
            tool = name
            print("Selected tool:", tool)
            return True

    for color, color_pos in color_buttons:
        rect = pygame.Rect(color_pos[0], color_pos[1], 25, 25)

        if rect.collidepoint(pos):
            current_color = color
            print("Selected color:", current_color)
            return True

    return False


def draw_info():
    text1 = f"Tool: {tool} | Brush size: {brush_size}"
    info = small_font.render(text1, True, YELLOW)
    screen.blit(info, (110, 10))

    text2 = "Keys: P Pencil | L Line | R Rect | C Circle | E Eraser | F Fill | T Text | 1/2/3 Size | Ctrl+S Save"
    info2 = small_font.render(text2, True, YELLOW)
    screen.blit(info2, (110, 35))

    text3 = "Extra shapes: S Square | H Right Triangle | G Equilateral Triangle | D Rhombus"
    info3 = small_font.render(text3, True, YELLOW)
    screen.blit(info3, (110, 60))


def draw_preview(mouse_pos):
    if not drawing or start_pos is None:
        return

    if tool == "line":
        pygame.draw.line(screen, current_color, start_pos, mouse_pos, brush_size)

    elif tool == "rectangle":
        rect = pygame.Rect(
            min(start_pos[0], mouse_pos[0]),
            min(start_pos[1], mouse_pos[1]),
            abs(mouse_pos[0] - start_pos[0]),
            abs(mouse_pos[1] - start_pos[1])
        )
        pygame.draw.rect(screen, current_color, rect, brush_size)

    elif tool == "circle":
        radius = int(
            ((mouse_pos[0] - start_pos[0]) ** 2 + (mouse_pos[1] - start_pos[1]) ** 2) ** 0.5
        )
        pygame.draw.circle(screen, current_color, start_pos, radius, brush_size)

    elif tool == "square":
        draw_square(screen, current_color, start_pos, mouse_pos, brush_size)

    elif tool == "right_triangle":
        draw_right_triangle(screen, current_color, start_pos, mouse_pos, brush_size)

    elif tool == "equilateral_triangle":
        draw_equilateral_triangle(screen, current_color, start_pos, mouse_pos, brush_size)

    elif tool == "rhombus":
        draw_rhombus(screen, current_color, start_pos, mouse_pos, brush_size)


def draw_final_shape(end_pos):
    global drawing, start_pos, last_pos

    if tool == "line":
        pygame.draw.line(canvas, current_color, start_pos, end_pos, brush_size)

    elif tool == "rectangle":
        rect = pygame.Rect(
            min(start_pos[0], end_pos[0]),
            min(start_pos[1], end_pos[1]),
            abs(end_pos[0] - start_pos[0]),
            abs(end_pos[1] - start_pos[1])
        )
        pygame.draw.rect(canvas, current_color, rect, brush_size)

    elif tool == "circle":
        radius = int(
            ((end_pos[0] - start_pos[0]) ** 2 + (end_pos[1] - start_pos[1]) ** 2) ** 0.5
        )
        pygame.draw.circle(canvas, current_color, start_pos, radius, brush_size)

    elif tool == "square":
        draw_square(canvas, current_color, start_pos, end_pos, brush_size)

    elif tool == "right_triangle":
        draw_right_triangle(canvas, current_color, start_pos, end_pos, brush_size)

    elif tool == "equilateral_triangle":
        draw_equilateral_triangle(canvas, current_color, start_pos, end_pos, brush_size)

    elif tool == "rhombus":
        draw_rhombus(canvas, current_color, start_pos, end_pos, brush_size)

    drawing = False
    start_pos = None
    last_pos = None


running = True

while running:
    screen.blit(canvas, (0, 0))

    mouse_pos = pygame.mouse.get_pos()

    draw_preview(mouse_pos)

    if text_active and text_pos is not None:
        text_surface = font.render(text_value + "|", True, current_color)
        screen.blit(text_surface, text_pos)

    draw_toolbar()
    draw_info()

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False


        if event.type == pygame.KEYDOWN:
            keys = pygame.key.get_pressed()

            if (keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]) and event.key == pygame.K_s:
                save_canvas(canvas)

            elif text_active:
                if event.key == pygame.K_RETURN:
                    text_surface = font.render(text_value, True, current_color)
                    canvas.blit(text_surface, text_pos)

                    text_active = False
                    text_value = ""
                    text_pos = None

                elif event.key == pygame.K_ESCAPE:
                    text_active = False
                    text_value = ""
                    text_pos = None

                elif event.key == pygame.K_BACKSPACE:
                    text_value = text_value[:-1]

                else:
                    text_value += event.unicode

            else:
                if event.key == pygame.K_p:
                    tool = "pencil"

                elif event.key == pygame.K_l:
                    tool = "line"

                elif event.key == pygame.K_r:
                    tool = "rectangle"

                elif event.key == pygame.K_c:
                    tool = "circle"

                elif event.key == pygame.K_s:
                    tool = "square"

                elif event.key == pygame.K_h:
                    tool = "right_triangle"

                elif event.key == pygame.K_g:
                    tool = "equilateral_triangle"

                elif event.key == pygame.K_d:
                    tool = "rhombus"

                elif event.key == pygame.K_e:
                    tool = "eraser"

                elif event.key == pygame.K_f:
                    tool = "fill"

                elif event.key == pygame.K_t:
                    tool = "text"

                elif event.key == pygame.K_1:
                    brush_size = 2

                elif event.key == pygame.K_2:
                    brush_size = 5

                elif event.key == pygame.K_3:
                    brush_size = 10

                elif event.key == pygame.K_w:
                    current_color = WHITE

                elif event.key == pygame.K_v:
                    current_color = RED

                elif event.key == pygame.K_n:
                    current_color = GREEN

                elif event.key == pygame.K_b:
                    current_color = BLUE

                elif event.key == pygame.K_y:
                    current_color = YELLOW

                elif event.key == pygame.K_m:
                    current_color = PURPLE

                elif event.key == pygame.K_o:
                    current_color = ORANGE

                elif event.key == pygame.K_ESCAPE:
                    running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pos = event.pos

                if handle_toolbar_click(mouse_pos):
                    drawing = False
                    start_pos = None
                    last_pos = None

                elif not is_on_toolbar(mouse_pos):
                    start_pos = mouse_pos
                    last_pos = mouse_pos

                    if tool == "fill":
                        flood_fill(canvas, mouse_pos, current_color)

                    elif tool == "text":
                        text_active = True
                        text_pos = mouse_pos
                        text_value = ""

                    else:
                        drawing = True

        if event.type == pygame.MOUSEMOTION:
            if drawing and not is_on_toolbar(event.pos):

                if tool == "pencil":
                    pygame.draw.line(canvas, current_color, last_pos, event.pos, brush_size)
                    last_pos = event.pos

                elif tool == "eraser":
                    pygame.draw.line(canvas, BLACK, last_pos, event.pos, brush_size)
                    last_pos = event.pos

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and drawing:
                end_pos = event.pos

                if not is_on_toolbar(end_pos):
                    draw_final_shape(end_pos)

                drawing = False
                start_pos = None
                last_pos = None

    pygame.display.flip()
    clock.tick(60)


pygame.quit()
sys.exit()

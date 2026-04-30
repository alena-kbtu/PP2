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

class PaintApp:
    def __init__(self):
      
        pygame.init()

     
        self.WIDTH = 1000
        self.HEIGHT = 650
        self.TOOLBAR_WIDTH = 90

        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("TSIS2 Paint Application")
        self.clock = pygame.time.Clock()

    
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GRAY = (210, 210, 210)
        self.DARK_GRAY = (70, 70, 70)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 200, 0)
        self.BLUE = (0, 0, 255)
        self.YELLOW = (255, 255, 0)
        self.ORANGE = (255, 165, 0)
        self.PURPLE = (160, 32, 240)

        self.current_color = self.BLACK

       
        self.canvas = pygame.Surface((self.WIDTH, self.HEIGHT))
        self.canvas.fill(self.WHITE)

        self.font = pygame.font.SysFont("Arial", 26)
        self.small_font = pygame.font.SysFont("Arial", 18)

     
        self.ICON_SIZE = 45
        self.pencil_icon = self.load_icon("assets/pencil.png")
        self.line_icon = self.load_icon("assets/linetool.png")
        self.rect_icon = self.load_icon("assets/rectangle.png")
        self.circle_icon = self.load_icon("assets/circle.png")
        self.eraser_icon = self.load_icon("assets/eraser.png")
        self.fill_icon = self.load_icon("assets/bucket.png")
        self.text_icon = self.load_icon("assets/text.png")

     
        self.tool = "pencil"
        self.brush_size = 13
        self.drawing = False
        self.start_pos = None
        self.last_pos = None

       
        self.text_active = False
        self.text_pos = None
        self.text_value = ""

      
        self.toolbar = [
            ("pencil", self.pencil_icon, (20, 90)),
            ("line", self.line_icon, (20, 145)),
            ("rectangle", self.rect_icon, (20, 200)),
            ("circle", self.circle_icon, (20, 255)),
            ("eraser", self.eraser_icon, (20, 310)),
            ("fill", self.fill_icon, (20, 365)),
            ("text", self.text_icon, (20, 420)),
        ]

        self.color_buttons = [
            (self.WHITE, (15, 500)),
            (self.RED, (45, 500)),
            (self.GREEN, (15, 535)),
            (self.BLUE, (45, 535)),
            (self.YELLOW, (15, 570)),
            (self.PURPLE, (45, 570)),
        ]

    def load_icon(self, path):
        try:
            icon = pygame.image.load(path)
            icon = pygame.transform.scale(icon, (self.ICON_SIZE, self.ICON_SIZE))
            return icon
        except:
            surf = pygame.Surface((self.ICON_SIZE, self.ICON_SIZE))
            surf.fill(self.GRAY)
            return surf

    def is_on_toolbar(self, pos):
        return pos[0] < self.TOOLBAR_WIDTH

    def draw_toolbar(self):
        pygame.draw.rect(self.screen, self.GRAY, (0, 0, self.TOOLBAR_WIDTH, self.HEIGHT))
        title = self.small_font.render("TOOLS", True, self.BLACK)
        self.screen.blit(title, (15, 15))

        for name, icon, pos in self.toolbar:
            button_rect = pygame.Rect(pos[0] - 5, pos[1] - 5, self.ICON_SIZE + 10, self.ICON_SIZE + 10)
            if self.tool == name:
                pygame.draw.rect(self.screen, self.YELLOW, button_rect)
            else:
                pygame.draw.rect(self.screen, self.WHITE, button_rect)
            
            pygame.draw.rect(self.screen, self.BLACK, button_rect, 2)
            self.screen.blit(icon, pos)

        color_text = self.small_font.render("COLOR", True, self.BLACK)
        self.screen.blit(color_text, (15, 470))

        for color, pos in self.color_buttons:
            rect = pygame.Rect(pos[0], pos[1], 25, 25)
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, self.BLACK, rect, 2)
            if color == self.current_color:
                pygame.draw.rect(self.screen, self.ORANGE, rect, 4)

        size_text = self.small_font.render(f"Size: {self.brush_size}", True, self.BLACK)
        self.screen.blit(size_text, (10, 615))

    def handle_toolbar_click(self, pos):
        for name, icon, icon_pos in self.toolbar:
            button_rect = pygame.Rect(icon_pos[0] - 5, icon_pos[1] - 5, self.ICON_SIZE + 10, self.ICON_SIZE + 10)
            if button_rect.collidepoint(pos):
                self.tool = name
                return True

        for color, color_pos in self.color_buttons:
            rect = pygame.Rect(color_pos[0], color_pos[1], 25, 25)
            if rect.collidepoint(pos):
                self.current_color = color
                return True
        return False

    def draw_info(self):
        text1 = f"Tool: {self.tool} | Brush size: {self.brush_size}"
        info = self.small_font.render(text1, True, self.YELLOW)
        self.screen.blit(info, (110, 10))

        text2 = "Keys: P Pencil | L Line | R Rect | C Circle | E Eraser | F Fill | T Text | 1/2/3 Size | Ctrl+S Save"
        info2 = self.small_font.render(text2, True, self.YELLOW)
        self.screen.blit(info2, (110, 35))

        text3 = "Extra shapes: S Square | H Right Triangle | G Equilateral Triangle | D Rhombus"
        info3 = self.small_font.render(text3, True, self.YELLOW)
        self.screen.blit(info3, (110, 60))

    def draw_preview(self, mouse_pos):
        if not self.drawing or self.start_pos is None:
            return

        if self.tool == "line":
            pygame.draw.line(self.screen, self.current_color, self.start_pos, mouse_pos, self.brush_size)
        elif self.tool == "rectangle":
            rect = pygame.Rect(min(self.start_pos[0], mouse_pos[0]), min(self.start_pos[1], mouse_pos[1]),
                               abs(mouse_pos[0] - self.start_pos[0]), abs(mouse_pos[1] - self.start_pos[1]))
            pygame.draw.rect(self.screen, self.current_color, rect, self.brush_size)
        elif self.tool == "circle":
            radius = int(((mouse_pos[0] - self.start_pos[0]) ** 2 + (mouse_pos[1] - self.start_pos[1]) ** 2) ** 0.5)
            pygame.draw.circle(self.screen, self.current_color, self.start_pos, radius, self.brush_size)
        elif self.tool == "square":
            draw_square(self.screen, self.current_color, self.start_pos, mouse_pos, self.brush_size)
        elif self.tool == "right_triangle":
            draw_right_triangle(self.screen, self.current_color, self.start_pos, mouse_pos, self.brush_size)
        elif self.tool == "equilateral_triangle":
            draw_equilateral_triangle(self.screen, self.current_color, self.start_pos, mouse_pos, self.brush_size)
        elif self.tool == "rhombus":
            draw_rhombus(self.screen, self.current_color, self.start_pos, mouse_pos, self.brush_size)

    def draw_final_shape(self, end_pos):
        if self.tool == "line":
            pygame.draw.line(self.canvas, self.current_color, self.start_pos, end_pos, self.brush_size)
        elif self.tool == "rectangle":
            rect = pygame.Rect(min(self.start_pos[0], end_pos[0]), min(self.start_pos[1], end_pos[1]),
                               abs(end_pos[0] - self.start_pos[0]), abs(end_pos[1] - self.start_pos[1]))
            pygame.draw.rect(self.canvas, self.current_color, rect, self.brush_size)
        elif self.tool == "circle":
            radius = int(((end_pos[0] - self.start_pos[0]) ** 2 + (end_pos[1] - self.start_pos[1]) ** 2) ** 0.5)
            pygame.draw.circle(self.canvas, self.current_color, self.start_pos, radius, self.brush_size)
        elif self.tool == "square":
            draw_square(self.canvas, self.current_color, self.start_pos, end_pos, self.brush_size)
        elif self.tool == "right_triangle":
            draw_right_triangle(self.canvas, self.current_color, self.start_pos, end_pos, self.brush_size)
        elif self.tool == "equilateral_triangle":
            draw_equilateral_triangle(self.canvas, self.current_color, self.start_pos, end_pos, self.brush_size)
        elif self.tool == "rhombus":
            draw_rhombus(self.canvas, self.current_color, self.start_pos, end_pos, self.brush_size)

    def run(self):
        running = True
        while running:
         
            self.screen.blit(self.canvas, (0, 0))
            mouse_pos = pygame.mouse.get_pos()
            self.draw_preview(mouse_pos)

          
            if self.text_active and self.text_pos is not None:
                text_surface = self.font.render(self.text_value + "|", True, self.current_color)
                self.screen.blit(text_surface, self.text_pos)

 
            self.draw_toolbar()
            self.draw_info()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    keys = pygame.key.get_pressed()
                    if (keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]) and event.key == pygame.K_s:
                        save_canvas(self.canvas)
                    
                    elif self.text_active:
                        if event.key == pygame.K_RETURN:
                            text_surface = self.font.render(self.text_value, True, self.current_color)
                            self.canvas.blit(text_surface, self.text_pos)
                            self.text_active, self.text_value, self.text_pos = False, "", None
                        elif event.key == pygame.K_ESCAPE:
                            self.text_active, self.text_value, self.text_pos = False, "", None
                        elif event.key == pygame.K_BACKSPACE:
                            self.text_value = self.text_value[:-1]
                        else:
                            self.text_value += event.unicode
                    
                    else:
                      
                        if event.key == pygame.K_p: self.tool = "pencil"
                        elif event.key == pygame.K_l: self.tool = "line"
                        elif event.key == pygame.K_r: self.tool = "rectangle"
                        elif event.key == pygame.K_c: self.tool = "circle"
                        elif event.key == pygame.K_s: self.tool = "square"
                        elif event.key == pygame.K_h: self.tool = "right_triangle"
                        elif event.key == pygame.K_g: self.tool = "equilateral_triangle"
                        elif event.key == pygame.K_d: self.tool = "rhombus"
                        elif event.key == pygame.K_e: self.tool = "eraser"
                        elif event.key == pygame.K_f: self.tool = "fill"
                        elif event.key == pygame.K_t: self.tool = "text"
                        elif event.key == pygame.K_1: self.brush_size = 2
                        elif event.key == pygame.K_2: self.brush_size = 5
                        elif event.key == pygame.K_3: self.brush_size = 10
                        elif event.key == pygame.K_ESCAPE: running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if self.handle_toolbar_click(event.pos):
                            self.drawing = False
                        elif not self.is_on_toolbar(event.pos):
                            self.start_pos = event.pos
                            self.last_pos = event.pos
                            if self.tool == "fill":
                                flood_fill(self.canvas, event.pos, self.current_color)
                            elif self.tool == "text":
                                self.text_active = True
                                self.text_pos = event.pos
                                self.text_value = ""
                            else:
                                self.drawing = True

                if event.type == pygame.MOUSEMOTION:
                    if self.drawing and not self.is_on_toolbar(event.pos):
                        if self.tool == "pencil":
                            pygame.draw.line(self.canvas, self.current_color, self.last_pos, event.pos, self.brush_size)
                            self.last_pos = event.pos
                        elif self.tool == "eraser":
                            pygame.draw.line(self.canvas, self.WHITE, self.last_pos, event.pos, self.brush_size)
                            self.last_pos = event.pos

                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1 and self.drawing:
                        if not self.is_on_toolbar(event.pos):
                            self.draw_final_shape(event.pos)
                        self.drawing = False
                        self.start_pos = None
                        self.last_pos = None

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = PaintApp()
    app.run()
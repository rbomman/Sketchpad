import os
import pygame
import colorsys
import math

# Configuration
pygame.init()

# Window dimensions
CANVAS_WIDTH, CANVAS_HEIGHT = 1180, 720
PANEL_WIDTH = 100
WINDOW_WIDTH = CANVAS_WIDTH + PANEL_WIDTH
WINDOW_HEIGHT = CANVAS_HEIGHT

# UI constants
SIDEBAR_MARGIN = 10
BUTTON_SIZE = 40
BUTTON_SPACING_X = 10
BUTTON_SPACING_Y = 10

# Colors
BACKGROUND_COLOR = (245, 245, 245)
SIDEBAR_COLOR = (50, 50, 50)

# Predefined palette for swatches
PALETTE = {
    'Black':  (33, 33, 33),
    'Gray':   (128, 128, 128),
    'White':  (245, 245, 245),
    'Red':    (231, 76, 60),
    'Orange': (243, 156, 18),
    'Yellow': (241, 196, 15),
    'Green':  (46, 204, 113),
    'Blue':   (52, 152, 219),
    'Purple': (155, 89, 182),
    'Brown':  (149, 88, 72),
}

# Brush sizes
BRUSH_SIZES = {'XS': 1, 'S': 3, 'M': 5, 'L': 7, 'XL': 9}

# Setup window and canvas
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Sketchpad")
canvas = pygame.Surface((CANVAS_WIDTH, CANVAS_HEIGHT))
canvas.fill(BACKGROUND_COLOR)
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 16)

# Drawing state (HLS colors)
h, l, s = 0.0, 0.5, 1.0
draw_color = tuple(int(c*255) for c in colorsys.hls_to_rgb(h, l, s))
brush_size = BRUSH_SIZES['M']
last_pos = None
hsl_mode = False

class Button:
    def __init__(self, color, rect, callback, label=""):
        self.base_color = color
        self.rect = pygame.Rect(rect)
        self.callback = callback
        self.label = label
        self.surface = pygame.Surface(self.rect.size)
        self.text_surf = font.render(label, True, (255,255,255) if sum(color)<400 else (20,20,20))
        self.hovered = False

    def draw(self, surf):
        col = tuple(min(c+20,255) if self.hovered else c for c in self.base_color)
        self.surface.fill(col)
        if self.label:
            tw, th = self.text_surf.get_size()
            self.surface.blit(self.text_surf, ((self.rect.width-tw)//2, (self.rect.height-th)//2))
        surf.blit(self.surface, self.rect.topleft)

    def process(self, events):
        mouse_pos = pygame.mouse.get_pos()
        self.hovered = self.rect.collidepoint(mouse_pos)
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and self.hovered:
                self.callback()

# Button functions
def set_color(color):
    global h, l, s, draw_color, hsl_mode
    rf, gf, bf = [c/255 for c in color]
    h2, l2, s2 = colorsys.rgb_to_hls(rf, gf, bf)
    h, l, s = h2, l2, s2
    draw_color = color
    hsl_mode = False

def set_size(size_label):
    global brush_size
    brush_size = BRUSH_SIZES[size_label]

def clear_canvas():
    canvas.fill(BACKGROUND_COLOR)

def save_canvas():
    folder = os.path.join(os.path.expanduser('~'), 'Desktop', 'screenshots')
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, 'sketch.png')
    pygame.image.save(canvas, path)
    print(f"Saved to {path}")

def toggle_hsl():
    global hsl_mode
    hsl_mode = not hsl_mode

# Build buttons
buttons = []
# Palette swatches (2 columns)
total = len(PALETTE)
cols = 2
rows = math.ceil(total/cols)
for idx, (_name, col) in enumerate(PALETTE.items()):
    cx = idx // rows
    cy = idx % rows
    x = CANVAS_WIDTH + SIDEBAR_MARGIN + cx*(BUTTON_SIZE + BUTTON_SPACING_X)
    y = SIDEBAR_MARGIN + cy*(BUTTON_SIZE + BUTTON_SPACING_Y)
    buttons.append(Button(col, (x, y, BUTTON_SIZE, BUTTON_SIZE), lambda c=col: set_color(c)))

# Brush size buttons below palette
d_start = SIDEBAR_MARGIN + rows*(BUTTON_SIZE + BUTTON_SPACING_Y) + BUTTON_SPACING_Y*2
for i, size_label in enumerate(BRUSH_SIZES):
    x = CANVAS_WIDTH + SIDEBAR_MARGIN + (i%3)*(BUTTON_SIZE + BUTTON_SPACING_X)
    y = d_start + (i//3)*(BUTTON_SIZE + BUTTON_SPACING_Y)
    buttons.append(Button((200,200,200), (x, y, BUTTON_SIZE, BUTTON_SIZE), lambda sl=size_label: set_size(sl), label=size_label))

# HSL toggle button further down to free space
hsl_x = CANVAS_WIDTH + SIDEBAR_MARGIN
hsl_y = d_start + math.ceil(len(BRUSH_SIZES)/3)*(BUTTON_SIZE + BUTTON_SPACING_Y) + BUTTON_SPACING_Y*4
buttons.append(Button((200,100,200), (hsl_x, hsl_y, BUTTON_SIZE, BUTTON_SIZE), toggle_hsl, label="HSL"))

# Clear and Save buttons at bottom
sv_width = BUTTON_SIZE*2 + BUTTON_SPACING_X
save_x = CANVAS_WIDTH + (PANEL_WIDTH - sv_width)//2
save_y = WINDOW_HEIGHT - BUTTON_SIZE - SIDEBAR_MARGIN
clear_y = save_y - BUTTON_SIZE - BUTTON_SPACING_Y
buttons.append(Button((180,50,50), (save_x, clear_y, sv_width, BUTTON_SIZE), clear_canvas, label="Clear"))
buttons.append(Button((50,180,50), (save_x, save_y, sv_width, BUTTON_SIZE), save_canvas, label="Save"))

# Slider positions moved down by 200px
overlay_offset = 200
SLIDER_X = CANVAS_WIDTH + SIDEBAR_MARGIN
SLIDER_W = PANEL_WIDTH - 2*SIDEBAR_MARGIN
SLIDER_H = 20
SLIDER_Y0 = CANVAS_HEIGHT//2 - 50 + overlay_offset
SLIDER_Y1 = SLIDER_Y0 + SLIDER_H + BUTTON_SPACING_Y
SLIDER_Y2 = SLIDER_Y1 + SLIDER_H + BUTTON_SPACING_Y

# HSL slider drawing
def draw_hsl_sliders(surf):
    for i in range(SLIDER_W):
        col = colorsys.hls_to_rgb(i/SLIDER_W, l, s)
        surf.fill(tuple(int(c*255) for c in col), (SLIDER_X+i, SLIDER_Y0, 1, SLIDER_H))
        col = colorsys.hls_to_rgb(h, i/SLIDER_W, s)
        surf.fill(tuple(int(c*255) for c in col), (SLIDER_X+i, SLIDER_Y1, 1, SLIDER_H))
        col = colorsys.hls_to_rgb(h, l, i/SLIDER_W)
        surf.fill(tuple(int(c*255) for c in col), (SLIDER_X+i, SLIDER_Y2, 1, SLIDER_H))
    # Markers
    pygame.draw.rect(surf, (255,255,255), (SLIDER_X+int(h*SLIDER_W)-2, SLIDER_Y0-2, 4, SLIDER_H+4), 1)
    pygame.draw.rect(surf, (255,255,255), (SLIDER_X+int(l*SLIDER_W)-2, SLIDER_Y1-2, 4, SLIDER_H+4), 1)
    pygame.draw.rect(surf, (255,255,255), (SLIDER_X+int(s*SLIDER_W)-2, SLIDER_Y2-2, 4, SLIDER_H+4), 1)

# Main loop
running = True
while running:
    events = pygame.event.get()
    for e in events:
        if e.type == pygame.QUIT:
            running = False
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            mx, my = e.pos
            if mx <= CANVAS_WIDTH and not hsl_mode:
                pygame.draw.circle(canvas, draw_color, e.pos, brush_size)
                last_pos = e.pos
            elif hsl_mode and SLIDER_X <= mx <= SLIDER_X+SLIDER_W:
                relx = mx - SLIDER_X
                if SLIDER_Y0 <= my <= SLIDER_Y0+SLIDER_H:
                    h = relx/SLIDER_W
                elif SLIDER_Y1 <= my <= SLIDER_Y1+SLIDER_H:
                    l = relx/SLIDER_W
                elif SLIDER_Y2 <= my <= SLIDER_Y2+SLIDER_H:
                    s = relx/SLIDER_W
                draw_color = tuple(int(c*255) for c in colorsys.hls_to_rgb(h, l, s))
                hsl_mode = False
        elif e.type == pygame.MOUSEMOTION and pygame.mouse.get_pressed()[0] and not hsl_mode and last_pos:
            if e.pos[0] <= CANVAS_WIDTH:
                x1, y1 = last_pos
                x2, y2 = e.pos
                dx, dy = x2 - x1, y2 - y1
                dist = math.hypot(dx, dy)
                steps = int(dist / max(1, brush_size/2)) + 1
                for i in range(steps):
                    xi = x1 + dx * i / steps
                    yi = y1 + dy * i / steps
                    pygame.draw.circle(canvas, draw_color, (int(xi), int(yi)), brush_size)
                last_pos = e.pos
        elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
            last_pos = None

    window.fill(SIDEBAR_COLOR)
    window.blit(canvas, (0, 0))
    if hsl_mode:
        draw_hsl_sliders(window)
    for btn in buttons:
        btn.process(events)
        btn.draw(window)
    pygame.display.flip()
    clock.tick(120)

pygame.quit()

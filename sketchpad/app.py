from __future__ import annotations

import colorsys
import ctypes
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable

import pygame


WINDOW_SIZE = (1360, 900)
CANVAS_SIZE = (1024, 720)
SIDEBAR_WIDTH = 300
PADDING = 18
BUTTON_HEIGHT = 42
SWATCH_SIZE = 38
SLIDER_HEIGHT = 18
SLIDER_GAP = 44
HISTORY_LIMIT = 25
FPS = 120
MIN_BRUSH_SIZE = 1
MAX_BRUSH_SIZE = 32

BACKGROUND = (242, 237, 230)
APP_BACKGROUND = (225, 216, 205)
SIDEBAR_BACKGROUND = (35, 41, 48)
SIDEBAR_SECTION = (52, 61, 70)
SIDEBAR_BORDER = (81, 93, 104)
TEXT_PRIMARY = (241, 242, 244)
TEXT_MUTED = (177, 187, 196)
CANVAS_BORDER = (84, 75, 66)
CANVAS_DROP = (185, 174, 160)
BUTTON_NEUTRAL = (73, 84, 95)
BUTTON_HOVER = (92, 105, 117)
BUTTON_ACTIVE = (199, 121, 55)
BUTTON_DANGER = (163, 65, 51)
BUTTON_SUCCESS = (56, 144, 94)
BUTTON_ERASER = (114, 84, 135)
STATUS_OK = (70, 133, 90)

PALETTE = [
    ("Ink", (34, 34, 34)),
    ("Slate", (91, 103, 112)),
    ("Snow", (248, 244, 239)),
    ("Cherry", (205, 74, 74)),
    ("Orange", (224, 138, 61)),
    ("Sun", (229, 192, 79)),
    ("Moss", (85, 148, 96)),
    ("Ocean", (66, 125, 184)),
    ("Berry", (131, 92, 177)),
    ("Cocoa", (129, 94, 74)),
]

@dataclass
class Button:
    rect: pygame.Rect
    label: str
    callback: Callable[[], None]
    base_color: tuple[int, int, int]
    hover_color: tuple[int, int, int]
    active_color: tuple[int, int, int]
    selected: bool = False

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        mouse_pos = pygame.mouse.get_pos()
        hovered = self.rect.collidepoint(mouse_pos)
        color = self.active_color if self.selected else self.hover_color if hovered else self.base_color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, SIDEBAR_BORDER, self.rect, width=1, border_radius=10)
        label_surface = font.render(self.label, True, TEXT_PRIMARY)
        surface.blit(label_surface, label_surface.get_rect(center=self.rect.center))

    def handle_click(self, pos: tuple[int, int]) -> bool:
        if self.rect.collidepoint(pos):
            self.callback()
            return True
        return False


class SketchpadApp:
    def __init__(self) -> None:
        self.enable_high_dpi()
        pygame.init()
        pygame.display.set_caption("Sketchpad Studio")
        self.window = pygame.display.set_mode(WINDOW_SIZE)
        self.clock = pygame.time.Clock()
        self.title_font = pygame.font.SysFont("Segoe UI Semibold", 28)
        self.body_font = pygame.font.SysFont("Segoe UI", 18)
        self.small_font = pygame.font.SysFont("Segoe UI", 15)
        self.status_font = pygame.font.SysFont("Consolas", 15)

        self.canvas_rect = pygame.Rect(PADDING, PADDING + 56, *CANVAS_SIZE)
        sidebar_x = self.canvas_rect.right + PADDING
        self.sidebar_rect = pygame.Rect(
            sidebar_x,
            PADDING,
            SIDEBAR_WIDTH,
            WINDOW_SIZE[1] - (PADDING * 2),
        )
        self.status_rect = pygame.Rect(
            self.canvas_rect.left,
            self.canvas_rect.bottom + 16,
            self.canvas_rect.width,
            44,
        )
        self.canvas = pygame.Surface(self.canvas_rect.size)
        self.canvas.fill(BACKGROUND)
        self.history: list[pygame.Surface] = []
        self.running = True

        self.current_color = PALETTE[0][1]
        self.brush_size = 7
        self.tool = "brush"
        self.hue, self.lightness, self.saturation = self.rgb_to_hls(self.current_color)
        self.active_slider: str | None = None
        self.active_hex_input = False
        self.is_drawing = False
        self.last_canvas_pos: tuple[int, int] | None = None
        self.status_message = "Ready"
        self.status_color = TEXT_MUTED
        self.hex_input = self.rgb_hex(self.current_color)

        self.preview_rect = pygame.Rect(self.sidebar_rect.left + PADDING, self.sidebar_rect.top + 470, 54, 54)
        self.hex_input_rect = pygame.Rect(self.preview_rect.right + 12, self.preview_rect.top + 12, 172, 30)
        self.brush_slider_rect = pygame.Rect(self.sidebar_rect.left + PADDING, self.sidebar_rect.top + 338, self.sidebar_rect.width - (PADDING * 2), SLIDER_HEIGHT)
        self.slider_rects = self._build_slider_rects()
        self.buttons = self._build_buttons()

    def _build_slider_rects(self) -> dict[str, pygame.Rect]:
        start_y = self.preview_rect.bottom + 38
        return {
            "hue": pygame.Rect(self.sidebar_rect.left + PADDING, start_y, self.sidebar_rect.width - (PADDING * 2), SLIDER_HEIGHT),
            "lightness": pygame.Rect(self.sidebar_rect.left + PADDING, start_y + SLIDER_GAP, self.sidebar_rect.width - (PADDING * 2), SLIDER_HEIGHT),
            "saturation": pygame.Rect(self.sidebar_rect.left + PADDING, start_y + (SLIDER_GAP * 2), self.sidebar_rect.width - (PADDING * 2), SLIDER_HEIGHT),
        }

    def _build_buttons(self) -> list[Button]:
        buttons: list[Button] = []

        tool_y = self.sidebar_rect.top + 250
        buttons.append(
            Button(
                rect=pygame.Rect(self.sidebar_rect.left + PADDING, tool_y, 122, BUTTON_HEIGHT),
                label="Brush (B)",
                callback=lambda: self.set_tool("brush"),
                base_color=BUTTON_NEUTRAL,
                hover_color=BUTTON_HOVER,
                active_color=BUTTON_ACTIVE,
                selected=True,
            )
        )
        buttons.append(
            Button(
                rect=pygame.Rect(self.sidebar_rect.left + PADDING + 136, tool_y, 122, BUTTON_HEIGHT),
                label="Eraser (E)",
                callback=lambda: self.set_tool("eraser"),
                base_color=BUTTON_ERASER,
                hover_color=(136, 103, 157),
                active_color=BUTTON_ACTIVE,
            )
        )

        action_y = self.sidebar_rect.bottom - 138
        buttons.append(
            Button(
                rect=pygame.Rect(self.sidebar_rect.left + PADDING, action_y, 80, BUTTON_HEIGHT),
                label="Undo",
                callback=self.undo,
                base_color=BUTTON_NEUTRAL,
                hover_color=BUTTON_HOVER,
                active_color=BUTTON_ACTIVE,
            )
        )
        buttons.append(
            Button(
                rect=pygame.Rect(self.sidebar_rect.left + 108, action_y, 80, BUTTON_HEIGHT),
                label="Clear",
                callback=self.clear_canvas,
                base_color=BUTTON_DANGER,
                hover_color=(184, 83, 68),
                active_color=BUTTON_ACTIVE,
            )
        )
        buttons.append(
            Button(
                rect=pygame.Rect(self.sidebar_rect.left + 196, action_y, 86, BUTTON_HEIGHT),
                label="Save",
                callback=self.save_canvas,
                base_color=BUTTON_SUCCESS,
                hover_color=(68, 158, 107),
                active_color=BUTTON_ACTIVE,
            )
        )
        return buttons

    def rgb_to_hls(self, color: tuple[int, int, int]) -> tuple[float, float, float]:
        red, green, blue = [component / 255 for component in color]
        return colorsys.rgb_to_hls(red, green, blue)

    def enable_high_dpi(self) -> None:
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass

    def hls_to_rgb(self) -> tuple[int, int, int]:
        red, green, blue = colorsys.hls_to_rgb(self.hue, self.lightness, self.saturation)
        return tuple(int(component * 255) for component in (red, green, blue))

    def set_status(self, message: str, color: tuple[int, int, int] = TEXT_MUTED) -> None:
        self.status_message = message
        self.status_color = color

    def save_history_snapshot(self) -> None:
        self.history.append(self.canvas.copy())
        if len(self.history) > HISTORY_LIMIT:
            self.history.pop(0)

    def set_tool(self, tool: str) -> None:
        self.tool = tool
        for button in self.buttons:
            if button.label.startswith("Brush"):
                button.selected = tool == "brush"
            elif button.label.startswith("Eraser"):
                button.selected = tool == "eraser"
        self.set_status(f"Tool set to {tool}.", STATUS_OK)

    def set_brush_size(self, size: int) -> None:
        self.brush_size = max(MIN_BRUSH_SIZE, min(MAX_BRUSH_SIZE, int(round(size))))
        self.set_status(f"Brush size set to {size}px.", STATUS_OK)

    def shift_brush_size(self, direction: int) -> None:
        self.set_brush_size(self.brush_size + direction)

    def open_color_picker(self) -> None:
        try:
            import tkinter as tk
            from tkinter import colorchooser

            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            result = colorchooser.askcolor(color=self.rgb_hex(self.current_color), title="Choose brush color")
            root.destroy()
            if result and result[0]:
                red, green, blue = [int(channel) for channel in result[0]]
                self.set_current_color((red, green, blue), "Picked custom color.", set_brush=True)
        except Exception:
            self.set_status("Color picker unavailable.")

    def clear_canvas(self) -> None:
        self.save_history_snapshot()
        self.canvas.fill(BACKGROUND)
        self.set_status("Canvas cleared.", STATUS_OK)

    def undo(self) -> None:
        if not self.history:
            self.set_status("Nothing to undo.")
            return
        self.canvas = self.history.pop()
        self.set_status("Undo applied.", STATUS_OK)

    def save_canvas(self) -> None:
        default_name = f"sketch-{datetime.now().strftime('%Y%m%d-%H%M%S')}.png"
        path = self.pick_save_path(default_name)
        if path is None:
            self.set_status("Save cancelled.")
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        pygame.image.save(self.canvas, str(path))
        self.set_status(f"Saved to {path}.", STATUS_OK)

    def pick_save_path(self, default_name: str) -> Path | None:
        try:
            import tkinter as tk
            from tkinter import filedialog

            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            suggested_dir = Path.home() / "Pictures" / "Sketchpad"
            file_path = filedialog.asksaveasfilename(
                title="Save sketch",
                defaultextension=".png",
                filetypes=[("PNG image", "*.png")],
                initialdir=suggested_dir,
                initialfile=default_name,
            )
            root.destroy()
            return Path(file_path) if file_path else None
        except Exception:
            fallback_dir = Path.home() / "Pictures" / "Sketchpad"
            return fallback_dir / default_name

    def select_palette_color(self, color: tuple[int, int, int], name: str) -> None:
        self.set_current_color(color, f"Selected {name.lower()}.", set_brush=True)

    def set_current_color(
        self,
        color: tuple[int, int, int],
        status_message: str,
        *,
        set_brush: bool = False,
    ) -> None:
        self.current_color = color
        self.hue, self.lightness, self.saturation = self.rgb_to_hls(color)
        self.hex_input = self.rgb_hex(color)
        if set_brush:
            self.set_tool("brush")
        self.set_status(status_message, STATUS_OK)

    def apply_slider_value(self, name: str, mouse_x: int) -> None:
        rect = self.slider_rects[name]
        relative = max(0.0, min(1.0, (mouse_x - rect.left) / max(1, rect.width - 1)))
        if name == "hue":
            self.hue = relative
        elif name == "lightness":
            self.lightness = relative
        else:
            self.saturation = relative
        self.set_current_color(self.hls_to_rgb(), "Updated custom color.", set_brush=True)

    def apply_brush_slider(self, mouse_x: int) -> None:
        relative = max(0.0, min(1.0, (mouse_x - self.brush_slider_rect.left) / max(1, self.brush_slider_rect.width - 1)))
        size = MIN_BRUSH_SIZE + round(relative * (MAX_BRUSH_SIZE - MIN_BRUSH_SIZE))
        self.set_brush_size(size)

    def commit_hex_input(self) -> None:
        text = self.hex_input.strip().upper()
        if not text:
            self.hex_input = self.rgb_hex(self.current_color)
            return
        if not text.startswith("#"):
            text = f"#{text}"
        if len(text) != 7:
            self.set_status("Hex color must be 6 digits.")
            self.hex_input = self.rgb_hex(self.current_color)
            return
        try:
            color = tuple(int(text[index:index + 2], 16) for index in (1, 3, 5))
        except ValueError:
            self.set_status("Invalid hex color.")
            self.hex_input = self.rgb_hex(self.current_color)
            return
        self.set_current_color(color, f"Set color to {text}.", set_brush=True)

    def get_draw_color(self) -> tuple[int, int, int]:
        return BACKGROUND if self.tool == "eraser" else self.current_color

    def canvas_position(self, window_pos: tuple[int, int]) -> tuple[int, int]:
        return window_pos[0] - self.canvas_rect.left, window_pos[1] - self.canvas_rect.top

    def start_stroke(self, canvas_pos: tuple[int, int]) -> None:
        self.save_history_snapshot()
        pygame.draw.circle(self.canvas, self.get_draw_color(), canvas_pos, self.brush_size)
        self.is_drawing = True
        self.last_canvas_pos = canvas_pos

    def continue_stroke(self, canvas_pos: tuple[int, int]) -> None:
        if not self.is_drawing or self.last_canvas_pos is None:
            return
        start_x, start_y = self.last_canvas_pos
        end_x, end_y = canvas_pos
        delta_x = end_x - start_x
        delta_y = end_y - start_y
        distance = max(abs(delta_x), abs(delta_y))
        for step in range(distance + 1):
            x = start_x + (delta_x * step) / max(1, distance)
            y = start_y + (delta_y * step) / max(1, distance)
            pygame.draw.circle(self.canvas, self.get_draw_color(), (int(x), int(y)), self.brush_size)
        self.last_canvas_pos = canvas_pos

    def stop_stroke(self) -> None:
        self.is_drawing = False
        self.last_canvas_pos = None

    def handle_keyboard_shortcut(self, event: pygame.event.Event) -> None:
        if self.active_hex_input:
            self.handle_hex_key(event)
            return
        if event.key == pygame.K_b:
            self.set_tool("brush")
        elif event.key == pygame.K_e:
            self.set_tool("eraser")
        elif event.key == pygame.K_LEFTBRACKET:
            self.shift_brush_size(-1)
        elif event.key == pygame.K_RIGHTBRACKET:
            self.shift_brush_size(1)
        elif event.key == pygame.K_s and (event.mod & pygame.KMOD_CTRL):
            self.save_canvas()
        elif event.key == pygame.K_z and (event.mod & pygame.KMOD_CTRL):
            self.undo()
        elif event.key == pygame.K_n and (event.mod & pygame.KMOD_CTRL):
            self.clear_canvas()

    def handle_hex_key(self, event: pygame.event.Event) -> None:
        if event.key == pygame.K_RETURN:
            self.active_hex_input = False
            self.commit_hex_input()
        elif event.key == pygame.K_ESCAPE:
            self.active_hex_input = False
            self.hex_input = self.rgb_hex(self.current_color)
            self.set_status("Hex entry cancelled.")
        elif event.key == pygame.K_BACKSPACE:
            self.hex_input = self.hex_input[:-1]
        else:
            if event.unicode and event.unicode.upper() in "#0123456789ABCDEF" and len(self.hex_input) < 7:
                if event.unicode == "#" and self.hex_input:
                    return
                self.hex_input += event.unicode.upper()

    def handle_mouse_down(self, pos: tuple[int, int]) -> None:
        self.active_hex_input = False
        if self.canvas_rect.collidepoint(pos):
            self.start_stroke(self.canvas_position(pos))
            return

        if self.preview_rect.collidepoint(pos):
            self.open_color_picker()
            return

        if self.hex_input_rect.collidepoint(pos):
            self.active_hex_input = True
            return

        if self.brush_slider_rect.collidepoint(pos):
            self.active_slider = "brush_size"
            self.apply_brush_slider(pos[0])
            return

        for name, rect in self.slider_rects.items():
            if rect.collidepoint(pos):
                self.active_slider = name
                self.apply_slider_value(name, pos[0])
                return

        if self.handle_palette_click(pos):
            return

        for button in self.buttons:
            if button.handle_click(pos):
                return

    def handle_palette_click(self, pos: tuple[int, int]) -> bool:
        swatches = self.palette_swatches()
        for name, color, rect in swatches:
            if rect.collidepoint(pos):
                self.select_palette_color(color, name)
                return True
        return False

    def palette_swatches(self) -> list[tuple[str, tuple[int, int, int], pygame.Rect]]:
        swatches: list[tuple[str, tuple[int, int, int], pygame.Rect]] = []
        start_x = self.sidebar_rect.left + PADDING
        start_y = self.sidebar_rect.top + 96
        for index, (name, color) in enumerate(PALETTE):
            col = index % 5
            row = index // 5
            rect = pygame.Rect(start_x + (col * 50), start_y + (row * 50), SWATCH_SIZE, SWATCH_SIZE)
            swatches.append((name, color, rect))
        return swatches

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self.handle_keyboard_shortcut(event)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.handle_mouse_down(event.pos)
            elif event.type == pygame.MOUSEMOTION:
                if self.active_slider == "brush_size":
                    self.apply_brush_slider(event.pos[0])
                elif self.active_slider is not None:
                    self.apply_slider_value(self.active_slider, event.pos[0])
                elif self.is_drawing and self.canvas_rect.collidepoint(event.pos):
                    self.continue_stroke(self.canvas_position(event.pos))
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.active_slider = None
                self.stop_stroke()

    def draw_sidebar(self) -> None:
        pygame.draw.rect(self.window, SIDEBAR_BACKGROUND, self.sidebar_rect, border_radius=18)
        pygame.draw.rect(self.window, SIDEBAR_BORDER, self.sidebar_rect, width=1, border_radius=18)

        title = self.title_font.render("Sketchpad Studio", True, TEXT_PRIMARY)
        self.window.blit(title, (self.sidebar_rect.left + PADDING, self.sidebar_rect.top + 18))

        self.draw_section_label("Palette", self.sidebar_rect.top + 72)
        for name, color, rect in self.palette_swatches():
            pygame.draw.rect(self.window, color, rect, border_radius=10)
            border_color = BUTTON_ACTIVE if color == self.current_color and self.tool == "brush" else SIDEBAR_BORDER
            pygame.draw.rect(self.window, border_color, rect, width=2, border_radius=10)
            label = self.small_font.render(name[0], True, (18, 18, 18) if sum(color) > 390 else TEXT_PRIMARY)
            self.window.blit(label, label.get_rect(center=rect.center))

        self.draw_section_label("Tools", self.sidebar_rect.top + 222)
        self.draw_section_label("Brush Size", self.sidebar_rect.top + 300)
        self.draw_section_label("Custom Color", self.sidebar_rect.top + 426)
        self.draw_brush_slider()

        preview_rect = self.preview_rect
        pygame.draw.rect(self.window, self.current_color, preview_rect, border_radius=14)
        pygame.draw.rect(self.window, SIDEBAR_BORDER, preview_rect, width=2, border_radius=14)
        self.draw_hex_input()

        for label, name in [("Hue", "hue"), ("Lightness", "lightness"), ("Saturation", "saturation")]:
            self.draw_slider(label, name)

        self.draw_section_label("Actions", self.sidebar_rect.bottom - 172)
        shortcuts = [
            "B brush   E eraser",
            "[ ] adjust brush",
            "Ctrl+Z undo",
            "Ctrl+S save",
        ]
        shortcut_y = self.sidebar_rect.bottom - 86
        for line in shortcuts:
            line_surface = self.small_font.render(line, True, TEXT_MUTED)
            self.window.blit(line_surface, (self.sidebar_rect.left + PADDING, shortcut_y))
            shortcut_y += 18

        for button in self.buttons:
            button.draw(self.window, self.body_font)

    def draw_section_label(self, text: str, y: int) -> None:
        label = self.small_font.render(text.upper(), True, TEXT_MUTED)
        self.window.blit(label, (self.sidebar_rect.left + PADDING, y))

    def draw_brush_slider(self) -> None:
        label = self.small_font.render(f"Thickness {self.brush_size}px", True, TEXT_PRIMARY)
        self.window.blit(label, (self.brush_slider_rect.left, self.brush_slider_rect.top - 24))
        pygame.draw.rect(self.window, SIDEBAR_SECTION, self.brush_slider_rect, border_radius=8)
        fill_width = int(((self.brush_size - MIN_BRUSH_SIZE) / (MAX_BRUSH_SIZE - MIN_BRUSH_SIZE)) * self.brush_slider_rect.width)
        if fill_width > 0:
            fill_rect = pygame.Rect(self.brush_slider_rect.left, self.brush_slider_rect.top, fill_width, self.brush_slider_rect.height)
            pygame.draw.rect(self.window, BUTTON_ACTIVE, fill_rect, border_radius=8)
        pygame.draw.rect(self.window, SIDEBAR_BORDER, self.brush_slider_rect, width=1, border_radius=8)
        marker_x = self.brush_slider_rect.left + fill_width
        marker_rect = pygame.Rect(marker_x - 4, self.brush_slider_rect.top - 3, 8, self.brush_slider_rect.height + 6)
        pygame.draw.rect(self.window, TEXT_PRIMARY, marker_rect, border_radius=4)

    def draw_hex_input(self) -> None:
        box_color = BUTTON_ACTIVE if self.active_hex_input else SIDEBAR_SECTION
        pygame.draw.rect(self.window, box_color, self.hex_input_rect, border_radius=8)
        pygame.draw.rect(self.window, SIDEBAR_BORDER, self.hex_input_rect, width=1, border_radius=8)
        text = self.hex_input if self.hex_input else "#"
        text_surface = self.small_font.render(text, True, TEXT_PRIMARY)
        self.window.blit(text_surface, (self.hex_input_rect.left + 10, self.hex_input_rect.top + 7))

    def draw_slider(self, label: str, name: str) -> None:
        rect = self.slider_rects[name]
        label_surface = self.small_font.render(label, True, TEXT_MUTED)
        self.window.blit(label_surface, (rect.left, rect.top - 24))

        slider_surface = pygame.Surface(rect.size)
        for index in range(rect.width):
            ratio = index / max(1, rect.width - 1)
            if name == "hue":
                color = colorsys.hls_to_rgb(ratio, 0.5, 1.0)
            elif name == "lightness":
                color = colorsys.hls_to_rgb(self.hue, ratio, self.saturation)
            else:
                color = colorsys.hls_to_rgb(self.hue, self.lightness, ratio)
            pygame.draw.line(
                slider_surface,
                tuple(int(component * 255) for component in color),
                (index, 0),
                (index, rect.height),
            )
        self.window.blit(slider_surface, rect.topleft)
        pygame.draw.rect(self.window, SIDEBAR_BORDER, rect, width=1, border_radius=8)

        value = {
            "hue": self.hue,
            "lightness": self.lightness,
            "saturation": self.saturation,
        }[name]
        marker_x = rect.left + int(value * max(1, rect.width - 1))
        marker_rect = pygame.Rect(marker_x - 4, rect.top - 3, 8, rect.height + 6)
        pygame.draw.rect(self.window, TEXT_PRIMARY, marker_rect, border_radius=4)

    def draw_canvas(self) -> None:
        shadow_rect = self.canvas_rect.move(8, 10)
        pygame.draw.rect(self.window, CANVAS_DROP, shadow_rect, border_radius=10)
        pygame.draw.rect(self.window, (253, 251, 247), self.canvas_rect, border_radius=10)
        pygame.draw.rect(self.window, CANVAS_BORDER, self.canvas_rect, width=2, border_radius=10)
        self.window.blit(self.canvas, self.canvas_rect.topleft)

    def draw_status_bar(self) -> None:
        pygame.draw.rect(self.window, (245, 241, 235), self.status_rect, border_radius=12)
        pygame.draw.rect(self.window, CANVAS_BORDER, self.status_rect, width=1, border_radius=12)
        mode_text = f"{self.tool.upper()}  |  {self.brush_size}px  |  {self.rgb_hex(self.current_color)}"
        mode_surface = self.status_font.render(mode_text, True, (52, 47, 42))
        status_surface = self.status_font.render(self.status_message, True, self.status_color)
        self.window.blit(mode_surface, (self.status_rect.left + 14, self.status_rect.top + 13))
        self.window.blit(status_surface, (self.status_rect.right - status_surface.get_width() - 14, self.status_rect.top + 13))

    def rgb_hex(self, color: tuple[int, int, int]) -> str:
        return "#{:02X}{:02X}{:02X}".format(*color)

    def draw(self) -> None:
        self.window.fill(APP_BACKGROUND)
        self.draw_canvas()
        self.draw_status_bar()
        self.draw_sidebar()
        pygame.display.flip()

    def run(self) -> int:
        self.set_status("Sketchpad Studio ready.", STATUS_OK)
        while self.running:
            self.handle_events()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
        return 0


def main() -> int:
    app = SketchpadApp()
    return app.run()

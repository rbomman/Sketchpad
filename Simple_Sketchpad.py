# Name: Simple Sketchpad
# Description: A sketchpad application in which you can draw in a variety of colours, different brush widths and save your drawings
# Author: Rishith Bomman
# Date: 2023/07/03
# Version: 1.0

# Save Downloads the file to "~\Desktop\screenshots"
# Clear wipes the screen so you can continue drawing something new
# Draw Slowly for best results

# License:  MIT License


# Imports
import sys
import pygame
import os

# Configuration
pygame.init()

# Set window dimensions
WIDTH = 1280
HEIGHT = 720

# Set panel dimensions
PANEL_WIDTH = 80

# Set colors
BIAS_COLOR = (33, 33, 33)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

#Set Sizes
XSMALL = 1
SMALL = 3
MEDIUM = 5
LARGE = 7
XLARGE = 9

#Background settings
# Set background color
BACKGROUND_COLOR = (255, 255, 255)  # White color

# Set the portion to fill sidebar with a different color
sidebar_rect = pygame.Rect(1180, 0, 100, 720)  # Rectangle coordinates (x, y, width, height)
sidebar_color = (100, 100, 100)  # Gray

# Set the portion to fill main display with a different color
screen_rect = pygame.Rect(0, 0, 1180, 720)  # Rectangle coordinates (x, y, width, height)
screen_color = (255, 255, 255)  # White

# Initialize Pygame
pygame.init()

draw_color = WHITE
draw_radius = 5

# Create a window
window = pygame.display.set_mode((WIDTH + PANEL_WIDTH, HEIGHT))
pygame.display.set_caption("Drawing Application")

#fps = 10000
fpsClock = pygame.time.Clock()
width, height = 1280, 720
screen = pygame.display.set_mode((width, height))

font = pygame.font.SysFont('Arial', 20)

objects = []

class Button():
    def __init__(self, color, x, y, width, height, buttonText='Button', onclickFunction=None, onePress=True):
        
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.onclickFunction = onclickFunction
        self.onePress = onePress
        self.color = color

        self.fillColors = {
            'normal': color,
            'hover': tuple(max(c1 - c2, 0) for c1, c2 in zip(color, BIAS_COLOR)),
            'pressed': tuple(max(c1 - 3*c2, 0) for c1, c2 in zip(color, BIAS_COLOR)),
        }

        self.buttonSurface = pygame.Surface((self.width, self.height))
        self.buttonRect = pygame.Rect(self.x, self.y, self.width, self.height)

        self.buttonSurf = font.render(buttonText, True, (20, 20, 20))

        self.alreadyPressed = False

        buttons.append(self)

    def process(self):

        mousePos = pygame.mouse.get_pos()
        
        self.buttonSurface.fill(self.fillColors['normal'])
        if self.buttonRect.collidepoint(mousePos):
            self.buttonSurface.fill(self.fillColors['hover'])

            if pygame.mouse.get_pressed(num_buttons=3)[0]:
                self.buttonSurface.fill(self.fillColors['pressed'])

                if self.onePress:
                    self.onclickFunction(self)

            else:
                self.alreadyPressed = False

        self.buttonSurface.blit(self.buttonSurf, [
            self.buttonRect.width/2 - self.buttonSurf.get_rect().width/2,
            self.buttonRect.height/2 - self.buttonSurf.get_rect().height/2
        ])
        screen.blit(self.buttonSurface, self.buttonRect)

#button functions
def set_color(self):
    global draw_color
    draw_color = self.color

def set_xsmall_font(self):
    global draw_radius
    draw_radius = XSMALL

def set_small_font(self):
    global draw_radius
    draw_radius = SMALL

def set_medium_font(self):
    global draw_radius
    draw_radius = MEDIUM

def set_large_font(self):
    global draw_radius
    draw_radius = LARGE

def set_xlarge_font(self):
    global draw_radius
    draw_radius = XLARGE

def save_drawing(self):
    # Set screenshot folder path
    screenshot_folder = os.path.expanduser("~\Desktop\screenshots")
    
    # Capture screenshot of drawing pad portion of the window
    screenshot = pygame.Surface((WIDTH  - 100, HEIGHT))
    screenshot.blit(window, (0, 0), pygame.Rect(0, 0, WIDTH - 100, HEIGHT))
    screenshot_path = os.path.join(screenshot_folder, "sketchpad_saved_image.png")
    pygame.image.save(screenshot, screenshot_path)

def clear_drawing(self):
    pygame.draw.rect(window, screen_color, screen_rect)
    

# Create buttons
buttons = []

#Colours
white_bt = Button(WHITE, 1200, 30, 50, 50, '', set_color)
black_bt = Button(BLACK, 1200, 80, 50, 50, '', set_color)
red_bt = Button(RED, 1200, 130, 50, 50, '', set_color)
green_bt = Button(GREEN, 1200, 180, 50, 50, '', set_color)
blue_bt = Button(BLUE, 1200, 230, 50, 50, '', set_color )

#Font size Buttons
xsmall_font = Button(WHITE, 1200, 330, 50, 50, 'XS', set_xsmall_font)
small_font = Button(WHITE, 1200, 380, 50, 50, 'S', set_small_font)
medium_font = Button(WHITE, 1200, 430, 50, 50, 'M', set_medium_font)
large_font = Button(WHITE, 1200, 480, 50, 50, 'L', set_large_font)
xlarge_font = Button(WHITE, 1200, 530, 50, 50, 'XL', set_xlarge_font)

#Functional Buttons
save_drawing_bt = Button(WHITE, 1200, 620, 50, 50, 'Save', save_drawing)
clear_drawing_bt = Button(WHITE, 1200, 670, 50, 50, 'Clear', clear_drawing)

# Fill only the specified portion with a different color
pygame.draw.rect(window, sidebar_color, sidebar_rect)
pygame.draw.rect(window, screen_color, screen_rect)

# Main program loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and event.pos[0] < window.get_width() - 107:  # Left mouse button on the drawing pad part of the screen:
                pygame.draw.circle(window, draw_color, event.pos, draw_radius)
        elif event.type == pygame.MOUSEMOTION:
            if pygame.mouse.get_pressed()[0] and event.pos[0] < window.get_width() - 109:  # Left mouse button held on the drawing pad part of the screen:
                pygame.draw.circle(window, draw_color, event.pos, draw_radius)

    for object in buttons:
        object.process()

    # Update the display
    pygame.display.flip()

# Quit the program
pygame.quit()

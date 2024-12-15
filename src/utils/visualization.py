import sys
import os
import pygame
from src.environment.map1 import Map, Robot, OBSTACLE, ROBOT, GOAL  # Hier werden die Symbole importiert

# Farben
WHITE = (255, 255, 255)

# Fenstergröße
WINDOW_SIZE = 500
CELL_SIZE = 25

MAP_WIDTH = 20  # Beispielwert für die Breite der Karte
MAP_HEIGHT = 20  # Beispielwert für die Höhe der Karte

# Bilder für Roboter und Ziel
ROBOT_IMAGE = pygame.image.load('images/robot_head.png')  # Dein Roboterbild
GOAL_IMAGE = pygame.image.load('images/goal_flag.png')    # Dein Zielbild

# Bilder skalieren (optional)
ROBOT_IMAGE = pygame.transform.scale(ROBOT_IMAGE, (CELL_SIZE, CELL_SIZE))
GOAL_IMAGE = pygame.transform.scale(GOAL_IMAGE, (CELL_SIZE, CELL_SIZE))

def draw_map(screen, game_map):
    """Zeichnet die Karte auf dem Bildschirm."""
    for y, row in enumerate(game_map.grid):
        for x, cell in enumerate(row):
            # Hintergrundfarbe
            color = WHITE
            if cell == OBSTACLE:
                color = (0, 0, 0)  # Hindernisse in schwarz

            # Zeichne das Raster
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (200, 200, 200), rect, 1)  # Rasterlinien

            # Zeichne den Roboter (wenn vorhanden)
            if cell == ROBOT:
                screen.blit(ROBOT_IMAGE, rect.topleft)
            
            # Zeichne das Ziel (wenn vorhanden)
            elif cell == GOAL:
                screen.blit(GOAL_IMAGE, rect.topleft)

if __name__ == "__main__":
    pygame.init()

    # Karte erstellen
    game_map = Map(MAP_WIDTH, MAP_HEIGHT)
    game_map.add_obstacles(50)
    game_map.place_goal(15, 15)
    robot = Robot(0, 0, game_map)

    # Pygame-Fenster einrichten
    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
    pygame.display.set_caption("2D-Simulation")

    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Karte zeichnen
        screen.fill(WHITE)
        draw_map(screen, game_map)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

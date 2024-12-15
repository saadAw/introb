import random
import pygame

# Symbole für die Karte
FREE = 0
OBSTACLE = 1
ROBOT = 'R'
GOAL = 'G'

class Map:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[FREE for _ in range(width)] for _ in range(height)]
        self.cell_size = 128  # Größe der Zellen, angepasst an die Originalgröße des Roboters
        self.screen_width = self.width * self.cell_size  # Bildschirmbreite an die Zellen anpassen
        self.screen_height = self.height * self.cell_size  # Bildschirmhöhe an die Zellen anpassen

    def add_obstacles(self, num_obstacles):
        """Fügt eine bestimmte Anzahl an Hindernissen zufällig hinzu."""
        for _ in range(num_obstacles):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if self.grid[y][x] == FREE:
                self.grid[y][x] = OBSTACLE

    def place_robot(self, x=0, y=0):
        """Platziert den Roboter auf der Karte."""
        # Hier startet der Roboter nun direkt in der oberen linken Ecke
        if self.grid[y][x] == FREE:
            self.grid[y][x] = ROBOT
            return x, y  # Gibt die Position des Roboters zurück, um ihn in Pygame anzuzeigen
        else:
            placed = False
            for i in range(self.height):
                for j in range(self.width):
                    if self.grid[i][j] == FREE:
                        self.grid[i][j] = ROBOT
                        placed = True
                        return j, i  # Die x, y Koordinaten umkehren, da j die horizontale und i die vertikale Position ist
                if placed:
                    break
            if not placed:
                raise ValueError("Keine freie Position für den Roboter gefunden!")


    def place_goal(self, x, y):
        """Platziert das Ziel auf der Karte."""
        if self.grid[y][x] == FREE and not (x == 0 and y == 0):
            self.grid[y][x] = GOAL
        else:
            found = False
            for i in range(self.height - 1, self.height // 2, -1):
                for j in range(self.width - 1, self.width // 2, -1):
                    if self.grid[i][j] == FREE and not (i == 0 and j == 0):
                        self.grid[i][j] = GOAL
                        found = True
                        break
                if found:
                    break
            if not found:
                raise ValueError("Kein freier Platz für das Ziel gefunden!")

    def draw_map(self, surface):
        """Zeigt die Karte im Pygame-Fenster an."""
        for y in range(self.height):
            for x in range(self.width):
                cell_x = x * self.cell_size
                cell_y = y * self.cell_size
                
                # Freie Felder zeichnen
                if self.grid[y][x] == FREE:
                    pygame.draw.rect(surface, (255, 255, 255), (cell_x, cell_y, self.cell_size, self.cell_size))
                # Hindernisse zeichnen
                elif self.grid[y][x] == OBSTACLE:
                    pygame.draw.rect(surface, (0, 0, 0), (cell_x, cell_y, self.cell_size, self.cell_size))
                # Ziel zeichnen
                elif self.grid[y][x] == GOAL:
                    pygame.draw.rect(surface, (0, 255, 0), (cell_x, cell_y, self.cell_size, self.cell_size))
                # Roboter zeichnen
                elif self.grid[y][x] == ROBOT:
                    pygame.draw.rect(surface, (255, 0, 0), (cell_x, cell_y, self.cell_size, self.cell_size))

        # Netzlinien zeichnen
        for x in range(self.width + 1):
            pygame.draw.line(surface, (200, 200, 200), (x * self.cell_size, 0), (x * self.cell_size, self.screen_height))
        for y in range(self.height + 1):
            pygame.draw.line(surface, (200, 200, 200), (0, y * self.cell_size), (self.screen_width, y * self.cell_size))

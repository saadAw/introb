from src.environment.constants import MapSymbols, CELL_SIZE, COLORS
import random
import pygame

class Map:  
    def __init__(self, width, height):  
        self.width = width  
        self.height = height  
        self.grid = [[MapSymbols.FREE for _ in range(width)] for _ in range(height)]  
        self.cell_size = CELL_SIZE  
        self.screen_width = self.width * self.cell_size  
        self.screen_height = self.height * self.cell_size  
        self.robot_pos = None  
        self.goal_pos = None

    def add_obstacles(self, num_obstacles):
        """Fügt eine bestimmte Anzahl an Hindernissen zufällig hinzu."""
        for _ in range(num_obstacles):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if self.grid[y][x] == MapSymbols.FREE:  # Hier geändert
                self.grid[y][x] = MapSymbols.OBSTACLE  # Hier geändert

    def place_robot(self, x=0, y=0):  
        if self.robot_pos:  # Alte Position löschen  
            old_x, old_y = self.robot_pos  
            self.grid[old_y][old_x] = MapSymbols.FREE  

        if self.grid[y][x] == MapSymbols.FREE:  
            self.grid[y][x] = MapSymbols.ROBOT  
            self.robot_pos = (x, y)  
            return x, y
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
        if self.goal_pos:  # Alte Position löschen  
            old_x, old_y = self.goal_pos  
            self.grid[old_y][old_x] = MapSymbols.FREE  

        if self.grid[y][x] == MapSymbols.FREE and not (x == 0 and y == 0):  
            self.grid[y][x] = MapSymbols.GOAL  
            self.goal_pos = (x, y)
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
        for y in range(self.height):
            for x in range(self.width):
                cell_x = x * self.cell_size
                cell_y = y * self.cell_size

                # Freie Felder zeichnen
                if self.grid[y][x] == MapSymbols.FREE:
                    pygame.draw.rect(surface, COLORS['WHITE'], (cell_x, cell_y, self.cell_size, self.cell_size))
                # Hindernisse zeichnen
                elif self.grid[y][x] == MapSymbols.OBSTACLE:
                    pygame.draw.rect(surface, COLORS['BLACK'], (cell_x, cell_y, self.cell_size, self.cell_size))
                # Ziel zeichnen
                elif self.grid[y][x] == MapSymbols.GOAL:
                    pygame.draw.rect(surface, COLORS['GREEN'], (cell_x, cell_y, self.cell_size, self.cell_size))
                # Roboter zeichnen
                elif self.grid[y][x] == MapSymbols.ROBOT:
                    pygame.draw.rect(surface, COLORS['RED'], (cell_x, cell_y, self.cell_size, self.cell_size))

        # Netzlinien zeichnen
        for x in range(self.width + 1):
            pygame.draw.line(surface, COLORS['GRID'], (x * self.cell_size, 0), 
                            (x * self.cell_size, self.screen_height))
        for y in range(self.height + 1):
            pygame.draw.line(surface, COLORS['GRID'], (0, y * self.cell_size), 
                            (self.screen_width, y * self.cell_size))

    def is_valid_move(self, x, y):  
        """Überprüft, ob eine Position gültig ist."""  
        return (0 <= x < self.width and   
                0 <= y < self.height and   
                self.grid[y][x] != MapSymbols.OBSTACLE)

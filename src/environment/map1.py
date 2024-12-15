# Karte 1: Definition der ersten Simulationsumgebung

# Diese Datei beschreibt die Eigenschaften und die Struktur der ersten Karte.

import random
import pygame

# Kartengröße
MAP_WIDTH = 20
MAP_HEIGHT = 20

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

    def add_obstacles(self, num_obstacles):
        """Fügt eine bestimmte Anzahl an Hindernissen zufällig hinzu."""
        for _ in range(num_obstacles):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            # Überprüfen, ob der Platz frei ist, bevor das Hindernis platziert wird
            if self.grid[y][x] == FREE:
                self.grid[y][x] = OBSTACLE

    def place_robot(self, x, y):
        """Platziert den Roboter auf der Karte."""
        if self.grid[y][x] == FREE:  # Überprüfen, ob der Platz frei ist
            self.grid[y][x] = ROBOT
        else:
            raise ValueError("Der Platz ist blockiert oder bereits belegt!")

    def place_robot(self, x, y):
        """Platziert den Roboter auf der Karte."""
        # Überprüfen, ob der Platz frei ist, andernfalls eine freie Stelle suchen
        if self.grid[y][x] == FREE:
            self.grid[y][x] = ROBOT
        else:
            # Suchen nach einer freien Position
            placed = False
            for i in range(self.height):
                for j in range(self.width):
                    if self.grid[i][j] == FREE:
                        self.grid[i][j] = ROBOT
                        self.x, self.y = j, i
                        placed = True
                        break
                if placed:
                    break
            if not placed:
                raise ValueError("Keine freie Position für den Roboter gefunden!")

    def place_goal(self, x, y):
        """Platziert das Ziel auf der Karte, aber nur, wenn der Platz frei ist und nicht direkt beim Roboter."""
        if self.grid[y][x] == FREE and not (x == 0 and y == 0):  # Verhindert Platzierung auf dem Roboter
            self.grid[y][x] = GOAL
        else:
            # Suche nach einem freien Platz für das Ziel
            found = False
            for i in range(self.height - 1, self.height // 2, -1):  # Suche in der unteren Hälfte der Karte
                for j in range(self.width - 1, self.width // 2, -1):  # Suche in der rechten Hälfte der Karte
                    if self.grid[i][j] == FREE and not (i == 0 and j == 0):  # Verhindert Platzierung direkt beim Roboter
                        self.grid[i][j] = GOAL
                        found = True
                        break
                if found:
                    break
            if not found:
                raise ValueError("Kein freier Platz für das Ziel gefunden!")


class Robot:
    def __init__(self, x, y, game_map):
        self.x = x
        self.y = y
        self.map = game_map
        self.map.place_robot(x, y)

    def move(self, direction):
        """Bewegt den Roboter in eine Richtung ('up', 'down', 'left', 'right')."""
        new_x, new_y = self.x, self.y
        if direction == 'up':
            new_y -= 1
        elif direction == 'down':
            new_y += 1
        elif direction == 'left':
            new_x -= 1
        elif direction == 'right':
            new_x += 1

        # Überprüfen, ob der neue Platz gültig ist
        if 0 <= new_x < self.map.width and 0 <= new_y < self.map.height:
            if self.map.grid[new_y][new_x] == FREE:
                # Update Position
                self.map.grid[self.y][self.x] = FREE  # Alten Platz freigeben
                self.x, self.y = new_x, new_y
                self.map.grid[new_y][new_x] = ROBOT  # Neuen Platz markieren
            else:
                print("Kollision mit Hindernis!")
        else:
            print("Bewegung außerhalb der Karte!")

# Hauptfunktion zum Testen
if __name__ == "__main__":
    # Karte erstellen
    game_map = Map(MAP_WIDTH, MAP_HEIGHT)

    # Hindernisse hinzufügen
    game_map.add_obstacles(50)

    # Ziel platzieren
    try:
        game_map.place_goal(15, 15)
    except ValueError as e:
        print(e)

    # Roboter erstellen
    robot = Robot(0, 0, game_map)

    # Karte anzeigen
    print("Startzustand der Karte:")
    game_map.display()

    # Roboter bewegt sich
    print("\nRoboter bewegt sich:")
    robot.move('down')
    robot.move('right')

    # Karte anzeigen
    print("\nAktueller Zustand der Karte:")
    game_map.display()

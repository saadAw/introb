import pygame
from src.environment import Map, Robot

# Initialisiere Pygame
pygame.init()

# Erstelle eine Spielkarte
game_map = Map(10, 10)  # Karte mit 10x10 Feldern
game_map.add_obstacles(20)  # Füge 20 Hindernisse hinzu
game_map.place_goal(8, 8)  # Platziere das Ziel auf (8, 8)

# Lade die Pfade zu den Bildordnern
idle_path = 'images/idle60'
walk_paths = {
    'down': 'images/walk60/down',
    'up': 'images/walk60/up',
    'left': 'images/walk60/left',
    'right': 'images/walk60/right'
}

# Platziere den Roboter an einer festen Position auf der Karte, z.B. oben links (0, 0)
robot_x, robot_y = 0, 0  # Startposition auf der Karte

# Berechne die Pygame-Position des Roboters
robot = Robot(
    robot_x,  # Startposition x auf der Karte
    robot_y,  # Startposition y auf der Karte
    idle_path,
    walk_paths,
    speed=1  # Geschwindigkeit des Roboters anpassen (z.B. 1 Pixel pro Frame)
)

# Pygame-Fenster initialisieren
screen = pygame.display.set_mode((game_map.screen_width, game_map.screen_height))  # Größeres Fenster entsprechend der Karte
pygame.display.set_caption('Robot Map')

# Spiel Schleife
running = True
while running:
    screen.fill((255, 255, 255))  # Hintergrund auf weiß setzen

    # Zeichne die Karte
    game_map.draw_map(screen)

    # Überprüfe auf Tasteneingaben
    keys = pygame.key.get_pressed()
    if keys[pygame.K_DOWN]:
        robot.move('down')
    elif keys[pygame.K_UP]:
        robot.move('up')
    elif keys[pygame.K_LEFT]:
        robot.move('left')
    elif keys[pygame.K_RIGHT]:
        robot.move('right')
    else:
        robot.move('idle')

    # Roboter anzeigen
    robot.display(screen)

    # Aktualisiere den Bildschirm
    pygame.display.flip()

    # Beende das Spiel, wenn das Fenster geschlossen wird
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Setze die Bildrate
    pygame.time.Clock().tick(30)

# Beende Pygame
pygame.quit()

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

# Definiere die endgültige kleinere Größe des Fensters
scaled_window_width = 900  # Neue Fensterbreite
scaled_window_height = 900  # Neue Fensterhöhe

# Initialisiere das Pygame Fenster mit der kleineren Größe
screen = pygame.display.set_mode((scaled_window_width, scaled_window_height))

# Erstelle eine größere Oberfläche, auf der die gesamte Karte, der Roboter usw. gezeichnet werden
full_surface_width = game_map.screen_width  # Die ursprüngliche größere Karte
full_surface_height = game_map.screen_height
full_surface = pygame.Surface((full_surface_width, full_surface_height))

# Platziere den Roboter auf der Karte (diese Zeile sorgt dafür, dass er auf (0, 0) platziert wird)
game_map.place_robot(robot_x, robot_y)

# Spiel Schleife
running = True
while running:
    # Zeichne den Hintergrund der gesamten Karte auf der vollen Oberfläche
    full_surface.fill((255, 255, 255))  # Weißer Hintergrund für die gesamte Fläche
    
    # Zeichne die Karte auf die große Oberfläche
    game_map.draw_map(full_surface)
    
    # Bewege den Roboter entsprechend den Tasten
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
    
    # Zeichne den Roboter auf die große Oberfläche
    robot.display(full_surface)

    # Skaliere die gesamte große Oberfläche auf das kleinere Fenster
    scaled_surface = pygame.transform.scale(full_surface, (scaled_window_width, scaled_window_height))
    
    # Zeige das skalierte Bild im Fenster
    screen.fill((0, 0, 0))  # Füll den Bildschirm mit einem schwarzen Hintergrund
    screen.blit(scaled_surface, (0, 0))  # Das skalierte Bild wird auf dem Bildschirm angezeigt

    # Aktualisiere den Bildschirm
    pygame.display.flip()

    # Überprüfe, ob das Spiel geschlossen wurde
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Setze die Bildrate
    pygame.time.Clock().tick(30)

# Beende Pygame
pygame.quit()
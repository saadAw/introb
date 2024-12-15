import pygame
from src.environment.map1 import Map
from src.environment.robot1 import Robot

WINDOW_SIZE = 500
CELL_SIZE = 25
MAP_WIDTH = 20
MAP_HEIGHT = 20

def draw_map(screen, game_map):
    """Zeichnet die Karte auf dem Bildschirm."""
    for y, row in enumerate(game_map.grid):
        for x, cell in enumerate(row):
            color = (255, 255, 255)
            if cell == 1:  # Hindernis
                color = (0, 0, 0)
            elif cell == 'R':  # Roboter
                color = (0, 0, 255)
            elif cell == 'G':  # Ziel
                color = (0, 255, 0)
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (200, 200, 200), rect, 1)

def run():
    pygame.init()
    game_map = Map(MAP_WIDTH, MAP_HEIGHT)
    game_map.add_obstacles(50)
    game_map.place_goal(15, 15)

    # Roboter erstellen
    idle_path = "C:/Uni/introb/images/idle60/Armature_idle_"
    walk_path = "C:/Uni/introb/images/walk60/Armature_walk_"
    robot = Robot(0, 0, game_map, idle_path, walk_path)

    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
    pygame.display.set_caption("2D-Simulation")
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            robot.move('up')
        elif keys[pygame.K_DOWN]:
            robot.move('down')
        elif keys[pygame.K_LEFT]:
            robot.move('left')
        elif keys[pygame.K_RIGHT]:
            robot.move('right')

        screen.fill((255, 255, 255))  # Hintergrund
        draw_map(screen, game_map)
        robot.draw(screen, CELL_SIZE)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    run()

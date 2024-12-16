import pygame
from src.environment.map import Map
from src.environment.robot import Robot
from src.game.game_logic import GameLogic
from src.environment.constants import GameState, FPS, COLORS, WINDOW_SIZE, MAP_WIDTH, MAP_HEIGHT

class GameRunner:
    """Main game runner class that handles game initialization and main loop"""
    def __init__(self):
        pygame.init()
        
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("Robot Navigation Game")
        
        self.setup_game()

    def setup_game(self):
        """Initialize game components"""
        self.game_map = Map(MAP_WIDTH, MAP_HEIGHT)
        
        self.robot = Robot(
            x=self.game_map.SPAWN_POS[0],
            y=self.game_map.SPAWN_POS[1],
            idle_path='assets/images/idle60',
            walk_paths={
                'down': 'assets/images/walk60/down',
                'up': 'assets/images/walk60/up',
                'left': 'assets/images/walk60/left',
                'right': 'assets/images/walk60/right'
            },
            speed=1
        )
        
        self.game_map.place_robot(self.robot.x, self.robot.y)
        self.game_logic = GameLogic((MAP_WIDTH, MAP_HEIGHT))
        
        self.full_surface = pygame.Surface((
            self.game_map.screen_width,
            self.game_map.screen_height
        ))

    def handle_events(self):
        """Process game events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and self.game_logic.state != GameState.PLAYING:
                    self.setup_game()
        return True

    def handle_input(self):
        """Handle keyboard input for robot movement"""
        if self.game_logic.state == GameState.PLAYING:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_DOWN]:
                self.robot.move('down', self.game_map)
            elif keys[pygame.K_UP]:
                self.robot.move('up', self.game_map)
            elif keys[pygame.K_LEFT]:
                self.robot.move('left', self.game_map)
            elif keys[pygame.K_RIGHT]:
                self.robot.move('right', self.game_map)
            else:
                self.robot.move('idle', self.game_map)

    def update(self):
        """Update game state"""
        if self.game_logic.state == GameState.PLAYING:
            self.game_logic.update()
            if self.game_map.goal_pos:
                self.game_logic.check_win_condition(
                    (self.robot.x, self.robot.y),
                    self.game_map.goal_pos
                )

    def draw(self):
        """Handle all drawing operations"""
        self.full_surface.fill(COLORS['WHITE'])
        self.game_map.draw_map(self.full_surface)
        self.robot.display(self.full_surface)
        self.game_logic.draw_ui(self.full_surface)

        # Scale and display
        scaled_surface = pygame.transform.scale(
            self.full_surface, WINDOW_SIZE)
        self.screen.fill(COLORS['BLACK'])
        self.screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()

    def run(self):
        """Main game loop"""
        clock = pygame.time.Clock()
        running = True

        while running:
            running = self.handle_events()
            self.handle_input()
            self.update()
            self.draw()
            clock.tick(FPS)

        pygame.quit()

if __name__ == "__main__":
    game = GameRunner()
    game.run()
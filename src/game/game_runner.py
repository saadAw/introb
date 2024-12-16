import pygame
import sys
from enum import Enum

from src.environment.map import Map
from src.environment.robot import Robot
from src.game.game_logic import GameLogic
from src.config.constants import GameState, FPS, COLORS, WINDOW_SIZE, MAP_WIDTH, MAP_HEIGHT
from src.algorithms.pathfinding.dijkstra import DijkstraPathfinder
from src.game.ui_manager import UIManager
# Import other algorithms as they're implemented
# from src.pathfinding.astar import AStarPathfinder
# from src.pathfinding.reinforcement import DQNAgent, PPOAgent

class AlgorithmType(Enum):
    """Enum for different pathfinding algorithms"""
    MANUAL = "Manual Control"
    DIJKSTRA = "Dijkstra"
    ASTAR = "A*"
    QL = "Q-Learning"
    DQN = "Deep Q-Network"

class GameRunner:
    """Main game runner class that handles game initialization and main loop"""
    def __init__(self):
        # Initialize stuff
        if not pygame.get_init():
            pygame.init()
            
        self.ui_manager = UIManager()

        # Set up the display
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("Robot Navigation Game")
        
        # Initialize the clock
        self.clock = pygame.time.Clock()
        
        # Initialize algorithm settings
        self.current_algorithm = AlgorithmType.MANUAL
        self.pathfinders = {}
        self.setup_algorithms()
        
        # Set up game components
        self.setup_game()
        
        # Flag for game loop
        self.running = True
        

    def setup_algorithms(self):
        """Initialize all pathfinding algorithms"""
        try:
            # Initialize only after game_map is created
            self.pathfinders = {
                AlgorithmType.DIJKSTRA: lambda: DijkstraPathfinder(self.game_map),
                # Add other algorithms as they're implemented
                # AlgorithmType.ASTAR: lambda: AStarPathfinder(self.game_map),
                # AlgorithmType.QL: lambda: QLAgent(self.game_map),
                # AlgorithmType.DQN: lambda: DQNAgent(self.game_map),
            }
        except Exception as e:
            print(f"Error setting up algorithms: {e}")
            raise

    def setup_game(self):
        """Initialize game components"""
        try:
            self.game_map = Map(MAP_WIDTH, MAP_HEIGHT)
            self.game_logic = GameLogic((MAP_WIDTH, MAP_HEIGHT))
            
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
            
            # Connect game logic to robot
            self.robot.set_game_logic(self.game_logic)
            
            self.game_map.place_robot(self.robot.x, self.robot.y)
            
            # Create the surface with proper dimensions
            self.full_surface = pygame.Surface((
                self.game_map.screen_width,
                self.game_map.screen_height
            ))
            
            # Initialize algorithms after game_map is created
            self.setup_algorithms()
            
            # Initialize current pathfinder
            self.current_pathfinder = None
            if self.current_algorithm in self.pathfinders:
                self.current_pathfinder = self.pathfinders[self.current_algorithm]()
                
        except Exception as e:
            print(f"Error during game setup: {e}")
            self.cleanup()
            sys.exit(1)

    def handle_events(self):
        """Process game events"""
        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r and self.game_logic.state != GameState.PLAYING:
                        self.setup_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
                        return
                    elif event.key == pygame.K_1:
                        self.current_algorithm = AlgorithmType.MANUAL
                    elif event.key == pygame.K_2:
                        self.current_algorithm = AlgorithmType.DIJKSTRA
                        self.current_pathfinder = self.pathfinders[AlgorithmType.DIJKSTRA]()
                    elif event.key == pygame.K_3:
                        if AlgorithmType.ASTAR in self.pathfinders:
                            self.current_algorithm = AlgorithmType.ASTAR
                            self.current_pathfinder = self.pathfinders[AlgorithmType.ASTAR]()
                    elif event.key == pygame.K_4:
                        if AlgorithmType.DQN in self.pathfinders:
                            self.current_algorithm = AlgorithmType.DQN
                            self.current_pathfinder = self.pathfinders[AlgorithmType.DQN]()
                    elif event.key == pygame.K_5:
                        if AlgorithmType.PPO in self.pathfinders:
                            self.current_algorithm = AlgorithmType.PPO
                            self.current_pathfinder = self.pathfinders[AlgorithmType.PPO]()
        except Exception as e:
            print(f"Error handling events: {e}")
            self.running = False

    def handle_input(self):
        """Handle input based on current algorithm"""
        try:
            if self.game_logic.state == GameState.PLAYING:
                if self.current_algorithm == AlgorithmType.MANUAL:
                    self._handle_manual_input()
                else:
                    self._handle_algorithm_input()
        except Exception as e:
            print(f"Error handling input: {e}")

    def _handle_manual_input(self):
        """Handle keyboard input for manual control"""
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

    def _handle_algorithm_input(self):
        """Handle automated movement based on current algorithm"""
        if self.current_pathfinder:
            next_move = self.current_pathfinder.get_next_move(
                (self.robot.x, self.robot.y),
                self.game_map.goal_pos
            )
            self.robot.move(next_move, self.game_map)

    def update(self):
        """Update game state"""
        try:
            if self.game_logic.state == GameState.PLAYING:
                self.game_logic.update()
                if self.game_map.goal_pos:
                    self.game_logic.check_win_condition(
                        (self.robot.x, self.robot.y),
                        self.game_map.goal_pos
                    )
        except Exception as e:
            print(f"Error updating game state: {e}")

    def draw(self):
        """Handle all drawing operations"""
        try:
            self.full_surface.fill(COLORS['WHITE'])
            self.game_map.draw_map(self.full_surface)
            self.robot.display(self.full_surface)
            
            self.ui_manager.draw_game_ui(
                self.full_surface,
                self.game_logic,
                self.current_algorithm
            )

            scaled_surface = pygame.transform.scale(
                self.full_surface, WINDOW_SIZE)
            self.screen.fill(COLORS['BLACK'])
            self.screen.blit(scaled_surface, (0, 0))
            pygame.display.flip()
        except Exception as e:
            print(f"Error drawing game: {e}")


    def cleanup(self):
        """Clean up pygame resources"""
        try:
            pygame.quit()
        except Exception as e:
            print(f"Error during cleanup: {e}")

    def run(self):
        """Main game loop"""
        try:
            while self.running:
                self.handle_events()
                self.handle_input()
                self.update()
                self.draw()
                self.clock.tick(FPS)
        except Exception as e:
            print(f"Error in main game loop: {e}")
        finally:
            self.cleanup()

if __name__ == "__main__":
    try:
        game = GameRunner()
        game.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        pygame.quit()
        sys.exit(1)
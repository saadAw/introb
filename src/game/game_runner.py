import pygame
import sys
from enum import Enum

from src.environment.map import Map
from src.environment.robot import Robot
from src.game.game_logic import GameLogic
from src.game.ui_manager import UIManager
from src.config.constants import (
    GameState, 
    FPS, 
    COLORS, 
    UI_PANEL_WIDTH,
    calculate_dimensions
)
from src.algorithms.pathfinding.dijkstra import DijkstraPathfinder
from src.algorithms.reinforcement.deep_q_learning import DQNAgent
from src.algorithms.pathfinding.astar import AStarPathfinder

from src.config.types import AlgorithmType

class GameRunner:
    """Main game runner class that handles game initialization and main loop"""
    def __init__(self):
        if not pygame.get_init():
            pygame.init()
            
        self.setup_initial_components()
        self.setup_remaining_components()
        
        self.running = True

    def setup_initial_components(self):
        """Initialize core components needed for window setup"""
        try:
            # Create map first to get dimensions
            self.game_map = Map(0, 0)  # Dimensions will be calculated in Map class
            
            # Set up the display with the map's calculated dimensions
            window_width = UI_PANEL_WIDTH + self.game_map.screen_width
            window_height = self.game_map.screen_height
            
            print(f"Window size: {window_width}x{window_height}")
            print(f"Cell size: {self.game_map.cell_size}")
            
            # Set up the display
            self.screen = pygame.display.set_mode((window_width, window_height))
            pygame.display.set_caption("Robot Navigation Game")
            
        except Exception as e:
            print(f"Error during initial setup: {e}")
            pygame.quit()
            sys.exit(1)

    def setup_remaining_components(self):
            """Initialize remaining game components"""
            try:
                self.ui_manager = UIManager()
                self.clock = pygame.time.Clock()
                self.game_logic = GameLogic((self.game_map.width, self.game_map.height))  
                self.game_logic.state = GameState.WAITING
                
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
                    cell_size=self.game_map.cell_size,
                    speed=1
                )
                
                # Connect game logic to robot
                self.robot.set_game_logic(self.game_logic)
                self.game_map.place_robot(self.robot.x, self.robot.y)
                
                # Create surface for drawing
                self.full_surface = pygame.Surface((
                    UI_PANEL_WIDTH + self.game_map.screen_width,
                    self.game_map.screen_height
                ))
                
                # Initialize algorithm settings
                self.current_algorithm = AlgorithmType.MANUAL
                self.pathfinders = {}
                self.setup_algorithms()
                
                # Initialize current pathfinder
                self.current_pathfinder = None
                if self.current_algorithm in self.pathfinders:
                    self.current_pathfinder = self.pathfinders[self.current_algorithm]()
                    
            except Exception as e:
                print(f"Error during component setup: {e}")
                self.cleanup()
                sys.exit(1)
                

    def setup_game(self):  
        """Reset game state"""  
        try:  
            # Reset map and robot position  
            self.game_map.load_map()  
            self.robot.x = self.game_map.SPAWN_POS[0]  
            self.robot.y = self.game_map.SPAWN_POS[1]  
            self.game_map.place_robot(self.robot.x, self.robot.y)  

            # Reset game logic to waiting state  
            self.game_logic = GameLogic((self.game_map.width, self.game_map.height))  
            self.game_logic.state = GameState.WAITING  
            self.robot.set_game_logic(self.game_logic)  

            # Reset current algorithm  
            self.current_algorithm = AlgorithmType.MANUAL  
            self.current_pathfinder = None  

        except Exception as e:  
            print(f"Error during game reset: {e}")  
            self.cleanup()  
            sys.exit(1)

    def setup_algorithms(self):
        """Initialize all pathfinding algorithms"""
        try:
            self.pathfinders = {
                AlgorithmType.DIJKSTRA: lambda: DijkstraPathfinder(self.game_map),
                AlgorithmType.ASTAR: lambda: AStarPathfinder(self.game_map),
                # Add other algorithms as they're implemented
                # AlgorithmType.QL: lambda: QLAgent(self.game_map),
                AlgorithmType.DQN: lambda: DQNAgent(self.game_map),
            }
        except Exception as e:
            print(f"Error setting up algorithms: {e}")
            raise

    def handle_events(self):  
        """Process game events"""  
        try:  
            for event in pygame.event.get():  
                if event.type == pygame.QUIT or (  
                    event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE  
                ):  
                    self.running = False  
                    return  

                if event.type == pygame.KEYDOWN:  
                    if event.key == pygame.K_r:  
                        self.setup_game()  
                        self.game_logic.state = GameState.WAITING  
                        return  

                    # Algorithmus-Auswahl nur im WAITING-Zustand  
                    if self.game_logic.state == GameState.WAITING:  
                        self._handle_algorithm_selection(event.key)  

        except Exception as e:  
            print(f"Error handling events: {e}")  
            self.running = False  

    def _handle_algorithm_selection(self, key):  
        """Handle algorithm selection based on key press"""  
        if key not in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5]:  
            return  

        # Wenn gleicher Algorithmus gewählt wird, lösche seinen Pfad  
        if self.current_algorithm:  
            self.game_map.clear_algorithm_path(self.current_algorithm)  

        # Dictionary für Algorithmus-Zuordnung  
        algorithm_map = {  
            pygame.K_1: (AlgorithmType.MANUAL, None),  
            pygame.K_2: (AlgorithmType.ASTAR, self.pathfinders.get(AlgorithmType.ASTAR)),  
            pygame.K_3: (AlgorithmType.DIJKSTRA, self.pathfinders.get(AlgorithmType.DIJKSTRA)),  
            pygame.K_4: (AlgorithmType.QL, self.pathfinders.get(AlgorithmType.QL)),  
            pygame.K_5: (AlgorithmType.DQN, self.pathfinders.get(AlgorithmType.DQN))  
        }  

        if key in algorithm_map:  
            algo_type, pathfinder_creator = algorithm_map[key]  
            self.current_algorithm = algo_type  
            self.current_pathfinder = pathfinder_creator() if pathfinder_creator else None  

            if self.current_algorithm:  
                self.game_logic.set_algorithm(self.current_algorithm)  
                self.game_logic.state = GameState.PLAYING
            
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
            # Create main surface with calculated dimensions
            window_width = UI_PANEL_WIDTH + self.game_map.screen_width
            window_height = self.game_map.screen_height
            main_surface = pygame.Surface((window_width, window_height))
            main_surface.fill(COLORS['WHITE'])
            
            # Draw map on the right side of the panel
            self.game_map.draw_map(main_surface, offset_x=UI_PANEL_WIDTH)
            self.robot.display(main_surface, offset_x=UI_PANEL_WIDTH)
            
            # Draw UI on the left panel
            self.ui_manager.draw_game_ui(
                main_surface,
                self.game_logic,
                self.current_algorithm
            )
            
            # Update display
            self.screen.blit(main_surface, (0, 0))
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
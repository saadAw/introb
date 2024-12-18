import pygame
import sys
from enum import Enum

from src.environment.map import Map
from src.environment.robot import Robot
from src.game.game_logic import GameLogic
from src.game.ui_manager import UIManager
from src.game.metrics_manager import MetricsDetailWindow, MetricsManager
from src.config.types import AlgorithmType
from src.config.constants import (
    GameState, 
    FPS, 
    COLORS, 
    UI_PANEL_WIDTH,
    calculate_dimensions
)
from src.algorithms.pathfinding.dijkstra import DijkstraPathfinder
from src.algorithms.pathfinding.astar import AStarPathfinder
from src.algorithms.pathfinding.greedy_best_first import GreedyBestFirstPathfinder
from src.algorithms.pathfinding.breadth_first import BFSPathfinder
from src.algorithms.reinforcement.q_learning import QLearningPathfinder
from src.algorithms.reinforcement.sarsa import SARSAPathfinder


class GameRunner:
    """Main game runner class that handles game initialization and main loop"""
    def __init__(self):
        if not pygame.get_init():
            pygame.init()
            
        self.setup_initial_components()
        self.setup_remaining_components()
        self.metrics_detail_window = MetricsDetailWindow()
        
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
                self.metrics_manager = MetricsManager()  
                self.game_logic = GameLogic((self.game_map.width, self.game_map.height))  
                self.game_logic.metrics_manager = self.metrics_manager
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
            self.metrics_detail_window = MetricsDetailWindow()

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
                AlgorithmType.DIJKSTRA: lambda: self._init_pathfinder(DijkstraPathfinder),
                AlgorithmType.ASTAR: lambda: self._init_pathfinder(AStarPathfinder),
                AlgorithmType.GBFS: lambda: self._init_pathfinder(GreedyBestFirstPathfinder),
                AlgorithmType.BFS: lambda: self._init_pathfinder(BFSPathfinder),
                AlgorithmType.QL: lambda: self._init_pathfinder(QLearningPathfinder),
                AlgorithmType.SARSA: lambda: self._init_pathfinder(SARSAPathfinder)
            }
        except Exception as e:
            print(f"Error setting up algorithms: {e}")
            raise
    
    def _init_pathfinder(self, pathfinder_class):  
        """Helper method to initialize pathfinder with game logic"""  
        pathfinder = pathfinder_class(self.game_map)  
        pathfinder.set_game_logic(self.game_logic)  
        return pathfinder

    def handle_events(self):  
        """Process game events"""  
        try:  
            for event in pygame.event.get():  
                if event.type == pygame.QUIT or (  
                    event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE  
                ):  
                    if self.metrics_detail_window.visible:
                        self.metrics_detail_window.hide()
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

                if event.type == pygame.MOUSEBUTTONDOWN:  
                    # Check if click was on a metric row  
                    for rect, algo_type in self.ui_manager.metric_click_areas:  
                        if rect.collidepoint(event.pos):  
                            metrics = self.metrics_manager.get_average_metrics(algo_type)  
                            if metrics:  
                                self.metrics_detail_window.show(
                                    algo_type, 
                                    metrics,
                                    (self.screen.get_width(), self.screen.get_height())
                                )  

                # Handle metrics window events  
                if self.metrics_detail_window.visible:  
                    if event.type == pygame.MOUSEBUTTONDOWN:  
                        close_rect = self.metrics_detail_window.draw()  
                        if close_rect and close_rect.collidepoint(event.pos):  
                            self.metrics_detail_window.hide()  
                    elif event.type == pygame.QUIT:  
                        self.metrics_detail_window.hide()

        except Exception as e:  
            print(f"Error handling events: {e}")  
            self.running = False

    def _handle_algorithm_selection(self, key):  
        """Handle algorithm selection based on key press"""  
        if key not in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7]:  
            return  

        # Clear previous algorithm path  
        if self.current_algorithm:  
            self.game_map.clear_algorithm_path(self.current_algorithm)  

        # Dictionary for algorithm mapping  
        algorithm_map = {  
            pygame.K_1: (AlgorithmType.MANUAL, None),  
            pygame.K_2: (AlgorithmType.ASTAR, self.pathfinders.get(AlgorithmType.ASTAR)),  
            pygame.K_3: (AlgorithmType.DIJKSTRA, self.pathfinders.get(AlgorithmType.DIJKSTRA)),
            pygame.K_4: (AlgorithmType.GBFS, self.pathfinders.get(AlgorithmType.GBFS)),
            pygame.K_5: (AlgorithmType.BFS, self.pathfinders.get(AlgorithmType.BFS)),              
            pygame.K_6: (AlgorithmType.QL, self.pathfinders.get(AlgorithmType.QL)),  
            pygame.K_7: (AlgorithmType.SARSA, self.pathfinders.get(AlgorithmType.SARSA))  
        }  

        if key in algorithm_map:  
            algo_type, pathfinder_creator = algorithm_map[key]  
            self.current_algorithm = algo_type  
            self.current_pathfinder = pathfinder_creator() if pathfinder_creator else None  

            # Start metrics tracking for the new algorithm  
            self.metrics_manager.start_run(self.current_algorithm)

            # Train reinforcement learning agents if selected
            if self.current_algorithm in [AlgorithmType.QL, AlgorithmType.SARSA] and self.current_pathfinder:
                algorithm_name = "Q-Learning" if self.current_algorithm == AlgorithmType.QL else "SARSA"
                print(f"Training {algorithm_name} agent...")
                
                self.current_pathfinder.train(
                    start=(self.robot.x, self.robot.y),
                    goal=self.game_map.goal_pos,
                )
                print(f"{algorithm_name} training completed!")

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
                self.current_algorithm,
                self.metrics_manager
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
                
                # Only process game updates if metrics window is not visible
                if not self.metrics_detail_window.visible:
                    self.handle_input()
                    self.update()
                    self.draw()
                else:
                    # Draw metrics window when it's visible
                    self.metrics_detail_window.draw()
                
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
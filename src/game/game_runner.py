import pygame
import sys
from typing import Dict, Callable, Optional, Tuple

from src.environment.map import Map
from src.environment.robot import Robot
from src.game.game_logic import GameLogic
from src.game.ui_manager import UIManager
from src.config.types import AlgorithmType, TestScenario
from src.config.constants import (
    GameState, 
    FPS, 
    COLORS, 
    UI_PANEL_WIDTH,
    TIME_LIMIT
)

class EventHandler:
    """Manages game events and input handling"""
    def __init__(self, game_state, map_instance, robot, pathfinders):
        self.game_state = game_state
        self.map = map_instance
        self.robot = robot
        self.pathfinders = pathfinders
        self.running = True
        self.current_algorithm = AlgorithmType.MANUAL
        self.current_pathfinder = None
        self.current_maze = TestScenario.DIAGONAL

    def handle_events(self) -> bool:
        """Process game events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                return False

            if event.type == pygame.KEYDOWN:
                # Add maze selection handling
                if self.game_state.state_manager.state == GameState.WAITING:
                    if event.key == pygame.K_F1:
                        self._switch_maze(TestScenario.DIAGONAL)
                    elif event.key == pygame.K_F2:
                        self._switch_maze(TestScenario.SNAKE)
                    elif event.key == pygame.K_F3:
                        self._switch_maze(TestScenario.OPEN)
                    elif event.key == pygame.K_F4:
                        self._switch_maze(TestScenario.BOTTLENECK)

                # Always allow reset
                if event.key == pygame.K_r:
                    return self._handle_reset()

                # Algorithm selection can happen in WAITING state
                if self.game_state.state_manager.state == GameState.WAITING:
                    if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7]:
                        self._handle_algorithm_selection(event.key)

        return True

    def _switch_maze(self, scenario: TestScenario):
        """Handle maze switching"""
        if self.map.change_maze(scenario):
            self.current_maze = scenario
            self.game_state.set_maze_type(scenario)
            self.robot.x = self.map.SPAWN_POS[0]
            self.robot.y = self.map.SPAWN_POS[1]
            for algo_type in AlgorithmType:
                self.map.clear_algorithm_path(algo_type)


    def handle_input(self):
        """Handle input based on current algorithm"""
        if self.game_state.state == GameState.PLAYING:
            if self.current_algorithm == AlgorithmType.MANUAL:
                self._handle_manual_input()
            else:
                self._handle_algorithm_input()

    def _handle_reset(self) -> bool:  
        """Handle game reset"""  
        # Reset map  
        self.map.load_map()  

        # Reset robot position  
        self.robot.x = self.map.SPAWN_POS[0]  
        self.robot.y = self.map.SPAWN_POS[1]  
        self.map.place_robot(self.robot.x, self.robot.y)  

        # Reset game state  
        self.game_state.reset()  
        self.game_state.state = GameState.WAITING  

        # Reset algorithm  
        self.current_algorithm = AlgorithmType.MANUAL  
        self.current_pathfinder = None  

        return True

    def _handle_algorithm_selection(self, key):
        """Handle algorithm selection"""
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

            # Clear previous algorithm path
            if self.current_algorithm:
                self.map.clear_algorithm_path(self.current_algorithm)

            # Set new algorithm
            self.current_algorithm = algo_type
            self.current_pathfinder = pathfinder_creator() if pathfinder_creator else None

            # Train reinforcement learning agents if needed
            if self.current_algorithm in [AlgorithmType.QL, AlgorithmType.SARSA] and self.current_pathfinder:
                self._train_reinforcement_agent()

            # Update game state
            if self.current_algorithm:  
                self.game_state.set_algorithm(self.current_algorithm)  
                self.game_state.state = GameState.PLAYING

    def _train_reinforcement_agent(self):
        """Train reinforcement learning agent"""
        algorithm_name = "Q-Learning" if self.current_algorithm == AlgorithmType.QL else "SARSA"
        print(f"Training {algorithm_name} agent...")

        self.current_pathfinder.train(
            start=(self.robot.x, self.robot.y),
            goal=self.map.goal_pos,
        )
        print(f"{algorithm_name} training completed!")

    def _handle_manual_input(self):
        """Handle keyboard input for manual control"""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_DOWN]:
            self.robot.move('down', self.map)
        elif keys[pygame.K_UP]:
            self.robot.move('up', self.map)
        elif keys[pygame.K_LEFT]:
            self.robot.move('left', self.map)
        elif keys[pygame.K_RIGHT]:
            self.robot.move('right', self.map)
        else:
            self.robot.move('idle', self.map)

    def _handle_algorithm_input(self):
        """Handle automated movement based on current algorithm"""
        if self.current_pathfinder:
            next_move = self.current_pathfinder.get_next_move(
                (self.robot.x, self.robot.y),
                self.map.goal_pos
            )
            self.robot.move(next_move, self.map)

class GameStateUpdater:
    """Manages game state updates"""
    def __init__(self, game_logic, map_instance, robot):
        self.game_logic = game_logic
        self.map = map_instance
        self.robot = robot

    def update(self):
        """Update game state"""
        if self.game_logic.state_manager.state == GameState.PLAYING:
            self.game_logic.update()
            if self.map.goal_pos:
                self.game_logic.check_win_condition(
                    (self.robot.x, self.robot.y),
                    self.map.goal_pos
                )

class GameRenderer:
    """Handles game rendering"""
    def __init__(self, screen, ui_manager, map_instance, robot):
        self.screen = screen
        self.ui_manager = ui_manager
        self.map = map_instance
        self.robot = robot

    def draw(self, game_logic, current_algorithm):
        """Render game elements"""
        # Create main surface with calculated dimensions
        window_width = UI_PANEL_WIDTH + self.map.screen_width
        window_height = self.map.screen_height
        main_surface = pygame.Surface((window_width, window_height))
        main_surface.fill(COLORS['WHITE'])

        # Draw map on the right side of the panel
        self.map.draw_map(main_surface, offset_x=UI_PANEL_WIDTH)
        self.robot.display(main_surface, offset_x=UI_PANEL_WIDTH)

        # Draw UI on the left panel
        self.ui_manager.draw_game_ui(
            main_surface,
            game_logic,
            current_algorithm
        )

        # Update display
        self.screen.blit(main_surface, (0, 0))
        pygame.display.flip()

        # Draw game state message  
        if game_logic.state_manager.state == GameState.WAITING:  
            # Modify this to use the new state management  
            pass

class GameRunner:
    """Main game runner class that handles game initialization and main loop"""
    def __init__(self):
        if not pygame.get_init():
            pygame.init()

        self.setup_initial_components()
        self.setup_remaining_components()

        # Create component managers
        self.event_handler = EventHandler(
            self.game_logic,  # This is now properly initialized
            self.game_map, 
            self.robot, 
            self.pathfinders
        )
        self.state_updater = GameStateUpdater(
            self.game_logic, 
            self.game_map, 
            self.robot
        )
        self.renderer = GameRenderer(
            self.screen, 
            self.ui_manager, 
            self.game_map, 
            self.robot
        )

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
            self.cleanup()
            sys.exit(1)

    def setup_remaining_components(self):
        """Initialize remaining game components"""
        try:
            self.ui_manager = UIManager()
            self.clock = pygame.time.Clock()
            self.game_logic = GameLogic((self.game_map.width, self.game_map.height))  
            self.game_logic.state_manager.state = GameState.WAITING

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

            # Initialize algorithm settings
            self.pathfinders = self.setup_algorithms()

        except Exception as e:
            print(f"Error during component setup: {e}")
            self.cleanup()
            sys.exit(1)
            
    def cleanup(self):
        """Clean up pygame resources"""
        try:
            if hasattr(self, 'game_logic'):
                self.game_logic.cleanup()
            pygame.quit()
        except Exception as e:
            print(f"Error during cleanup: {e}")

    def setup_algorithms(self) -> Dict[AlgorithmType, Callable]:
        """Initialize all pathfinding algorithms"""
        try:
            from src.algorithms.pathfinding.dijkstra import DijkstraPathfinder
            from src.algorithms.pathfinding.astar import AStarPathfinder
            from src.algorithms.pathfinding.greedy_best_first import GreedyBestFirstPathfinder
            from src.algorithms.pathfinding.breadth_first import BFSPathfinder
            from src.algorithms.reinforcement.q_learning import QLearningPathfinder
            from src.algorithms.reinforcement.sarsa import SARSAPathfinder

            return {
                AlgorithmType.DIJKSTRA: lambda: DijkstraPathfinder(self.game_map),
                AlgorithmType.ASTAR: lambda: AStarPathfinder(self.game_map),
                AlgorithmType.GBFS: lambda: GreedyBestFirstPathfinder(self.game_map),
                AlgorithmType.BFS: lambda: BFSPathfinder(self.game_map),
                AlgorithmType.QL: lambda: QLearningPathfinder(self.game_map),
                AlgorithmType.SARSA: lambda: SARSAPathfinder(self.game_map),
            }
        except Exception as e:
            print(f"Error setting up algorithms: {e}")
            raise
    
    def _init_pathfinder(self, pathfinder_class):  
        """Helper method to initialize pathfinder with game logic"""  
        pathfinder = pathfinder_class(self.game_map)  
        pathfinder.set_game_logic(self.game_logic)  
        return pathfinder

    def run(self):
        """Main game loop"""
        try:
            while self.event_handler.running:
                # Handle events and check if game should continue
                self.event_handler.running = self.event_handler.handle_events()

                # Handle input based on current algorithm
                self.event_handler.handle_input()

                # Update game state
                self.state_updater.update()

                # Render game
                self.renderer.draw(
                    self.game_logic, 
                    self.event_handler.current_algorithm
                )

                # Control frame rate
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
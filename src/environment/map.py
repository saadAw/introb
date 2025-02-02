import pygame  
from typing import Tuple 
from enum import Enum 

from src.config.constants import MapSymbols, COLORS, calculate_dimensions  
from src.environment.mazes.maze_data import LAYOUT  
from src.config.types import AlgorithmType, TestScenario
from src.environment.mazes.maze_data import (
    DIAGONAL_MAZE, DIAGONAL_MAZE_2, DIAGONAL_MAZE_3,
    SNAKE_MAZE, SNAKE_MAZE_2, SNAKE_MAZE_3,
    OPEN_MAZE, OPEN_MAZE_2, OPEN_MAZE_3,
    BOTTLENECK_MAZE, BOTTLENECK_MAZE_2, BOTTLENECK_MAZE_3
)


class Map:
    """Represents the game map with multiple layout variations"""    

    ALGORITHM_COLORS = {    
        AlgorithmType.MANUAL: COLORS['PATH_MANUAL'],    
        AlgorithmType.ASTAR: COLORS['PATH_ASTAR'],    
        AlgorithmType.DIJKSTRA: COLORS['PATH_DIJKSTRA'],
        AlgorithmType.GBFS: COLORS['PATH_GBFS'],
        AlgorithmType.BFS: COLORS['PATH_BFS'],
        AlgorithmType.QL: COLORS['PATH_QL'],    
        AlgorithmType.SARSA: COLORS['PATH_SARSA'],  
    }    
    PATH_SCALE = 0.6    

    def __init__(self, width: int, height: int):
        self.maze_layouts = {
            TestScenario.DIAGONAL: [DIAGONAL_MAZE, DIAGONAL_MAZE_2, DIAGONAL_MAZE_3],
            TestScenario.SNAKE: [SNAKE_MAZE, SNAKE_MAZE_2, SNAKE_MAZE_3],
            TestScenario.OPEN: [OPEN_MAZE, OPEN_MAZE_2, OPEN_MAZE_3],
            TestScenario.BOTTLENECK: [BOTTLENECK_MAZE, BOTTLENECK_MAZE_2, BOTTLENECK_MAZE_3]
        }
        
        self.current_scenario = TestScenario.DIAGONAL
        self.current_variation = 0
        self.current_layout = self.maze_layouts[self.current_scenario][self.current_variation]
        
        self.maze_height = len(self.current_layout)
        self.maze_width = len(self.current_layout[0]) if self.current_layout else 0
        
        dimensions = calculate_dimensions(self.maze_width, self.maze_height)
        
        self.width = dimensions['map_width']
        self.height = dimensions['map_height']
        self.cell_size = dimensions['cell_size']
        self.screen_width = self.width * self.cell_size
        self.screen_height = self.height * self.cell_size

        self.test_scenarios = {
            TestScenario.DIAGONAL: {
                'spawn': (1, self.height - 2),
                'goal': (self.width - 2, 1)
            },
            TestScenario.SNAKE: {
                'spawn': (1, self.height - 2),
                'goal': (self.width - 2, 1)
            },
            TestScenario.OPEN: {
                'spawn': (1, self.height - 2),
                'goal': (self.width - 2, 1)
            },
            TestScenario.BOTTLENECK: {
                'spawn': (1, self.height - 2),
                'goal': (self.width - 2, 1)
            }
        }

        self.SPAWN_POS = self.test_scenarios[self.current_scenario]['spawn']
        self.GOAL_POS = self.test_scenarios[self.current_scenario]['goal']
        self.OPTIMAL_PATH_LENGTH = max(self.width, self.height) * 2
        
        self.robot_pos = None
        self.goal_pos = None
        self.grid = [[MapSymbols.FREE for _ in range(self.width)] 
                    for _ in range(self.height)]
        self.algorithm_paths = {algo_type: set() for algo_type in AlgorithmType}
        self.path_grid = {}
        self.paths = {}
        
        self.load_map()

    def change_maze(self, scenario: TestScenario, next_variation: bool = False):
        """
        Change the current maze layout
        Args:
            scenario: The maze scenario to switch to
            next_variation: If True, cycle to next variation of current scenario
        """
        if scenario in self.maze_layouts:
            if next_variation:
                self.current_variation = (self.current_variation + 1) % len(self.maze_layouts[scenario])
            else:
                self.current_variation = 0
                
            self.current_scenario = scenario
            self.current_layout = self.maze_layouts[scenario][self.current_variation]
            
            self.SPAWN_POS = self.test_scenarios[scenario]['spawn']
            self.GOAL_POS = self.test_scenarios[scenario]['goal']
            
            self.load_map()
            return True
        return False

    def get_current_maze_info(self) -> str:
        """Get information about current maze variation"""
        return f"{self.current_scenario.name} - Variation {self.current_variation + 1}"


    def load_map(self) -> None:
        """Load the current map layout"""
        try:
            for y, row in enumerate(self.current_layout):
                for x, cell in enumerate(row):
                    self.grid[y][x] = MapSymbols.OBSTACLE if cell == 1 else MapSymbols.FREE
            
            if not self.is_valid_move(*self.SPAWN_POS):
                self.SPAWN_POS = self._find_valid_position(start_from_bottom=True)
            
            if not self.is_valid_move(*self.GOAL_POS):
                self.GOAL_POS = self._find_valid_position(start_from_bottom=False)
            
            self.place_robot(*self.SPAWN_POS)
            self.place_goal(*self.GOAL_POS)
            
        except Exception as e:
            print(f"Error loading maze: {e}")
            raise

    def _find_valid_position(self, start_from_bottom=True) -> Tuple[int, int]:
        """Find a valid position in the maze"""
        y_range = range(self.height - 1, -1, -1) if start_from_bottom else range(self.height)
        
        for y in y_range:
            for x in range(self.width):
                if self.is_valid_move(x, y):
                    return (x, y)
        
        raise Exception("No valid position found in maze")

    def place_robot(self, x: int, y: int) -> Tuple[int, int]:
        """Place robot at the specified position"""
        if self.robot_pos:
            old_x, old_y = self.robot_pos
            self.grid[old_y][old_x] = MapSymbols.FREE

        self.grid[y][x] = MapSymbols.ROBOT
        self.robot_pos = (x, y)
        return (x, y)

    def place_goal(self, x: int, y: int) -> None:
        """Place goal at the specified position"""
        if self.goal_pos:
            old_x, old_y = self.goal_pos
            self.grid[old_y][old_x] = MapSymbols.FREE

        self.grid[y][x] = MapSymbols.GOAL
        self.goal_pos = (x, y)

    def draw_map(self, surface, offset_x=0):    
        """Draw the map with all elements on given surface"""    
        self._draw_cells(surface, offset_x)    
        self._draw_grid(surface, offset_x)    

        for pos, algo_type in self.path_grid.items():  
            x, y = pos  
            color = self.ALGORITHM_COLORS[algo_type]  
            rect = pygame.Rect(  
                offset_x + x * self.cell_size,  
                y * self.cell_size,  
                self.cell_size,  
                self.cell_size  
            )  
            pygame.draw.rect(surface, color, rect.inflate(  
                -self.cell_size * self.PATH_SCALE,  
                -self.cell_size * self.PATH_SCALE  
            ))

    def _draw_cells(self, surface, offset_x=0):
        """Draw all cells (private helper method)"""
        for y in range(self.height):
            for x in range(self.width):
                cell_x = offset_x + x * self.cell_size
                cell_y = y * self.cell_size
                cell_rect = (cell_x, cell_y, self.cell_size, self.cell_size)
                
                cell_type = self.grid[y][x]
                color = {
                    MapSymbols.FREE: COLORS['WHITE'],
                    MapSymbols.OBSTACLE: COLORS['BLACK'],
                    MapSymbols.GOAL: COLORS['GREEN'],
                    MapSymbols.ROBOT: COLORS['RED']
                }.get(cell_type, COLORS['WHITE'])
                
                pygame.draw.rect(surface, color, cell_rect)

    def _draw_grid(self, surface, offset_x=0):
        """Draw grid lines (private helper method)"""
        for x in range(self.width + 1):
            start_pos = (offset_x + x * self.cell_size, 0)
            end_pos = (offset_x + x * self.cell_size, self.screen_height)
            pygame.draw.line(surface, COLORS['GRID'], start_pos, end_pos)

        for y in range(self.height + 1):
            start_pos = (offset_x, y * self.cell_size)
            end_pos = (offset_x + self.screen_width, y * self.cell_size)
            pygame.draw.line(surface, COLORS['GRID'], start_pos, end_pos)

    def is_valid_move(self, x: int, y: int) -> bool:
        """Check if position is valid for movement"""
        return (0 <= x < self.width and
                0 <= y < self.height and
                self.grid[y][x] != MapSymbols.OBSTACLE)
    
    def add_to_path(self, pos: Tuple[int, int], algorithm: AlgorithmType):  
        """Add position to algorithm's path and update path_grid"""  
        if algorithm not in self.paths:  
            self.paths[algorithm] = set()  

        self.paths[algorithm].add(pos)  
        self.path_grid[pos] = algorithm  

    def clear_algorithm_path(self, algorithm: AlgorithmType):  
        """Clear path for specific algorithm"""  
        if algorithm in self.paths:  
            positions_to_remove = []  
            for pos, algo in self.path_grid.items():  
                if algo == algorithm:  
                    positions_to_remove.append(pos)  

            for pos in positions_to_remove:  
                del self.path_grid[pos]  

            self.paths[algorithm].clear()
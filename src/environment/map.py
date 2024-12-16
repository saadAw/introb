import pygame
from typing import Tuple

from src.config.constants import MapSymbols, COLORS, calculate_dimensions
from src.environment.mazes.maze_data import LAYOUT

class Map:
    """Represents the game map with a single fixed layout"""
    
    def __init__(self, width: int, height: int):
        """Initialize map with given dimensions"""
        # Get maze dimensions from LAYOUT
        self.maze_height = len(LAYOUT)
        self.maze_width = len(LAYOUT[0]) if LAYOUT else 0
        
        print(f"Maze dimensions: {self.maze_width}x{self.maze_height}")
        
        # Calculate appropriate dimensions
        dimensions = calculate_dimensions(self.maze_width, self.maze_height)
        
        # Set class attributes
        self.width = dimensions['map_width']
        self.height = dimensions['map_height']
        self.cell_size = dimensions['cell_size']
        self.screen_width = self.width * self.cell_size
        self.screen_height = self.height * self.cell_size
        
        # Set spawn and goal positions 
        self.SPAWN_POS = (1, self.height - 2) # near bottom left
        self.GOAL_POS = (self.width - 2, 1) # near top right
        self.OPTIMAL_PATH_LENGTH = max(self.width, self.height) * 2
        
        # Initialize positions
        self.robot_pos = None
        self.goal_pos = None
        
        # Initialize the grid
        self.grid = [[MapSymbols.FREE for _ in range(self.width)] 
                    for _ in range(self.height)]
        
        self.load_map()

    def load_map(self) -> None:
        """Load the fixed map layout"""
        try:
            for y, row in enumerate(LAYOUT):
                for x, cell in enumerate(row):
                    self.grid[y][x] = MapSymbols.OBSTACLE if cell == 1 else MapSymbols.FREE
            
            # Find valid spawn and goal positions
            if not self.is_valid_move(*self.SPAWN_POS):
                self.SPAWN_POS = self._find_valid_position(start_from_bottom=True)
            
            if not self.is_valid_move(*self.GOAL_POS):
                self.GOAL_POS = self._find_valid_position(start_from_bottom=False)
            
            # Place robot and goal
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
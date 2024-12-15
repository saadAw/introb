from src.environment.constants import MapSymbols, CELL_SIZE, COLORS
import pygame
from typing import Dict, List, Tuple

from src.environment.constants import MapSymbols, CELL_SIZE, COLORS
import pygame
from typing import Tuple

class Map:
    """Represents the game map with a single fixed layout"""
    
    # Single fixed layout (0=free, 1=obstacle)
    LAYOUT = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 0, 0, 0, 0, 1, 1, 0],
        [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
        [0, 0, 1, 1, 1, 1, 1, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 1, 0, 0, 1, 1, 1, 0],
        [0, 0, 0, 1, 0, 0, 1, 0, 0, 0],
        [0, 1, 0, 0, 0, 0, 0, 0, 1, 0],
        [0, 1, 1, 1, 0, 0, 1, 1, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ]

    # Fixed positions
    SPAWN_POS = (5, 9)  # Middle bottom
    GOAL_POS = (4, 0)   # Near top middle
    OPTIMAL_PATH_LENGTH = 13  # Shortest possible path length

    def __init__(self, width: int, height: int):
        """Initialize map with given dimensions"""
        self.width = width
        self.height = height
        self.cell_size = CELL_SIZE
        self.screen_width = self.width * self.cell_size
        self.screen_height = self.height * self.cell_size
        self.robot_pos = None
        self.goal_pos = None
        self.load_map()

    def load_map(self) -> None:
        """Load the fixed map layout"""
        # Load grid from layout
        self.grid = [[MapSymbols.FREE for _ in range(self.width)] for _ in range(self.height)]
        for y, row in enumerate(self.LAYOUT):
            for x, cell in enumerate(row):
                self.grid[y][x] = MapSymbols.OBSTACLE if cell == 1 else MapSymbols.FREE

        # Set initial positions
        self.place_robot(*self.SPAWN_POS)
        self.place_goal(*self.GOAL_POS)

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

    def draw_map(self, surface: pygame.Surface) -> None:
        """Draw the map with all elements on given surface"""
        self._draw_cells(surface)
        self._draw_grid(surface)

    def _draw_cells(self, surface: pygame.Surface) -> None:
        """Draw all cells (private helper method)"""
        for y in range(self.height):
            for x in range(self.width):
                cell_x = x * self.cell_size
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

    def _draw_grid(self, surface: pygame.Surface) -> None:
        """Draw grid lines (private helper method)"""
        for x in range(self.width + 1):
            start_pos = (x * self.cell_size, 0)
            end_pos = (x * self.cell_size, self.screen_height)
            pygame.draw.line(surface, COLORS['GRID'], start_pos, end_pos)

        for y in range(self.height + 1):
            start_pos = (0, y * self.cell_size)
            end_pos = (self.screen_width, y * self.cell_size)
            pygame.draw.line(surface, COLORS['GRID'], start_pos, end_pos)

    def is_valid_move(self, x: int, y: int) -> bool:
        """Check if position is valid for movement"""
        return (0 <= x < self.width and
                0 <= y < self.height and
                self.grid[y][x] != MapSymbols.OBSTACLE)
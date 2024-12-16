from config.constants import MapSymbols, CELL_SIZE, COLORS
import random
import pygame
from collections import deque
from typing import Optional, Set, Tuple

class Map:
    """Represents the game map with obstacles, robot, and goal positions"""
    
    MIN_GOAL_DISTANCE = 6  # Minimum Manhattan distance between spawn and goal
    
    def __init__(self, width: int, height: int):
        """Initialize map with given dimensions"""
        self.width = width
        self.height = height
        self.grid = [[MapSymbols.FREE for _ in range(width)] for _ in range(height)]
        self.cell_size = CELL_SIZE
        self.screen_width = self.width * self.cell_size
        self.screen_height = self.height * self.cell_size
        self.robot_pos = None
        self.goal_pos = None

    def add_obstacles(self, num_obstacles: int) -> None:
        """Add random obstacles to the map ensuring path exists to goal"""
        attempts = 0
        obstacles_added = 0
        max_attempts = num_obstacles * 10  # Prevent infinite loops
        
        while obstacles_added < num_obstacles and attempts < max_attempts:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            
            # Don't place near spawn point
            if abs(x - 5) + abs(y - 9) <= 1:  # Assuming spawn at (5,9)
                continue
                
            if self.grid[y][x] == MapSymbols.FREE:
                # Temporarily add obstacle
                self.grid[y][x] = MapSymbols.OBSTACLE
                
                # If goal exists, check if it's still reachable
                if self.goal_pos and not self._path_exists((5, 9), self.goal_pos):
                    self.grid[y][x] = MapSymbols.FREE  # Revert obstacle
                else:
                    obstacles_added += 1
                    
            attempts += 1

    def _path_exists(self, start: Tuple[int, int], end: Tuple[int, int]) -> bool:
        """Check if a path exists between start and end positions using BFS"""
        if start == end:
            return True
            
        queue = deque([start])
        visited = {start}
        
        while queue:
            x, y = queue.popleft()
            
            # Check all adjacent cells
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                new_x, new_y = x + dx, y + dy
                
                if ((new_x, new_y) not in visited and 
                    self.is_valid_move(new_x, new_y)):
                    if (new_x, new_y) == end:
                        return True
                    queue.append((new_x, new_y))
                    visited.add((new_x, new_y))
                    
        return False

    def _get_valid_goal_positions(self, spawn_pos: Tuple[int, int]) -> Set[Tuple[int, int]]:
        """Get all valid goal positions with minimum distance from spawn"""
        valid_positions = set()
        
        for y in range(self.height):
            for x in range(self.width):
                # Check if position is free and far enough from spawn
                manhattan_dist = abs(x - spawn_pos[0]) + abs(y - spawn_pos[1])
                if (self.grid[y][x] == MapSymbols.FREE and 
                    manhattan_dist >= self.MIN_GOAL_DISTANCE):
                    valid_positions.add((x, y))
                    
        return valid_positions

    def place_goal(self, x: int, y: int) -> None:
        """Place goal on the map ensuring minimum distance from spawn"""
        spawn_pos = (5, 9)  # Default spawn position
        
        # Clear old goal
        if self.goal_pos:
            old_x, old_y = self.goal_pos
            self.grid[old_y][old_x] = MapSymbols.FREE

        # Get valid positions
        valid_positions = self._get_valid_goal_positions(spawn_pos)
        
        # Filter for positions with valid paths
        reachable_positions = {
            pos for pos in valid_positions 
            if self._path_exists(spawn_pos, pos)
        }
        
        if not reachable_positions:
            raise ValueError("No valid and reachable goal position found!")
            
        # If provided position is valid, use it
        if (x, y) in reachable_positions:
            goal_pos = (x, y)
        else:
            # Otherwise choose random valid position
            goal_pos = random.choice(list(reachable_positions))
            
        self.grid[goal_pos[1]][goal_pos[0]] = MapSymbols.GOAL
        self.goal_pos = goal_pos

    def place_robot(self, x: int = 0, y: int = 0) -> tuple[int, int]:
        """Place robot on the map, returns final position"""
        # Clear old position
        if self.robot_pos:
            old_x, old_y = self.robot_pos
            self.grid[old_y][old_x] = MapSymbols.FREE

        # Try to place at requested position
        if self.is_valid_move(x, y):
            self.grid[y][x] = MapSymbols.ROBOT
            self.robot_pos = (x, y)
            return x, y

        # Find first available position if requested is invalid
        for i in range(self.height):
            for j in range(self.width):
                if self.grid[i][j] == MapSymbols.FREE:
                    self.grid[i][j] = MapSymbols.ROBOT
                    self.robot_pos = (j, i)
                    return j, i

        raise ValueError("No free position found for robot!")

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

                # Draw appropriate color based on cell type
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
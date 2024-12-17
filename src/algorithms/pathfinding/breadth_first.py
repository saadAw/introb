from typing import Dict, List, Optional, Tuple, Set
from collections import deque
from src.config.constants import MapSymbols

class BFSPathfinder:
    def __init__(self, game_map):
        self.game_map = game_map
        self.width = game_map.width
        self.height = game_map.height
        
    def get_neighbors(self, pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Get valid neighboring positions"""
        x, y = pos
        possible_neighbors = [
            (x+1, y), (x-1, y),  # right, left
            (x, y+1), (x, y-1)   # down, up
        ]
        return [(nx, ny) for nx, ny in possible_neighbors 
                if 0 <= nx < self.width and 0 <= ny < self.height 
                and self.game_map.grid[ny][nx] != MapSymbols.OBSTACLE]
    
    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int]) -> Tuple[List[Tuple[int, int]], int]:
        """
        Find shortest path using Breadth-First Search
        Returns: (path, steps) where path is list of positions and steps is total moves
        """
        if not (self.game_map.is_valid_move(*start) and self.game_map.is_valid_move(*goal)):
            return [], float('inf')
            
        # Use deque for efficient queue operations
        queue = deque([start])
        # Track visited positions and their predecessors
        came_from = {start: None}
        # Track visited positions to avoid cycles
        visited = set([start])
        
        while queue:
            current_pos = queue.popleft()
            
            if current_pos == goal:
                break
                
            # Examine all neighbors in order (maintains shortest path property)
            for next_pos in self.get_neighbors(current_pos):
                if next_pos not in visited:
                    queue.append(next_pos)
                    visited.add(next_pos)
                    came_from[next_pos] = current_pos
        
        # No path found if goal wasn't reached
        if goal not in came_from:
            return [], float('inf')
            
        # Reconstruct path
        path = []
        current_pos = goal
        steps = 0  # Count steps to measure path length
        while current_pos is not None:
            path.append(current_pos)
            if current_pos != start:
                steps += 1
            current_pos = came_from[current_pos]
        path.reverse()
        
        return path, steps
        
    def get_next_move(self, current_pos: Tuple[int, int], goal_pos: Tuple[int, int]) -> str:
        """Get the next move direction based on the optimal path"""
        path, _ = self.find_path(current_pos, goal_pos)
        
        if len(path) < 2:
            return 'idle'
            
        current_x, current_y = path[0]
        next_x, next_y = path[1]
        
        dx = next_x - current_x
        dy = next_y - current_y
        
        if dx > 0:
            return 'right'
        elif dx < 0:
            return 'left'
        elif dy > 0:
            return 'down'
        elif dy < 0:
            return 'up'
        
        return 'idle'
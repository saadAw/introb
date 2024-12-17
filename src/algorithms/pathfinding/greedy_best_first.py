from typing import Dict, List, Optional, Tuple, Set
import heapq
from src.config.constants import MapSymbols

class GreedyBestFirstPathfinder:
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
    
    def calculate_heuristic(self, current_pos: Tuple[int, int], goal_pos: Tuple[int, int]) -> float:
        """Calculate Manhattan distance to goal"""
        x1, y1 = current_pos
        x2, y2 = goal_pos
        return abs(x1 - x2) + abs(y1 - y2)
        
    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int]) -> Tuple[List[Tuple[int, int]], float]:
        """
        Find path using Greedy Best-First Search
        Only considers distance to goal, ignoring path cost
        """
        if not (self.game_map.is_valid_move(*start) and self.game_map.is_valid_move(*goal)):
            return [], float('inf')

        # Queue entries are (heuristic, position)
        # Note: We only use heuristic for priority, unlike A* which uses f = g + h
        queue = [(self.calculate_heuristic(start, goal), start)]
        came_from = {start: None}
        visited = set()

        while queue:
            _, current_pos = heapq.heappop(queue)
            
            if current_pos == goal:
                break
                
            if current_pos in visited:
                continue
                
            visited.add(current_pos)
            
            # Sort neighbors by heuristic value
            neighbors = self.get_neighbors(current_pos)
            neighbors_with_costs = [
                (self.calculate_heuristic(next_pos, goal), next_pos)
                for next_pos in neighbors
            ]
            neighbors_with_costs.sort()  # Sort by heuristic value
            
            # Add neighbors to queue in order of increasing distance to goal
            for _, next_pos in neighbors_with_costs:
                if next_pos not in visited and next_pos not in came_from:
                    came_from[next_pos] = current_pos
                    heapq.heappush(queue, (self.calculate_heuristic(next_pos, goal), next_pos))

        if goal not in came_from:
            return [], float('inf')

        # Reconstruct path
        path = []
        current_pos = goal
        path_cost = 0  # Count steps to measure actual path length
        while current_pos is not None:
            path.append(current_pos)
            if current_pos != start:
                path_cost += 1
            current_pos = came_from[current_pos]
        path.reverse()

        return path, path_cost
        
    def get_next_move(self, current_pos: Tuple[int, int], goal_pos: Tuple[int, int]) -> str:
        """Get the next move direction based on the found path"""
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
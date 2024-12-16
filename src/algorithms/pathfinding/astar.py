from typing import Dict, List, Optional, Tuple, Set
import heapq
from src.config.constants import MapSymbols

class AStarPathfinder:
    '''Basic structure adopted from Dijkstra (Constructor, get_neighbors)'''
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
    
    def calculate_heuristic(self, current_pos: Tuple[int, int], goal_pos: Tuple[int, int]) -> int:
        """
        Estimates distance between current position and goal position using Manhattan distance
        Returns: Integer representing the estimated distance
        """
        x1 = current_pos[0]
        y1 = current_pos[1]
        x2 = goal_pos[0]
        y2 = goal_pos[1]

        return abs(x1-x2) + abs(y1-y2)

    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int]) -> Tuple[List[Tuple[int, int]], float]:
        """
        Find shortest path using A* algorithm
        Returns:
            Tuple containing:
            - List of positions representing the path from start to goal
            - Total cost of the path (float('inf') if no path exists)
        """
        # Validate start and goal positions
        if not (self.game_map.is_valid_move(*start) and self.game_map.is_valid_move(*goal)):
            return [], float('inf')

        # Initialize data structures
        # Queue entries are tuples of (f_cost, position) where f_cost = g_cost + heuristic
        queue: List[Tuple[float, Tuple[int, int]]] = [(self.calculate_heuristic(start, goal), start)]

        # Maps positions to their predecessor in the optimal path
        came_from: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {start: None}

        # Maps positions to their g_cost (actual distance from start)
        g_costs: Dict[Tuple[int, int], float] = {start: 0}

        # Keeps track of processed positions to avoid cycles
        visited: Set[Tuple[int, int]] = set()

        while queue:
            # Get position with lowest f_cost from queue
            _, current_pos = heapq.heappop(queue)

            # Path found if we reached the goal
            if current_pos == goal:
                break

            # Skip if position was already processed
            if current_pos in visited:
                continue

            visited.add(current_pos)

            # Examine all valid neighboring positions
            for next_pos in self.get_neighbors(current_pos):
                # Calculate new g_cost for reaching next_pos through current_pos
                new_g_cost = g_costs[current_pos] + 1  # Cost of 1 for each step

                # Update position if we found a better path to it
                if next_pos not in g_costs or new_g_cost < g_costs[next_pos]:
                    g_costs[next_pos] = new_g_cost
                    # Calculate f_cost = g_cost + heuristic for priority queue
                    f_cost = new_g_cost + self.calculate_heuristic(next_pos, goal)
                    came_from[next_pos] = current_pos
                    heapq.heappush(queue, (f_cost, next_pos))

        # No path found if goal wasn't reached
        if goal not in came_from:
            return [], float('inf')

        # Reconstruct path by walking backwards from goal to start
        path: List[Tuple[int, int]] = []
        current_pos = goal
        while current_pos is not None:
            path.append(current_pos)
            current_pos = came_from[current_pos]
        path.reverse()

        return path, g_costs[goal]

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
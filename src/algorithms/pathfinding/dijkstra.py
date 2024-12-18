from typing import Dict, List, Tuple, Set
import heapq
from src.config.constants import MapSymbols

class DijkstraPathfinder:
    def __init__(self, game_map):
        self.game_map = game_map
        self.width = game_map.width
        self.height = game_map.height
        self.game_logic = None  # Added game_logic reference

    def set_game_logic(self, game_logic):  
        """Set reference to game logic for metrics tracking"""  
        self.game_logic = game_logic

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

    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int]) -> Tuple[List[Tuple[int, int]], float]:
        """
        Find shortest path using Dijkstra's algorithm
        Returns: (path, cost) where path is list of positions and cost is total distance
        """
        if not (self.game_map.is_valid_move(*start) and self.game_map.is_valid_move(*goal)):
            return [], float('inf')

        # Priority queue of (distance, position)
        queue: List[Tuple[int, Tuple[int, int]]] = [(0, start)]
        # Dictionary of position -> previous position for path reconstruction
        came_from: Dict[Tuple[int, int], Tuple[int, int]] = {start: None}
        # Dictionary of position -> current shortest distance
        cost_so_far: Dict[Tuple[int, int], int] = {start: 0}
        # Set of visited positions
        visited: Set[Tuple[int, int]] = set()

        # Increment node count for start position
        if self.game_logic:
            self.game_logic.increment_nodes_explored()

        while queue:
            current_cost, current_pos = heapq.heappop(queue)

            if current_pos == goal:
                break

            if current_pos in visited:
                continue

            visited.add(current_pos)

            # Increment node count for each newly visited position
            if self.game_logic:
                self.game_logic.increment_nodes_explored()

            for next_pos in self.get_neighbors(current_pos):
                new_cost = cost_so_far[current_pos] + 1  # Cost of 1 for each step

                if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                    cost_so_far[next_pos] = new_cost
                    came_from[next_pos] = current_pos
                    heapq.heappush(queue, (new_cost, next_pos))

                    # Increment node count for each newly discovered position
                    if self.game_logic and next_pos not in visited:
                        self.game_logic.increment_nodes_explored()

        # Reconstruct path
        if goal not in came_from:
            return [], float('inf')

        path = []
        current_pos = goal
        while current_pos is not None:
            path.append(current_pos)
            current_pos = came_from[current_pos]
        path.reverse()

        return path, cost_so_far[goal]

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
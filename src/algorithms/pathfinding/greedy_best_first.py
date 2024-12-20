from typing import Dict, List, Optional, Tuple, Set
import heapq
from src.config.constants import MapSymbols

class GreedyBestFirstPathfinder:
    """
    Implementation of Greedy Best-First Search pathfinding algorithm.
    Uses heuristic to find path, ignoring actual path costs.
    """

    def __init__(self, game_map):
        """
        Initialize the pathfinder with a game map.
        """
        self.game_map = game_map
        self.width = game_map.width
        self.height = game_map.height
        self.game_logic = None

    def set_game_logic(self, game_logic):
        """
        Set reference to game logic

        """
        self.game_logic = game_logic

    def get_neighbors(self, pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Get valid neighboring positions.

        """
        x, y = pos
        possible_neighbors = [
            (x+1, y), (x-1, y),  # right, left
            (x, y+1), (x, y-1)   # down, up
        ]
        return [(nx, ny) for nx, ny in possible_neighbors 
                if 0 <= nx < self.width and 0 <= ny < self.height 
                and self.game_map.grid[ny][nx] != MapSymbols.OBSTACLE]

    def calculate_heuristic(self, current_pos: Tuple[int, int], goal_pos: Tuple[int, int]) -> float:
        """
        Calculate Manhattan distance to goal.

        """
        x1, y1 = current_pos
        x2, y2 = goal_pos
        return abs(x1 - x2) + abs(y1 - y2)

    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int]) -> Tuple[List[Tuple[int, int]], float]:
        """
        Find path using Greedy Best-First Search.
        Only considers distance to goal, ignoring path cost.

        """
        if not (self.game_map.is_valid_move(*start) and self.game_map.is_valid_move(*goal)):
            return [], float('inf')

        queue = [(self.calculate_heuristic(start, goal), start)]
        came_from = {start: None}
        visited = set()

        # Increment counter for start node
        if self.game_logic:
            self.game_logic.increment_nodes_explored()
            visited.add(start)

        while queue:
            _, current_pos = heapq.heappop(queue)

            if current_pos == goal:
                break

            if current_pos != start and current_pos in visited:
                continue

            # Increment counter for each new node explored
            if current_pos not in visited:
                visited.add(current_pos)
                if self.game_logic:
                    self.game_logic.increment_nodes_explored()

            neighbors = self.get_neighbors(current_pos)
            neighbors_with_costs = [
                (self.calculate_heuristic(next_pos, goal), next_pos)
                for next_pos in neighbors
                if next_pos not in visited
            ]
            neighbors_with_costs.sort()

            for _, next_pos in neighbors_with_costs:
                if next_pos not in visited and next_pos not in came_from:
                    came_from[next_pos] = current_pos
                    heapq.heappush(queue, (self.calculate_heuristic(next_pos, goal), next_pos))

        if goal not in came_from:
            return [], float('inf')

        path = []
        current_pos = goal
        path_cost = 0
        while current_pos is not None:
            path.append(current_pos)
            if current_pos != start:
                path_cost += 1
            current_pos = came_from[current_pos]
        path.reverse()

        return path, path_cost

    def get_next_move(self, current_pos: Tuple[int, int], goal_pos: Tuple[int, int]) -> str:
        """
        Get the next move direction based on the found path.

        """
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
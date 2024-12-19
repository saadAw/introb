from typing import Dict, List, Optional, Tuple, Set
from collections import deque
from src.config.constants import MapSymbols

class BFSPathfinder:
    """
    Implementation of Breadth-First Search pathfinding algorithm.
    Finds the shortest path between two points on a 2D grid.
    """

    def __init__(self, game_map):
        """
        Initialize the pathfinder with a game map.

        Args:
            game_map: The game map object containing the grid and dimensions
        """
        self.game_map = game_map
        self.width = game_map.width
        self.height = game_map.height
        self.game_logic = None

    def set_game_logic(self, game_logic):
        """
        Set reference to game logic for metrics tracking.

        Args:
            game_logic: GameLogic instance for tracking metrics
        """
        self.game_logic = game_logic

    def get_neighbors(self, pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Get valid neighboring positions.

        Args:
            pos: Current position tuple (x, y)

        Returns:
            List of valid neighboring position tuples
        """
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
        Find shortest path using Breadth-First Search.

        Args:
            start: Starting position tuple (x, y)
            goal: Goal position tuple (x, y)

        Returns:
            Tuple containing:
            - List of positions forming the path
            - Total number of steps in the path
        """
        if not (self.game_map.is_valid_move(*start) and self.game_map.is_valid_move(*goal)):
            return [], float('inf')

        queue = deque([start])
        came_from = {start: None}
        visited = set([start])

        # Increment counter for start node
        if self.game_logic:
            self.game_logic.increment_nodes_explored()

        while queue:
            current_pos = queue.popleft()

            if current_pos == goal:
                break

            for next_pos in self.get_neighbors(current_pos):
                if next_pos not in visited:
                    queue.append(next_pos)
                    visited.add(next_pos)
                    came_from[next_pos] = current_pos
                    # Increment counter for each new node explored
                    if self.game_logic:
                        self.game_logic.increment_nodes_explored()

        if goal not in came_from:
            return [], float('inf')

        path = []
        current_pos = goal
        steps = 0
        while current_pos is not None:
            path.append(current_pos)
            if current_pos != start:
                steps += 1
            current_pos = came_from[current_pos]
        path.reverse()

        return path, steps

    def get_next_move(self, current_pos: Tuple[int, int], goal_pos: Tuple[int, int]) -> str:
        """
        Get the next move direction based on the optimal path.

        Args:
            current_pos: Current position tuple (x, y)
            goal_pos: Goal position tuple (x, y)

        Returns:
            String indicating the next move direction ('up', 'down', 'left', 'right', or 'idle')
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
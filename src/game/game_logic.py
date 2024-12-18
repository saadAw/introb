import pygame  
from src.config.constants import GameState, TIME_LIMIT, FPS, COLORS  
from src.config.types import AlgorithmType
from time import time  # Add this import

class GameLogic:  
    """Handles game logic, scoring, and UI elements"""  
    def __init__(self, map_size=(10, 10)):  
        self.state = GameState.PLAYING  
        self.time_remaining = TIME_LIMIT * FPS  
        self.score = 0  
        self.map_size = map_size  
        self.moves_made = 0  
        self.optimal_path_length = 13  
        self.current_algorithm = None    
        self.used_algorithms = set()
        self.metrics_manager = None  # Add this line
        self.algorithm_start_time = None  # Add this line
        self.nodes_explored = 0  # Add this line to track explored nodes

    def update(self):
        """Updates game state including time"""
        if self.state == GameState.PLAYING:
            self.time_remaining -= 1
            if self.time_remaining <= 0:
                self.state = GameState.LOSE
                if self.metrics_manager and self.current_algorithm:
                    self._update_metrics(success=False)

    def check_win_condition(self, robot_pos, goal_pos):
        """Checks if robot has reached the goal"""
        if robot_pos == goal_pos:
            self.state = GameState.WIN
            time_bonus = max(self.time_remaining // FPS, 0)
            efficiency_bonus = max(0, self.optimal_path_length - self.moves_made) * 10
            self.score += time_bonus + efficiency_bonus

            # Update metrics on win
            if self.metrics_manager and self.current_algorithm:
                self._update_metrics(success=True)

    def _update_metrics(self, success: bool):
        """Helper method to update metrics"""
        if self.current_algorithm in self.metrics_manager.current_run:
            metrics = self.metrics_manager.current_run[self.current_algorithm]
            metrics.path_length = self.moves_made
            metrics.path_cost = self.score
            metrics.nodes_explored = self.nodes_explored
            self.metrics_manager.end_run(self.current_algorithm, success)

    def reset(self):
        """Resets game state"""
        self.state = GameState.PLAYING
        self.time_remaining = TIME_LIMIT * FPS
        self.score = 0
        self.moves_made = 0
        self.nodes_explored = 0
        self.algorithm_start_time = None

    def calculate_reward(self, old_pos, new_pos, goal_pos):
        """Calculates reward for an action"""
        self.moves_made += 1

        # Check if game is over
        if new_pos == goal_pos:
            efficiency_bonus = max(0, self.optimal_path_length - self.moves_made)
            return 100 + efficiency_bonus * 10
        elif self.time_remaining <= 0:
            return -100

        # Calculate distance-based reward
        old_distance = abs(old_pos[0] - goal_pos[0]) + abs(old_pos[1] - goal_pos[1])
        new_distance = abs(new_pos[0] - goal_pos[0]) + abs(new_pos[1] - goal_pos[1])

        if new_distance < old_distance:
            return 1
        elif new_distance > old_distance:
            return -1

        return -0.1

    def set_algorithm(self, algorithm: AlgorithmType):  
        """Set current algorithm and start metrics tracking"""
        self.current_algorithm = algorithm  
        self.used_algorithms.add(algorithm)
        self.algorithm_start_time = time()
        self.nodes_explored = 0

        # Start metrics tracking for new algorithm
        if self.metrics_manager:
            self.metrics_manager.start_run(algorithm)

    def increment_nodes_explored(self):
        """Increment the count of explored nodes"""
        self.nodes_explored += 1
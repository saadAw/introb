import pygame  
from src.config.constants import GameState, TIME_LIMIT, FPS, COLORS  
from src.config.types import AlgorithmType
  
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

    def update(self):
        """Updates game state including time"""
        if self.state == GameState.PLAYING:
            self.time_remaining -= 1
            if self.time_remaining <= 0:
                self.state = GameState.LOSE

    def check_win_condition(self, robot_pos, goal_pos):
        """Checks if robot has reached the goal"""
        if robot_pos == goal_pos:
            self.state = GameState.WIN
            time_bonus = max(self.time_remaining // FPS, 0)
            efficiency_bonus = max(0, self.optimal_path_length - self.moves_made) * 10
            self.score += time_bonus + efficiency_bonus

    def reset(self):
        """Resets game state"""
        self.state = GameState.PLAYING
        self.time_remaining = TIME_LIMIT * FPS
        self.score = 0
        self.moves_made = 0

    def calculate_reward(self, old_pos, new_pos, goal_pos):
        """Calculates reward for an action"""
        self.moves_made += 1
        
        # Check if game is over
        if new_pos == goal_pos:
            efficiency_bonus = max(0, self.optimal_path_length - self.moves_made)
            return 100 + efficiency_bonus * 10  # Large positive reward for reaching goal
        elif self.time_remaining <= 0:
            return -100  # Large negative reward for running out of time
            
        # Calculate distance-based reward
        old_distance = abs(old_pos[0] - goal_pos[0]) + abs(old_pos[1] - goal_pos[1])
        new_distance = abs(new_pos[0] - goal_pos[0]) + abs(new_pos[1] - goal_pos[1])
        
        if new_distance < old_distance:
            return 1  # Small positive reward for moving closer
        elif new_distance > old_distance:
            return -1  # Small negative reward for moving away
        
        return -0.1  # Tiny negative reward for each step to encourage efficiency

    def set_algorithm(self, algorithm: AlgorithmType):  
        self.current_algorithm = algorithm  
        self.used_algorithms.add(algorithm)
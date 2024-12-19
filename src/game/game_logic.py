import math
import pygame
from typing import Tuple, Callable
from src.config.constants import GameState, TIME_LIMIT, FPS, COLORS
from src.config.types import AlgorithmType, TestScenario
from src.game.metrics_manager import MetricsManager
from datetime import datetime

class GameStateManager:
    """Manages game state and transitions"""
    def __init__(self, initial_state: GameState = GameState.WAITING):  
        self.state = initial_state  

    def reset(self, initial_state: GameState = GameState.WAITING):  
        """Reset game state"""  
        self.state = initial_state  
        return self.state  

    def update(self, condition: bool = False):  
        """Update game state based on conditions"""  
        if condition:  
            self.state = GameState.WIN  
        return self.state

class ScoreManager:
    """Handles scoring logic"""  
    def __init__(self, optimal_path_length: int = 13):  
        self.score = 0  
        self.moves_made = 0  
        self.optimal_path_length = optimal_path_length  
        self.nodes_explored = 0

    def calculate_score(self, time_taken: float, nodes_explored: int, path_length: int) -> float:
        """  
        Calculate a normalized score (0-100) based on path efficiency, exploration, and time  
        """  
        # Weights  
        PATH_WEIGHT = 0.65       # Slightly increased  
        EXPLORATION_WEIGHT = 0.25 # Same  
        TIME_WEIGHT = 0.10       # Slightly decreased  

        # 1. Path Efficiency Score (with stronger exponential penalty)  
        path_ratio = self.optimal_path_length / max(path_length, 1)  
        path_score = min(100 * (path_ratio ** 3.5), 100)  # Increased exponent from 3 to 3.5  

        # Rest remains the same  
        nodes_per_step = nodes_explored / max(path_length, 1)  
        exploration_score = max(0, 100 - 15 * math.log10(nodes_per_step))  
        time_score = max(0, 100 - 15 * math.log10(max(time_taken, 0.1)))  

        final_score = (  
            PATH_WEIGHT * path_score +  
            EXPLORATION_WEIGHT * exploration_score +  
            TIME_WEIGHT * time_score  
        )  

        return round(final_score, 2)
    

    def _update_metrics(self, success: bool):
        """Helper method to update metrics"""
        if self.current_algorithm in self.metrics_manager.current_run:
            metrics = self.metrics_manager.current_run[self.current_algorithm]
            metrics.path_length = self.moves_made
            metrics.path_cost = self.score
            metrics.nodes_explored = self.nodes_explored
            self.metrics_manager.end_run(self.current_algorithm, success)
            # Update metrics on win
            if self.metrics_manager and self.current_algorithm:
                self._update_metrics(success=True)

    def reset(self):
        """Reset score and moves"""
        self.score = 0
        self.moves_made = 0
        self.nodes_explored = 0
        self.algorithm_start_time = None

class TimeManager:  
    def __init__(self, total_time):  
        """  
        Initialize time manager  

        :param total_time: Total time in seconds  
        """  
        self.total_time = total_time  
        self.time_remaining = total_time * FPS  # Convert to frames  
        self.frame_count = 0  

    def update(self):  
        """Decrement time remaining"""  
        if self.time_remaining > 0:  
            self.frame_count += 1  
            if self.frame_count >= FPS:  # Decrement every second  
                self.time_remaining -= FPS  
                self.frame_count = 0  

    def is_time_expired(self):  
        """  
        Check if time has expired  

        :return: True if time is expired, False otherwise  
        """  
        return self.time_remaining <= 0  

    def reset(self):  
        """Reset time to initial value"""  
        self.time_remaining = self.total_time * FPS  
        self.frame_count = 0  

    @property  
    def remaining_seconds(self):  
        """  
        Get remaining time in seconds  

        :return: Remaining time in seconds  
        """  
        return max(self.time_remaining // FPS, 0)

class AlgorithmTracker:
    """Tracks algorithm usage"""
    def __init__(self):
        self.current_algorithm = None
        self.used_algorithms = set()

    def set_algorithm(self, algorithm: AlgorithmType):
        """Set and track current algorithm"""
        self.current_algorithm = algorithm
        self.used_algorithms.add(algorithm)

    def reset(self):
        """Reset algorithm tracking"""
        self.current_algorithm = None
        self.used_algorithms.clear()

class RewardCalculator:
    """Calculates rewards for agent actions"""
    @staticmethod
    def calculate_reward(
        old_pos: Tuple[int, int], 
        new_pos: Tuple[int, int], 
        goal_pos: Tuple[int, int], 
        time_remaining: int,
        optimal_path_length: int,
        moves_made: int
    ) -> float:
        """Calculate reward based on agent's movement"""
        # Reaching goal
        if new_pos == goal_pos:
            efficiency_bonus = max(0, optimal_path_length - moves_made)
            return 100 + efficiency_bonus * 10

        # Time expired
        if time_remaining <= 0:
            return -100

        # Distance-based reward
        old_distance = abs(old_pos[0] - goal_pos[0]) + abs(old_pos[1] - goal_pos[1])
        new_distance = abs(new_pos[0] - goal_pos[0]) + abs(new_pos[1] - goal_pos[1])

        if new_distance < old_distance:
            return 1  # Moving closer
        elif new_distance > old_distance:
            return -1  # Moving away

        return -0.1  # Neutral movement

class GameLogic:
    def __init__(self, map_size: Tuple[int, int] = (10, 10), optimal_path_length: int = 13):
        # Composition over inheritance
        self.state_manager = GameStateManager()
        self.score_manager = ScoreManager(optimal_path_length)
        self.time_manager = TimeManager(TIME_LIMIT)
        self.algorithm_tracker = AlgorithmTracker()
        self.current_maze = TestScenario.DIAGONAL  # Add this line

        self.map_size = map_size
        self.optimal_path_length = optimal_path_length
        
        self.metrics_manager = MetricsManager()
        self.total_nodes_explored = 0  # Add this line  
        self.nodes_explored = 0
        self.start_time = None
        
    def cleanup(self):
        """Clean up resources and save final metrics"""
        if self.metrics_manager.current_run:
            self.metrics_manager.end_run(
                success=self.state_manager.state == GameState.WIN,
                score=self.score_manager.score
            )
        self.metrics_manager.save_metrics()
        
    def set_algorithm(self, algorithm: AlgorithmType):  
        """Set current algorithm"""  
        self.algorithm_tracker.set_algorithm(algorithm)  
        self.nodes_explored = 0  
        self.start_time = datetime.now()  
        # Start metrics collection  
        self.metrics_manager.start_run(algorithm, self.current_maze)

    def increment_nodes_explored(self):  
        self.nodes_explored += 1  
        self.total_nodes_explored += 1
        
    def reset_nodes_explored(self):    
        """Reset both node exploration counters to 0"""    
        self.nodes_explored = 0  
        self.total_nodes_explored = 0

    def set_maze_type(self, maze_type: TestScenario):
        """Set current maze type"""
        self.current_maze = maze_type
        return self.current_maze
        
    def update(self):  
        if self.state_manager.state == GameState.PLAYING:  
            self.time_manager.update()  
            self._update_metrics()

            # Check for time out  
            if self.time_manager.is_time_expired():  
                self.state_manager.state = GameState.LOSE
                # Add metrics for failed run
                self.metrics_manager.end_run(
                    success=False,
                    score=self.score_manager.score
                )
                self.metrics_manager.save_metrics()

    def _update_metrics(self):
        """Update metrics during gameplay"""  
        if self.metrics_manager.current_run:
            time_taken = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
            current_score = self.score_manager.calculate_score(
                time_taken=time_taken,
                nodes_explored=self.total_nodes_explored,
                path_length=self.score_manager.moves_made
            )

            self.metrics_manager.update_run(  
                nodes_explored=self.total_nodes_explored,  
                path_length=self.score_manager.moves_made,  
                time_taken=time_taken,  
                remaining_time=self.time_manager.remaining_seconds,  
                total_time=self.time_manager.total_time  
            )

    def check_win_condition(self, robot_pos: Tuple[int, int], goal_pos: Tuple[int, int]):  
        """Check if robot has reached the goal"""  
        if robot_pos == goal_pos:  
            self.state_manager.state = GameState.WIN  
            time_taken = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0  

            # Calculate final score using new scoring system
            final_score = self.score_manager.calculate_score(
                time_taken=time_taken,
                nodes_explored=self.total_nodes_explored,
                path_length=self.score_manager.moves_made
            )
            self.score_manager.score = final_score

            # Update metrics
            self.metrics_manager.update_run(  
                nodes_explored=self.total_nodes_explored,
                path_length=self.score_manager.moves_made,  
                time_taken=time_taken,  
                remaining_time=self.time_manager.remaining_seconds,  
                total_time=self.time_manager.total_time  
            )  

            self.metrics_manager.end_run(True, final_score)  

        return self.state_manager.state

    def calculate_reward(self, old_pos: Tuple[int, int], new_pos: Tuple[int, int], goal_pos: Tuple[int, int]) -> float:
        """Calculate reward for an action"""
        # Increment moves
        self.score_manager.moves_made += 1

        # Calculate and return reward
        return RewardCalculator.calculate_reward(
            old_pos, 
            new_pos, 
            goal_pos, 
            self.time_manager.time_remaining,
            self.optimal_path_length,
            self.score_manager.moves_made
        )
    
    def get_live_score(self) -> float:  
        """Calculate and return the current live score using ScoreManager's calculate_score"""  
        if self.start_time:  
            time_taken = (datetime.now() - self.start_time).total_seconds()  
            return self.score_manager.calculate_score(  
                time_taken=time_taken,  
                nodes_explored=self.total_nodes_explored,  
                path_length=self.score_manager.moves_made  
            )  
        return 0.0

    def reset(self):    
        """Reset entire game state"""    
        self.state_manager.reset()    
        self.score_manager.reset()    
        self.time_manager.reset()    
        self.algorithm_tracker.reset()    
        self.reset_nodes_explored()  
        return self.state_manager.state

    # Convenience properties and methods
    @property
    def state(self):
        return self.state_manager.state
    
    @state.setter  
    def state(self, value):  
        self.state_manager.state = value

    @property
    def score(self):
        return self.score_manager.score

    @property
    def moves_made(self):
        return self.score_manager.moves_made

    @property
    def time_remaining(self):
        return self.time_manager.time_remaining

    @property
    def current_algorithm(self):
        return self.algorithm_tracker.current_algorithm

    @property
    def used_algorithms(self):
        return self.algorithm_tracker.used_algorithms
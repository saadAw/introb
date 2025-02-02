from typing import Dict, List, Tuple
import numpy as np
import random
from collections import defaultdict, deque
from src.config.constants import MapSymbols

class SARSAPathfinder:
    # Configuration parameters
    PARAMS = {
        # Core SARSA parameters
        'LEARNING_RATE_START': 0.1,      # Initial learning rate
        'LEARNING_RATE_MIN': 0.01,       # Minimum learning rate
        'DISCOUNT_FACTOR': 0.95,         # Future reward discount
        'EPSILON_START': 1.0,            # Initial exploration rate
        'EPSILON_MIN': 0.01,             # Minimum exploration rate
        'EPSILON_DECAY': 0.995,          # Exploration decay rate

        # Memory and tracking
        'EXPERIENCE_BUFFER_SIZE': 1000,   # Size of experience replay buffer
        'MAX_PREVIOUS_STATES': 10,        # Number of previous states to track
        'REPLAY_BATCH_SIZE': 32,          # Batch size for experience replay

        # Reward structure
        'REWARD_GOAL': 100.0,            # Reward for reaching goal
        'REWARD_WALL': -5.0,             # Penalty for hitting wall
        'REWARD_LOOP': -2.0,             # Penalty for revisiting states
        'REWARD_CLOSER': 1.0,            # Reward for moving closer to goal
        'REWARD_FARTHER': -1.0,          # Penalty for moving away from goal
        'SAFETY_FACTOR': 0.8,            # SARSA-specific safety factor

        # Training settings
        'DEFAULT_EPISODES': 1000,         # Default number of training episodes
        'MAX_STEPS_PER_EPISODE': 1000,    # Maximum steps per episode
        'PROGRESS_PRINT_INTERVAL': 100,   # Episodes between progress updates

        # Early Stopping
        'EARLY_STOPPING_PATIENCE': 20,    # Episodes to wait for improvement
        'EARLY_STOPPING_MIN_DELTA': 0.1,  # Minimum change for improvement
        'EARLY_STOPPING_WINDOW': 100,     # Window for calculating average reward
        'MIN_EPISODES': 200,             # Minimum episodes before early stopping
        'MAX_EPISODES': 5000,            # Maximum episodes regardless of improvement
    }

    def __init__(self, game_map, learning_rate=None, discount_factor=None, epsilon_start=None):
        self.game_map = game_map
        self.width = game_map.width
        self.height = game_map.height

        # Initialize parameters
        self.learning_rate_start = learning_rate or self.PARAMS['LEARNING_RATE_START']
        self.discount_factor = discount_factor or self.PARAMS['DISCOUNT_FACTOR']
        self.epsilon = epsilon_start or self.PARAMS['EPSILON_START']

        # Using defaultdict for Q-table
        self.q_table = defaultdict(lambda: defaultdict(float))

        # Action space
        self.actions = ['right', 'left', 'down', 'up']
        self.action_deltas = {
            'right': (1, 0),
            'left': (-1, 0),
            'down': (0, 1),
            'up': (0, -1)
        }

        # Initialize learning components
        self.experience_buffer = deque(maxlen=self.PARAMS['EXPERIENCE_BUFFER_SIZE'])
        self.state_visits = defaultdict(int)
        self.previous_states = []
        self.max_previous_states = self.PARAMS['MAX_PREVIOUS_STATES']
        self.current_goal = None

        # Performance tracking
        self.episode_rewards = []
        self.path_lengths = []

        self.game_logic = None

    def set_game_logic(self, game_logic):  
        """  
        Set reference to game logic for metrics tracking.  

        Args:  
            game_logic: GameLogic instance for tracking metrics  
        """  
        self.game_logic = game_logic

    def get_state_features(self, pos: Tuple[int, int], goal: Tuple[int, int]) -> str:
        """Enhanced state representation with safety considerations"""
        x, y = pos
        gx, gy = goal

        # Get wall information with extended vision
        wall_map = []
        for dy in [-2, -1, 0, 1, 2]:  # Extended vision range
            for dx in [-2, -1, 0, 1, 2]:
                nx, ny = x + dx, y + dy
                if (0 <= nx < self.width and 
                    0 <= ny < self.height and 
                    self.game_map.grid[ny][nx] != MapSymbols.OBSTACLE):
                    wall_map.append('0')
                else:
                    wall_map.append('1')

        # Calculate relative direction and distance
        dx = gx - x
        dy = gy - y
        distance = abs(dx) + abs(dy)
        
        # Get octant-based direction (more precise than quadrants)
        angle = np.arctan2(dy, dx)
        octant = int((angle + np.pi) / (np.pi/8))

        # Count nearby walls for safety consideration
        nearby_walls = wall_map.count('1')

        return f"{','.join(wall_map)}|{octant}|{distance}|{nearby_walls}|{pos}"

    def get_valid_actions(self, state: Tuple[int, int]) -> List[str]:
        """Get list of valid actions with safety ratings"""
        valid_actions = []
        x, y = state

        for action, (dx, dy) in self.action_deltas.items():
            new_x, new_y = x + dx, y + dy
            if (0 <= new_x < self.width and 
                0 <= new_y < self.height and 
                self.game_map.grid[new_y][new_x] != MapSymbols.OBSTACLE):
                valid_actions.append(action)

        return valid_actions

    def get_next_state(self, state: Tuple[int, int], action: str) -> Tuple[int, int]:  
        """Get next state given current state and action"""  
        dx, dy = self.action_deltas[action]  
        next_x = state[0] + dx  
        next_y = state[1] + dy  

        # Increment nodes explored counter when checking a new state  
        state_key = (next_x, next_y)  
        if self.game_logic and state_key not in self.state_visits:  
            self.game_logic.increment_nodes_explored()  
            self.state_visits[state_key] = 1  

        if (0 <= next_x < self.width and   
            0 <= next_y < self.height and   
            self.game_map.grid[next_y][next_x] != MapSymbols.OBSTACLE):  
            return (next_x, next_y)  
        return state
    
    def get_reward(self, current_state: Tuple[int, int], 
                  next_state: Tuple[int, int], 
                  goal: Tuple[int, int]) -> float:
        """Enhanced reward calculation with safety considerations"""
        # Goal reached
        if next_state == goal:
            return self.PARAMS['REWARD_GOAL']

        # Wall collision
        if next_state == current_state:
            return self.PARAMS['REWARD_WALL']

        # Loop prevention
        if next_state in self.previous_states:
            return self.PARAMS['REWARD_LOOP']

        # Distance-based rewards
        current_distance = abs(current_state[0] - goal[0]) + abs(current_state[1] - goal[1])
        next_distance = abs(next_state[0] - goal[0]) + abs(next_state[1] - goal[1])

        # Safety consideration - count nearby walls
        x, y = next_state
        nearby_walls = sum(1 for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]
                         if not (0 <= x+dx < self.width and 
                               0 <= y+dy < self.height and 
                               self.game_map.grid[y+dy][x+dx] != MapSymbols.OBSTACLE))
        
        safety_penalty = nearby_walls * (1 - self.PARAMS['SAFETY_FACTOR'])

        if next_distance < current_distance:
            return self.PARAMS['REWARD_CLOSER'] - safety_penalty
        return self.PARAMS['REWARD_FARTHER'] - safety_penalty

    def choose_action(self, state: Tuple[int, int], valid_actions: List[str]) -> str:
        """SARSA action selection with safety considerations"""
        if np.random.random() < self.epsilon:
            return np.random.choice(valid_actions)

        state_key = self.get_state_features(state, self.current_goal)
        q_values = {action: self.q_table[state_key][action] for action in valid_actions}

        # Add safety bias
        x, y = state
        for action in valid_actions:
            dx, dy = self.action_deltas[action]
            next_x, next_y = x + dx, y + dy
            nearby_walls = sum(1 for ddx, ddy in [(0,1), (0,-1), (1,0), (-1,0)]
                             if not (0 <= next_x+ddx < self.width and 
                                   0 <= next_y+ddy < self.height and 
                                   self.game_map.grid[next_y+ddy][next_x+ddx] != MapSymbols.OBSTACLE))
            q_values[action] *= self.PARAMS['SAFETY_FACTOR'] ** nearby_walls

        return max(q_values.items(), key=lambda x: x[1])[0]

    def train(self, start: Tuple[int, int], goal: Tuple[int, int], 
          episodes: int = None, max_steps: int = None) -> None:
        """SARSA training process with data collection"""
        import os
        import json
        import time
        from datetime import datetime

        # Create directory for training data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        data_dir = f"training_data/sarsa_training_{timestamp}"
        os.makedirs(data_dir, exist_ok=True)

        # Training metrics to track
        training_data = {
            "episode_rewards": [],
            "episode_lengths": [],
            "exploration_rates": [],
            "nodes_explored_per_episode": [],
            "completion_times": [],
            "training_summary": {}
        }

        training_start_time = time.time()
        max_steps = max_steps or self.PARAMS['MAX_STEPS_PER_EPISODE']
        self.current_goal = goal
        self.state_visits = {}  # Reset state visits at start of training

        best_avg_reward = float('-inf')
        patience_counter = 0
        window_size = self.PARAMS['EARLY_STOPPING_WINDOW']

        print("Starting SARSA training with data collection...")

        episode = 0
        while episode < self.PARAMS['MAX_EPISODES']:
            episode_start_time = time.time()
            current_state = start
            self.previous_states = []
            episode_reward = 0
            path_length = 0
            nodes_explored_start = len(self.state_visits)
            goal_reached = False

            # Count start state only if not visited before
            if self.game_logic and current_state not in self.state_visits:
                self.game_logic.increment_nodes_explored()
                self.state_visits[current_state] = 1

            valid_actions = self.get_valid_actions(current_state)
            current_action = self.choose_action(current_state, valid_actions)

            for step in range(max_steps):
                # Get and count next state
                next_state = self.get_next_state(current_state, current_action)
                if self.game_logic and next_state not in self.state_visits:
                    self.game_logic.increment_nodes_explored()
                    self.state_visits[next_state] = 1

                reward = self.get_reward(current_state, next_state, goal)

                next_valid_actions = self.get_valid_actions(next_state)
                next_action = self.choose_action(next_state, next_valid_actions)

                # SARSA update
                state_key = self.get_state_features(current_state, goal)
                next_state_key = self.get_state_features(next_state, goal)

                current_q = self.q_table[state_key][current_action]
                next_q = self.q_table[next_state_key][next_action]

                self.q_table[state_key][current_action] = current_q + \
                    self.learning_rate_start * (reward + self.discount_factor * next_q - current_q)

                if len(self.previous_states) >= self.max_previous_states:
                    self.previous_states.pop(0)
                self.previous_states.append(current_state)

                episode_reward += reward
                path_length += 1

                if next_state == goal:
                    goal_reached = True
                    break

                current_state = next_state
                current_action = next_action

            # Store episode data
            self.episode_rewards.append(episode_reward)
            self.path_lengths.append(path_length)

            # Collect episode data for saving
            episode_time = time.time() - episode_start_time
            nodes_explored_episode = len(self.state_visits) - nodes_explored_start

            training_data["episode_rewards"].append(float(episode_reward))
            training_data["episode_lengths"].append(path_length)
            training_data["exploration_rates"].append(float(self.epsilon))
            training_data["nodes_explored_per_episode"].append(nodes_explored_episode)
            training_data["completion_times"].append(float(episode_time))

            # Decay epsilon
            self.epsilon = max(self.PARAMS['EPSILON_MIN'],
                            self.epsilon * self.PARAMS['EPSILON_DECAY'])

            # Save intermediate data every 100 episodes
            if (episode + 1) % 100 == 0:
                with open(f"{data_dir}/training_progress_{episode+1}.json", 'w') as f:
                    json.dump(training_data, f, indent=4)

            # Early stopping check
            if episode >= self.PARAMS['MIN_EPISODES']:
                current_avg_reward = np.mean(self.episode_rewards[-window_size:])

                if (episode + 1) % self.PARAMS['PROGRESS_PRINT_INTERVAL'] == 0:
                    avg_length = np.mean(self.path_lengths[-window_size:])
                    print(f"Episode {episode + 1}: Avg Reward = {current_avg_reward:.2f}, "
                        f"Avg Path Length = {avg_length:.2f}, "
                        f"Best Avg Reward = {best_avg_reward:.2f}, "
                        f"Patience = {patience_counter}, "
                        f"Goal Reached = {goal_reached}")

                if current_avg_reward > best_avg_reward + self.PARAMS['EARLY_STOPPING_MIN_DELTA']:
                    best_avg_reward = current_avg_reward
                    patience_counter = 0
                else:
                    patience_counter += 1

                if patience_counter >= self.PARAMS['EARLY_STOPPING_PATIENCE']:
                    print(f"\nEarly stopping triggered after {episode + 1} episodes")
                    break

            episode += 1

        # Calculate and save training summary
        total_training_time = time.time() - training_start_time
        training_data["training_summary"] = {
            "total_episodes": episode + 1,
            "total_training_time": total_training_time,
            "final_epsilon": float(self.epsilon),
            "best_average_reward": float(best_avg_reward),
            "total_unique_states_visited": len(self.state_visits),
            "average_episode_length": float(np.mean(training_data["episode_lengths"])),
            "average_episode_reward": float(np.mean(training_data["episode_rewards"])),
            "average_nodes_per_episode": float(np.mean(training_data["nodes_explored_per_episode"])),
            "training_parameters": self.PARAMS
        }

        # Save final training data
        with open(f"{data_dir}/final_training_data.json", 'w') as f:
            json.dump(training_data, f, indent=4)

        print(f"\nTraining completed. Data saved in {data_dir}")
        print(f"Total training time: {total_training_time:.2f} seconds")
        print(f"Final average reward: {np.mean(self.episode_rewards[-window_size:]):.2f}")
        print(f"Final average path length: {np.mean(self.path_lengths[-window_size:]):.2f}")
    def get_next_move(self, current_pos: Tuple[int, int], goal_pos: Tuple[int, int]) -> str:
        """Get next move with safety considerations"""
        self.current_goal = goal_pos

        if len(self.previous_states) >= self.max_previous_states:
            self.previous_states.pop(0)
        self.previous_states.append(current_pos)

        valid_actions = self.get_valid_actions(current_pos)
        return self.choose_action(current_pos, valid_actions)
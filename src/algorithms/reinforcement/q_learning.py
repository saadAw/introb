from typing import Dict, List, Tuple
import numpy as np
import random
from collections import defaultdict, deque
from src.config.constants import MapSymbols

class QLearningPathfinder:
    # Configuration parameters
    PARAMS = {
        # Core Q-learning parameters
        'LEARNING_RATE_START': 0.1,      # Initial learning rate
        'LEARNING_RATE_MIN': 0.01,       # Minimum learning rate
        'DISCOUNT_FACTOR': 0.95,         # Future reward discount
        'EPSILON_START': 1.0,            # Initial exploration rate
        'EPSILON_MIN': 0.001,             # Minimum exploration rate
        'EPSILON_DECAY': 0.995,          # Exploration decay rate

        # Memory and tracking
        'EXPERIENCE_BUFFER_SIZE': 1000,   # Size of experience replay buffer
        'MAX_PREVIOUS_STATES': 10,        # Number of previous states to track
        'REPLAY_BATCH_SIZE': 32,          # Batch size for experience replay

        # Reward structure
        'REWARD_GOAL': 50000.0,            # Reward for reaching goal
        'REWARD_WALL': -10.0,             # Penalty for hitting wall
        'REWARD_LOOP': -10.0,             # Penalty for revisiting states
        'REWARD_CLOSER': 0.0,            # Reward for moving closer to goal
        'REWARD_FARTHER': -0.5,          # Penalty for moving away from goal
        'EXPLORATION_BONUS_FACTOR': 1,  # Factor for exploration bonus

        # Training settings
        'DEFAULT_EPISODES': 1000,         # Default number of training episodes
        'MAX_STEPS_PER_EPISODE': 5000,    # Maximum steps per episode
        'PROGRESS_PRINT_INTERVAL': 100,    # Episodes between progress updates

        # Early Stopping
        'EARLY_STOPPING_PATIENCE': 100,     # Number of epochs to wait for improvement  
        'EARLY_STOPPING_MIN_DELTA': 0.1,   # Minimum change to qualify as an improvement  
        'EARLY_STOPPING_WINDOW': 100,      # Window size for calculating average reward  
        'MIN_EPISODES': 100,              # Minimum number of episodes before early stopping  
        'MAX_EPISODES': 5000,             # Maximum number of episodes regardless of improvement
    }

    def __init__(self, game_map, learning_rate=None, discount_factor=None, epsilon_start=None):
        self.game_map = game_map
        self.width = game_map.width
        self.height = game_map.height

        # Initialize parameters (allow override through constructor)
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
        """Enhanced state representation"""
        x, y = pos
        gx, gy = goal

        # Get wall information in surrounding area
        wall_map = []
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
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

        # Get quadrant-based direction
        angle = np.arctan2(dy, dx)
        quadrant = int((angle + np.pi) / (np.pi/4))

        return f"{','.join(wall_map)}|{quadrant}|{distance}|{pos}"

    def get_valid_actions(self, state: Tuple[int, int]) -> List[str]:
        """Get list of valid actions from current state"""
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
        next_state = (next_x, next_y)

        # Only count if it's a valid, new state
        if (0 <= next_x < self.width and   
            0 <= next_y < self.height and   
            self.game_map.grid[next_y][next_x] != MapSymbols.OBSTACLE and
            self.game_logic and 
            next_state not in self.state_visits):  
            self.game_logic.increment_nodes_explored()
            self.state_visits[next_state] = 1

        if (0 <= next_x < self.width and   
            0 <= next_y < self.height and   
            self.game_map.grid[next_y][next_x] != MapSymbols.OBSTACLE):  
            return (next_x, next_y)  
        return state

    def get_reward(self, current_state: Tuple[int, int], 
                  next_state: Tuple[int, int], 
                  goal: Tuple[int, int]) -> float:
        """Enhanced reward calculation"""
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

        # Exploration bonus
        state_key = self.get_state_features(next_state, goal)
        exploration_bonus = self.PARAMS['EXPLORATION_BONUS_FACTOR'] / (self.state_visits[state_key] + 1)

        if next_distance < current_distance:
            return self.PARAMS['REWARD_CLOSER'] + exploration_bonus
        return self.PARAMS['REWARD_FARTHER'] + exploration_bonus

    def get_learning_rate(self, state_key: str, action: str) -> float:
        """Dynamic learning rate based on state-action visits"""
        visits = self.state_visits[state_key]
        return max(self.PARAMS['LEARNING_RATE_MIN'], 
                  self.learning_rate_start * (1 / (1 + visits * 0.1)))

    def choose_action(self, state: Tuple[int, int], valid_actions: List[str]) -> str:
        """Enhanced action selection with exploration"""
        if np.random.random() < self.epsilon:
            return np.random.choice(valid_actions)

        state_key = self.get_state_features(state, self.current_goal)
        q_values = {action: self.q_table[state_key][action] for action in valid_actions}

        # Add small random noise for tie-breaking
        noisy_q_values = {action: q + np.random.normal(0, 0.01) 
                         for action, q in q_values.items()}
        return max(noisy_q_values.items(), key=lambda x: x[1])[0]

    def update_q_value(self, state: Tuple[int, int], action: str, 
                      reward: float, next_state: Tuple[int, int]) -> None:
        """Update Q-value with dynamic learning rate"""
        state_key = self.get_state_features(state, self.current_goal)
        next_state_key = self.get_state_features(next_state, self.current_goal)

        learning_rate = self.get_learning_rate(state_key, action)

        next_q = max([self.q_table[next_state_key][a] 
                     for a in self.get_valid_actions(next_state)], 
                    default=0)

        current_q = self.q_table[state_key][action]
        self.q_table[state_key][action] = current_q + learning_rate * (
            reward + self.discount_factor * next_q - current_q
        )

    def train(self, start: Tuple[int, int], goal: Tuple[int, int],   
          episodes: int = None, max_steps: int = None) -> None:  
        """Enhanced training process with early stopping"""  
        max_steps = max_steps or self.PARAMS['MAX_STEPS_PER_EPISODE']  
        self.current_goal = goal  

        # Early stopping variables  
        best_avg_reward = float('-inf')  
        patience_counter = 0  
        min_delta = self.PARAMS['EARLY_STOPPING_MIN_DELTA']  
        window_size = self.PARAMS['EARLY_STOPPING_WINDOW']  

        print("Starting training with early stopping...")  

        episode = 0  
        while episode < self.PARAMS['MAX_EPISODES']:  
            current_state = start  
            self.previous_states = []  
            episode_reward = 0  
            path_length = 0  

            # Episode training loop  
            for step in range(max_steps):  
                valid_actions = self.get_valid_actions(current_state)  
                action = self.choose_action(current_state, valid_actions)  
                next_state = self.get_next_state(current_state, action)  

                reward = self.get_reward(current_state, next_state, goal)  
                self.update_q_value(current_state, action, reward, next_state)  

                self.experience_buffer.append(  
                    (current_state, action, reward, next_state)  
                )  

                self.previous_states.append(current_state)  
                if len(self.previous_states) > self.max_previous_states:  
                    self.previous_states.pop(0)  

                state_key = self.get_state_features(current_state, goal)  

                episode_reward += reward  
                path_length += 1  
                current_state = next_state  

                if current_state == goal:  
                    break  

            self.episode_rewards.append(episode_reward)  
            self.path_lengths.append(path_length)  

            # Decay epsilon  
            self.epsilon = max(self.PARAMS['EPSILON_MIN'],   
                            self.epsilon * self.PARAMS['EPSILON_DECAY'])  

            # Experience replay  
            if len(self.experience_buffer) >= self.PARAMS['REPLAY_BATCH_SIZE']:  
                batch = random.sample(self.experience_buffer,   
                                    self.PARAMS['REPLAY_BATCH_SIZE'])  
                for exp_state, exp_action, exp_reward, exp_next_state in batch:  
                    self.update_q_value(exp_state, exp_action, exp_reward, exp_next_state)  

            # Early stopping check  
            if episode >= self.PARAMS['MIN_EPISODES']:  
                current_avg_reward = np.mean(self.episode_rewards[-window_size:])  

                # Print progress  
                if (episode + 1) % self.PARAMS['PROGRESS_PRINT_INTERVAL'] == 0:  
                    avg_length = np.mean(self.path_lengths[-window_size:])  
                    print(f"Episode {episode + 1}: Avg Reward = {current_avg_reward:.2f}, "  
                        f"Avg Path Length = {avg_length:.2f}, "  
                        f"Best Avg Reward = {best_avg_reward:.2f}, "  
                        f"Patience = {patience_counter}")  

                # Check if there's an improvement  
                if current_avg_reward > best_avg_reward + min_delta:  
                    best_avg_reward = current_avg_reward  
                    patience_counter = 0  
                else:  
                    patience_counter += 1  

                # Check if we should stop  
                if patience_counter >= self.PARAMS['EARLY_STOPPING_PATIENCE']:  
                    print(f"\nEarly stopping triggered after {episode + 1} episodes")  
                    print(f"Best average reward: {best_avg_reward:.2f}")  
                    print(f"Final average reward: {current_avg_reward:.2f}")  
                    print(f"Final average path length: {np.mean(self.path_lengths[-window_size:]):.2f}")  
                    break  

            episode += 1  

        if episode >= self.PARAMS['MAX_EPISODES']:  
            print(f"\nReached maximum episodes ({self.PARAMS['MAX_EPISODES']})")  
            print(f"Final average reward: {np.mean(self.episode_rewards[-window_size:]):.2f}")  
            print(f"Final average path length: {np.mean(self.path_lengths[-window_size:]):.2f}")

    def get_next_move(self, current_pos: Tuple[int, int], goal_pos: Tuple[int, int]) -> str:
        """Get next move with enhanced decision making"""
        self.current_goal = goal_pos

        if len(self.previous_states) >= self.max_previous_states:
            self.previous_states.pop(0)
        self.previous_states.append(current_pos)

        valid_actions = self.get_valid_actions(current_pos)
        state_key = self.get_state_features(current_pos, goal_pos)
        q_values = {action: self.q_table[state_key][action] for action in valid_actions}

        # Check for loops
        if len(self.previous_states) >= 3:
            if len(set(self.previous_states[-3:])) == 1:  # Same position 3 times
                sorted_actions = sorted(q_values.items(), key=lambda x: x[1], reverse=True)
                if len(sorted_actions) > 1:
                    return sorted_actions[1][0]

        return max(q_values.items(), key=lambda x: x[1])[0]
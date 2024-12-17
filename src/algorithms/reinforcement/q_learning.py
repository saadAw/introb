from typing import Dict, List, Tuple
import numpy as np
from collections import defaultdict
from src.config.constants import MapSymbols

class QLearningPathfinder:
    def __init__(self, game_map, learning_rate=0.1, discount_factor=0.95, epsilon_start=1.0):
        self.game_map = game_map
        self.width = game_map.width
        self.height = game_map.height

        # Q-learning hyperparameters
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon_start
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995

        # Using defaultdict to avoid explicit initialization of Q-values
        self.q_table = defaultdict(lambda: defaultdict(float))

        # Action space
        self.actions = ['right', 'left', 'down', 'up']
        self.action_deltas = {
            'right': (1, 0),
            'left': (-1, 0),
            'down': (0, 1),
            'up': (0, -1)
        }

        # Keep track of previous states to prevent loops
        self.previous_states = []
        self.max_previous_states = 10

    def get_state_features(self, pos: Tuple[int, int], goal: Tuple[int, int]) -> str:
        """Create a more informative state representation"""
        x, y = pos
        gx, gy = goal

        # Check surrounding cells for walls
        surroundings = []
        for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
            nx, ny = x + dx, y + dy
            if (0 <= nx < self.width and 
                0 <= ny < self.height and 
                self.game_map.grid[ny][nx] != MapSymbols.OBSTACLE):
                surroundings.append('0')
            else:
                surroundings.append('1')

        # Calculate relative direction to goal
        dx = gx - x
        dy = gy - y
        direction = ''
        if abs(dx) > abs(dy):
            direction = 'E' if dx > 0 else 'W'
        else:
            direction = 'S' if dy > 0 else 'N'

        # Combine features into state representation
        state = f"{','.join(surroundings)}|{direction}|{pos}"
        return state

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

        # Check if next state would hit a wall
        if (0 <= next_x < self.width and 
            0 <= next_y < self.height and 
            self.game_map.grid[next_y][next_x] != MapSymbols.OBSTACLE):
            return (next_x, next_y)
        return state  # Return current state if would hit wall

    def get_reward(self, current_state: Tuple[int, int], 
                  next_state: Tuple[int, int], 
                  goal: Tuple[int, int]) -> float:
        """Calculate reward for the transition"""
        # Check if reached goal
        if next_state == goal:
            return 100.0

        # Penalty for hitting walls (when next_state == current_state)
        if next_state == current_state:
            return -5.0

        # Penalty for revisiting states (discourage loops)
        if next_state in self.previous_states:
            return -2.0

        # Calculate distance-based reward
        current_distance = abs(current_state[0] - goal[0]) + abs(current_state[1] - goal[1])
        next_distance = abs(next_state[0] - goal[0]) + abs(next_state[1] - goal[1])

        if next_distance < current_distance:
            return 1.0  # Reward for moving closer to goal
        return -0.5    # Small penalty for moving away from goal

    def choose_action(self, state: Tuple[int, int], valid_actions: List[str]) -> str:
        """Choose action using epsilon-greedy policy"""
        if np.random.random() < self.epsilon:
            return np.random.choice(valid_actions)

        # Get Q-values for all valid actions
        state_key = self.get_state_features(state, self.current_goal)
        q_values = {action: self.q_table[state_key][action] for action in valid_actions}

        # Return action with highest Q-value (random tie-breaking)
        max_q = max(q_values.values())
        best_actions = [action for action, q in q_values.items() if q == max_q]
        return np.random.choice(best_actions)

    def train(self, start: Tuple[int, int], goal: Tuple[int, int], 
              episodes: int = 1000, max_steps: int = 1000) -> None:
        """Train the Q-learning agent"""
        self.current_goal = goal  # Store goal for state features

        for episode in range(episodes):
            current_state = start
            self.previous_states = []

            for step in range(max_steps):
                # Get valid actions and choose one
                valid_actions = self.get_valid_actions(current_state)
                action = self.choose_action(current_state, valid_actions)

                # Take action and get reward
                next_state = self.get_next_state(current_state, action)
                reward = self.get_reward(current_state, next_state, goal)

                # Update Q-value
                current_state_key = self.get_state_features(current_state, goal)
                next_state_key = self.get_state_features(next_state, goal)

                next_max_q = max([self.q_table[next_state_key][a] 
                                for a in self.get_valid_actions(next_state)], 
                               default=0)

                current_q = self.q_table[current_state_key][action]
                self.q_table[current_state_key][action] = current_q + self.learning_rate * (
                    reward + self.discount_factor * next_max_q - current_q
                )

                # Update state and previous states
                self.previous_states.append(current_state)
                if len(self.previous_states) > self.max_previous_states:
                    self.previous_states.pop(0)
                current_state = next_state

                # Check if goal reached
                if current_state == goal:
                    break

            # Decay epsilon
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def get_next_move(self, current_pos: Tuple[int, int], goal_pos: Tuple[int, int]) -> str:
        """Get the next move direction based on learned Q-values"""
        self.current_goal = goal_pos  # Update current goal

        # Update previous states
        if len(self.previous_states) >= self.max_previous_states:
            self.previous_states.pop(0)
        self.previous_states.append(current_pos)

        # Get valid actions and their Q-values
        valid_actions = self.get_valid_actions(current_pos)
        state_key = self.get_state_features(current_pos, goal_pos)

        # Choose best action (no exploration during execution)
        q_values = {action: self.q_table[state_key][action] for action in valid_actions}
        best_action = max(q_values.items(), key=lambda x: x[1])[0]

        # If stuck in a loop, try second-best action
        if len(self.previous_states) >= 3:
            if len(set(self.previous_states[-3:])) == 1:  # Same position 3 times
                sorted_actions = sorted(q_values.items(), key=lambda x: x[1], reverse=True)
                if len(sorted_actions) > 1:
                    best_action = sorted_actions[1][0]  # Use second-best action

        return best_action
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import random
from collections import deque
import json
from datetime import datetime
import os
from typing import Tuple, List, Dict

class DQN(nn.Module):
    """Neural network for Q-value approximation"""
    def __init__(self, input_size: int, output_size: int):
        super(DQN, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_size, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, output_size)
        )

    def forward(self, x):
        return self.network(x)

class ReplayBuffer:
    """Experience replay buffer"""
    def __init__(self, capacity: int = 10000):
        self.buffer = deque(maxlen=capacity)

    def push(self, state, action, reward, next_state, done):
        self.buffer.append((state, action, reward, next_state, done))

    def sample(self, batch_size: int) -> tuple:
        state, action, reward, next_state, done = zip(*random.sample(self.buffer, batch_size))
        return (np.array(state), np.array(action), np.array(reward),
                np.array(next_state), np.array(done))

    def __len__(self):
        return len(self.buffer)

class DQNAgent:
    """DQN Agent for maze navigation with metric tracking"""
    def __init__(self, game_map):
        self.game_map = game_map
        self.state_size = 5  # (x, y, goal_x, goal_y, distance)
        self.action_size = 4  # up, down, left, right
        self.action_map = {0: 'up', 1: 'down', 2: 'left', 3: 'right'}

        
        # Hyperparameters
        self.gamma = 0.99
        self.epsilon = 1.0
        self.epsilon_min = 0.1  # Higher minimum exploration
        self.epsilon_decay = 0.995  # Slower decay
        self.learning_rate = 0.001
        self.batch_size = 32

        # Neural Networks
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.policy_net = DQN(self.state_size, self.action_size).to(self.device)
        self.target_net = DQN(self.state_size, self.action_size).to(self.device)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        
        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=self.learning_rate)
        self.memory = ReplayBuffer()
        
        # Training parameters
        self.steps_done = 0
        self.target_update = 10
        
        # Metrics
        self.episode_rewards = []
        self.episode_lengths = []
        self.current_episode_reward = 0
        self.current_episode_length = 0
        self.losses = []
        self.average_q_values = []
        self.training_episodes = 0
        self.successful_episodes = 0
        
        # Create metrics directory if it doesn't exist
        self.metrics_dir = "metrics"
        os.makedirs(self.metrics_dir, exist_ok=True)
        
    def get_state(self, pos: tuple, goal_pos: tuple) -> np.ndarray:
        """Enhanced state representation"""
        # Calculate Manhattan distance
        distance = abs(pos[0] - goal_pos[0]) + abs(pos[1] - goal_pos[1])
        
        # Normalize positions by map size
        normalized_state = np.array([
            pos[0] / self.game_map.width,
            pos[1] / self.game_map.height,
            goal_pos[0] / self.game_map.width,
            goal_pos[1] / self.game_map.height,
            distance / (self.game_map.width + self.game_map.height)  # Normalized distance
        ], dtype=np.float32)
        
        return normalized_state

    def get_next_move(self, current_pos: tuple, goal_pos: tuple) -> str:
        """Select action using epsilon-greedy policy"""
        state = torch.FloatTensor(self.get_state(current_pos, goal_pos)).to(self.device)
        
        if random.random() > self.epsilon:
            with torch.no_grad():
                q_values = self.policy_net(state)
                self.average_q_values.append(q_values.mean().item())
                action = q_values.max(0)[1].item()
        else:
            action = random.randrange(self.action_size)
            
        # Decay epsilon
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
        return self.action_map[action]

    def train(self, batch_size: int):
        if len(self.memory) < batch_size:
            return

        states, actions, rewards, next_states, dones = self.memory.sample(batch_size)
        states = torch.FloatTensor(states).to(self.device)
        actions = torch.LongTensor(actions).to(self.device)
        rewards = torch.FloatTensor(rewards).to(self.device)
        next_states = torch.FloatTensor(next_states).to(self.device)
        dones = torch.FloatTensor(dones).to(self.device)

        # Direct Q-learning without target network
        current_q_values = self.policy_net(states).gather(1, actions.unsqueeze(1))
        next_q_values = self.policy_net(next_states).max(1)[0].detach()
        target_q_values = rewards + (1 - dones) * self.gamma * next_q_values
        
        loss = nn.MSELoss()(current_q_values.squeeze(), target_q_values)
        self.losses.append(loss.item())
        
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()        
        # Update target network
        self.steps_done += 1
        if self.steps_done % self.target_update == 0:
            self.target_net.load_state_dict(self.policy_net.state_dict())
            
    def calculate_reward(self, old_pos, new_pos, goal_pos):
        """Enhanced reward calculation"""
        if new_pos == goal_pos:
            return 100  # Large reward for reaching goal
        
        old_distance = abs(old_pos[0] - goal_pos[0]) + abs(old_pos[1] - goal_pos[1])
        new_distance = abs(new_pos[0] - goal_pos[0]) + abs(new_pos[1] - goal_pos[1])
        
        if new_distance < old_distance:
            return 1  # Reward for moving closer
        elif new_distance > old_distance:
            return -2  # Larger penalty for moving away
        
        return -0.1  # Small penalty for standing still


    def update(self, state, action, reward, next_state, done):
        """Store transition and update metrics"""
        action_idx = list(self.action_map.values()).index(action)
        self.memory.push(self.get_state(*state), action_idx, reward,
                        self.get_state(*next_state), done)
        
        # Update episode metrics
        self.current_episode_reward += reward
        self.current_episode_length += 1
        
        if done:
            print(f"Episode finished with total reward: {self.current_episode_reward}")  # Debug print
            self.training_episodes += 1
            if reward > 0:
                self.successful_episodes += 1
            self.episode_rewards.append(self.current_episode_reward)
            self.episode_lengths.append(self.current_episode_length)
            self.current_episode_reward = 0
            self.current_episode_length = 0
        
        # Train the network
        if len(self.memory) >= self.batch_size:
            self.train(self.batch_size)

    def get_current_metrics(self) -> Dict:
        """Get current training metrics"""
        if not self.episode_rewards:
            return {
                "avg_reward": 0,
                "success_rate": 0,
                "avg_length": 0,
                "epsilon": self.epsilon,
                "loss": 0,
                "avg_q_value": 0
            }
            
        return {
            "avg_reward": np.mean(self.episode_rewards[-100:]),
            "success_rate": self.successful_episodes / max(1, self.training_episodes),
            "avg_length": np.mean(self.episode_lengths[-100:]),
            "epsilon": self.epsilon,
            "loss": np.mean(self.losses[-100:]) if self.losses else 0,
            "avg_q_value": np.mean(self.average_q_values[-100:]) if self.average_q_values else 0
        }

    def save_metrics(self):
        """Save metrics to file"""
        metrics = {
            "episode_rewards": self.episode_rewards,
            "episode_lengths": self.episode_lengths,
            "losses": self.losses,
            "average_q_values": self.average_q_values,
            "training_episodes": self.training_episodes,
            "successful_episodes": self.successful_episodes,
            "epsilon": self.epsilon
        }
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.metrics_dir, f"dqn_metrics_{timestamp}.json")
        
        with open(filename, 'w') as f:
            json.dump(metrics, f)

    def save(self, path: str):
        """Save the model and training state"""
        torch.save({
            'policy_net_state_dict': self.policy_net.state_dict(),
            'target_net_state_dict': self.target_net.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'epsilon': self.epsilon,
            'metrics': self.get_current_metrics()
        }, path)

    def load(self, path: str):
        """Load the model and training state"""
        checkpoint = torch.load(path)
        self.policy_net.load_state_dict(checkpoint['policy_net_state_dict'])
        self.target_net.load_state_dict(checkpoint['target_net_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.epsilon = checkpoint['epsilon']
        

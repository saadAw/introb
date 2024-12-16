import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import random
from collections import deque
from typing import Tuple, List

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
    """DQN Agent for maze navigation"""
    def __init__(self, game_map):
        self.game_map = game_map
        self.state_size = 4  # (x, y, goal_x, goal_y)
        self.action_size = 4  # up, down, left, right
        self.action_map = {0: 'up', 1: 'down', 2: 'left', 3: 'right'}
        
        # Hyperparameters
        self.gamma = 0.99
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
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
        
    def get_state(self, pos: tuple, goal_pos: tuple) -> np.ndarray:
        """Convert positions to state representation"""
        return np.array([pos[0], pos[1], goal_pos[0], goal_pos[1]], dtype=np.float32)

    def get_next_move(self, current_pos: tuple, goal_pos: tuple) -> str:
        """Select action using epsilon-greedy policy"""
        if random.random() > self.epsilon:
            with torch.no_grad():
                state = torch.FloatTensor(self.get_state(current_pos, goal_pos)).to(self.device)
                q_values = self.policy_net(state)
                action = q_values.max(0)[1].item()
        else:
            action = random.randrange(self.action_size)
            
        # Decay epsilon
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
        return self.action_map[action]

    def train(self, batch_size: int):
        """Train the network using experience replay"""
        if len(self.memory) < batch_size:
            return

        # Sample batch from memory
        states, actions, rewards, next_states, dones = self.memory.sample(batch_size)
        
        # Convert to tensors
        states = torch.FloatTensor(states).to(self.device)
        actions = torch.LongTensor(actions).to(self.device)
        rewards = torch.FloatTensor(rewards).to(self.device)
        next_states = torch.FloatTensor(next_states).to(self.device)
        dones = torch.FloatTensor(dones).to(self.device)

        # Compute current Q values
        current_q_values = self.policy_net(states).gather(1, actions.unsqueeze(1))
        
        # Compute next Q values
        with torch.no_grad():
            next_q_values = self.target_net(next_states).max(1)[0]
        
        # Compute target Q values
        target_q_values = rewards + (1 - dones) * self.gamma * next_q_values
        
        # Compute loss
        loss = nn.MSELoss()(current_q_values.squeeze(), target_q_values)
        
        # Optimize the model
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        # Update target network
        self.steps_done += 1
        if self.steps_done % self.target_update == 0:
            self.target_net.load_state_dict(self.policy_net.state_dict())

    def update(self, state, action, reward, next_state, done):
        """Store transition in replay memory"""
        action_idx = list(self.action_map.values()).index(action)
        self.memory.push(self.get_state(*state), action_idx, reward,
                        self.get_state(*next_state), done)
        
        # Train the network
        if len(self.memory) >= self.batch_size:
            self.train(self.batch_size)

    def save(self, path: str):
        """Save the model"""
        torch.save({
            'policy_net_state_dict': self.policy_net.state_dict(),
            'target_net_state_dict': self.target_net.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'epsilon': self.epsilon,
        }, path)

    def load(self, path: str):
        """Load the model"""
        checkpoint = torch.load(path)
        self.policy_net.load_state_dict(checkpoint['policy_net_state_dict'])
        self.target_net.load_state_dict(checkpoint['target_net_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.epsilon = checkpoint['epsilon']
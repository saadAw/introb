import os
import sys
# Add the project root directory to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.append(project_root)

import torch
import multiprocessing
import numpy as np
from tqdm import tqdm
from copy import deepcopy
import time

from src.environment.map import Map
from src.game.game_logic import GameLogic
from src.config.constants import GameState
from old.deep_q_learning import DQNAgent

class FastEnvironment:
    """A stripped-down version of the environment for fast training"""
    def __init__(self, map_size=(10, 10)):
        self.game_map = Map(0, 0)
        self.game_logic = GameLogic(map_size)
        self.reset()

    def reset(self):
        """Reset the environment"""
        self.game_map.load_map()
        self.current_pos = self.game_map.SPAWN_POS
        self.goal_pos = self.game_map.GOAL_POS
        self.game_logic.reset()
        return self.current_pos, self.goal_pos

    def step(self, action):
        """Execute one step in the environment"""
        old_pos = self.current_pos
        new_pos = list(old_pos)
        
        # Update position based on action
        if action == 'up':
            new_pos[1] -= 1
        elif action == 'down':
            new_pos[1] += 1
        elif action == 'left':
            new_pos[0] -= 1
        elif action == 'right':
            new_pos[0] += 1
            
        new_pos = tuple(new_pos)
        
        # Check if move is valid
        if self.game_map.is_valid_move(*new_pos):
            self.current_pos = new_pos
            
        # Calculate reward and check if done
        reward = self.game_logic.calculate_reward(old_pos, self.current_pos, self.goal_pos)
        done = (self.current_pos == self.goal_pos)  # Only done when reaching goal
        
        return self.current_pos, reward, done

def train_instance(instance_id, num_episodes, shared_dict):
    env = FastEnvironment()
    agent = DQNAgent(env.game_map)
    
    agent.epsilon_decay = 0.95
    agent.epsilon_min = 0.05
    agent.learning_rate = 0.001
    
    max_steps = 100
    best_reward = float('-inf')
    
    for episode in range(num_episodes):
        current_pos, goal_pos = env.reset()
        episode_reward = 0
        done = False
        steps = 0
        
        while not done and steps < max_steps:
            action = agent.get_next_move(current_pos, goal_pos)
            next_pos, reward, done = env.step(action)
            agent.update((current_pos, goal_pos), action, reward, (next_pos, goal_pos), done)
            current_pos = next_pos
            episode_reward += reward
            steps += 1
        
        if episode % 10 == 0:
            if episode_reward > best_reward:
                best_reward = episode_reward
                agent.save(f"models/dqn_agent_{instance_id}.pt")
                
            shared_dict[instance_id] = {
                'current_episode': episode,
                'metrics': agent.get_current_metrics(),
                'episode_reward': episode_reward,
                'best_reward': best_reward,
                'steps': steps,
                'epsilon': agent.epsilon
            }
            
            # Print summary only every 50 episodes
            if episode % 50 == 0:
                print(f"\nInstance {instance_id}, Episode {episode}")
                print(f"Best Reward: {best_reward:.2f}, Current Reward: {episode_reward:.2f}")
                print(f"Steps: {steps}, Epsilon: {agent.epsilon:.3f}")

    return agent
        
def train_parallel(num_instances=4, episodes_per_instance=500, visualize=True):
    """Train multiple DQN instances in parallel"""
    manager = multiprocessing.Manager()
    shared_dict = manager.dict()
    
    # Initialize shared dict with default values for each instance
    for i in range(num_instances):
        shared_dict[i] = {
            'current_episode': 0,
            'metrics': {},
            'episode_reward': 0,
            'best_reward': float('-inf'),
            'steps': 0,
            'epsilon': 1.0
        }
    
    num_cores = multiprocessing.cpu_count()
    num_fast_instances = min(num_instances - 1, num_cores * 4)
    
    processes = []
    
    if visualize:
        visual_process = multiprocessing.Process(
            target=visual_train_instance,
            args=(0, episodes_per_instance, shared_dict)
        )
        visual_process.start()
        processes.append(visual_process)
    
    for i in range(num_fast_instances):
        p = multiprocessing.Process(
            target=train_instance,
            args=(i + (1 if visualize else 0), episodes_per_instance, shared_dict)
        )
        p.start()
        processes.append(p)
    
    with tqdm(total=episodes_per_instance) as pbar:
        previous_episodes = 0
        while any(p.is_alive() for p in processes):
            if shared_dict:
                avg_episodes = np.mean([m['current_episode'] for m in shared_dict.values()])
                if avg_episodes > previous_episodes:
                    pbar.update(int(avg_episodes - previous_episodes))
                    previous_episodes = avg_episodes
                
                # Calculate summary statistics
                best_reward = max([m.get('best_reward', float('-inf')) for m in shared_dict.values()])
                current_rewards = [m.get('episode_reward', 0) for m in shared_dict.values()]
                avg_reward = np.mean(current_rewards)
                max_reward = max(current_rewards)
                
                pbar.set_description(
                    f"Best Ever: {best_reward:.1f} | "
                    f"Current Avg: {avg_reward:.1f} | "
                    f"Current Best: {max_reward:.1f}"
                )
            
            time.sleep(0.1)
    
    for p in processes:
        p.join()
        
    # Find best model
    best_success_rate = -1
    best_model_path = None
    
    for i in range(num_instances):
        model_path = f"models/dqn_agent_{i}.pt"
        try:
            if os.path.exists(model_path):
                checkpoint = torch.load(model_path, weights_only=True)
                success_rate = checkpoint['metrics']['success_rate']
                
                if success_rate > best_success_rate:
                    best_success_rate = success_rate
                    best_model_path = model_path
        except Exception as e:
            print(f"Error loading model {model_path}: {e}")
            continue
    
    if best_model_path:
        print(f"Best success rate: {best_success_rate:.2%}")
        final_path = "models/best_dqn_agent.pt"
        import shutil
        shutil.copy2(best_model_path, final_path)
        return final_path
    else:
        print("No successful models were found")
        return None
    
        
def visual_train_instance(instance_id, num_episodes, shared_dict):
    """Train one instance with visualization but MUCH faster"""
    import pygame
    from src.game.game_runner import GameRunner
    
    pygame.init()
    game = GameRunner()
    game.setup_game()
    
    agent = DQNAgent(game.game_map)
    agent.epsilon_decay = 0.90  # Much faster exploration decay
    agent.epsilon_min = 0.01
    agent.learning_rate = 0.005  # Higher learning rate
    
    # Extreme speed settings
    SPEED_MULTIPLIER = 200  # Run 200 steps before visualizing
    VISUALIZATION_FREQUENCY = 20  # Only show every 20th frame
    
    try:
        for episode in range(num_episodes):
            game.setup_game()
            current_pos = game.robot.x, game.robot.y
            goal_pos = game.game_map.goal_pos
            done = False
            steps = 0
            max_steps = 50  # Limit episodes to 50 steps maximum
            
            while not done and steps < max_steps:
                # Minimal event handling
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                        pygame.quit()
                        return
                
                # Run multiple steps before visualization
                for _ in range(SPEED_MULTIPLIER):
                    if done:
                        break
                    
                    action = agent.get_next_move(current_pos, goal_pos)
                    old_pos = current_pos
                    game.robot.move(action, game.game_map)
                    current_pos = (game.robot.x, game.robot.y)
                    reward = game.game_logic.calculate_reward(old_pos, current_pos, goal_pos)
                    done = (current_pos == goal_pos) or (game.game_logic.time_remaining <= 0)
                    agent.update((old_pos, goal_pos), action, reward, (current_pos, goal_pos), done)
                    steps += 1
                
                if steps % VISUALIZATION_FREQUENCY == 0:
                    game.draw()
                    pygame.display.flip()
            
            # Update metrics less frequently
            if episode % 50 == 0:
                metrics = agent.get_current_metrics()
                shared_dict[instance_id] = {
                    'current_episode': episode,
                    'metrics': metrics
                }
        
        return agent
    except Exception as e:
        print(f"Error in visual training: {e}")
        pygame.quit()
        return None
            
if __name__ == "__main__":
    os.makedirs("models", exist_ok=True)
    
    # Train with fewer episodes but more focused learning
    print("Training agents...")
    best_model = train_parallel(num_instances=4, episodes_per_instance=500, visualize=True)
    
    if best_model:
        print("\nTraining complete! Best model saved at:", best_model)
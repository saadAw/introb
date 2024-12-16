# src/environment/robot.py
import pygame
from src.config.constants import COLORS

class Robot:
    def __init__(self, x, y, idle_path, walk_paths, cell_size, speed=1, cooldown=50):
        self.x = x
        self.y = y
        self.speed = speed
        self.cooldown = cooldown
        self.last_move_time = pygame.time.get_ticks()
        self.frame = 0
        self.facing_direction = 'up'  # Track which way the robot is facing
        self.game_logic = None
        
        # Store cell size
        self.cell_size = cell_size
        
        # Sprite size (2.5x cell size)
        self.sprite_size = int(self.cell_size * 2.5)
        
        # Adjust offsets for larger sprite
        self.offset_x = -self.sprite_size // 2 + self.cell_size // 2
        self.offset_y = -self.sprite_size // 2 + self.cell_size // 2
        
        # Load and scale images - we'll only use walk animations
        self.walk_images = {
            'down': self.load_walk_images(walk_paths['down']),
            'up': self.load_walk_images(walk_paths['up']),
            'left': self.load_walk_images(walk_paths['left']),
            'right': self.load_walk_images(walk_paths['right']),
        }
        # Use first frame of walk animation for each direction as idle
        self.idle_frames = {
            'down': self.walk_images['down'][0],
            'up': self.walk_images['up'][0],
            'left': self.walk_images['left'][0],
            'right': self.walk_images['right'][0],
        }
        self.current_image = self.idle_frames['up']

    def load_walk_images(self, folder_path):
        """Loads and scales all images for the walk animation."""
        images = []
        for i in range(60):
            try:
                image = pygame.image.load(f"{folder_path}/Armature_walk_{i:02}.png")
                image = pygame.transform.scale(image, (self.sprite_size, self.sprite_size))
                images.append(image)
            except pygame.error as e:
                print(f"Image not found: {folder_path}/Armature_walk_{i:02}.png")
                break
        return images
    
    def set_game_logic(self, game_logic):
        """Set reference to game logic for move tracking"""
        self.game_logic = game_logic

    def move(self, direction, game_map):
        """Handle robot movement and animation."""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_move_time >= self.cooldown:
            new_x, new_y = self.x, self.y
            old_pos = (self.x, self.y)
            moved = False
            
            # Handle movement and animation
            if direction == 'down':
                new_y += 1
                moved = True
            elif direction == 'up':
                new_y -= 1
                moved = True
            elif direction == 'left':
                new_x -= 1
                moved = True
            elif direction == 'right':
                new_x += 1
                moved = True
            
            if direction != 'idle':
                self.current_image = self.walk_images[direction][self.frame]
                self.facing_direction = direction
            else:
                self.current_image = self.idle_frames[self.facing_direction]
                self.frame = 0
            
            if moved and game_map.is_valid_move(new_x, new_y):
                self.x = new_x
                self.y = new_y
                game_map.place_robot(self.x, self.y)
                self.frame = (self.frame + 1) % len(self.walk_images[self.facing_direction])
                
                if self.game_logic:
                    new_pos = (new_x, new_y)
                    self.game_logic.calculate_reward(old_pos, new_pos, game_map.goal_pos)

            if direction != 'idle':  
                game_map.add_to_path((self.x, self.y), self.game_logic.current_algorithm)
            
            self.last_move_time = current_time

    def display(self, surface, offset_x=0):
        """Display the robot with corrected positioning"""
        position_x = offset_x + self.x * self.cell_size + self.offset_x
        position_y = self.y * self.cell_size + self.offset_y
        surface.blit(self.current_image, (position_x, position_y))
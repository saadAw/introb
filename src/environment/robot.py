import pygame
from src.environment.constants import COLORS, CELL_SIZE

class Robot:
    def __init__(self, x, y, idle_path, walk_paths, speed=1, cooldown=50):
        self.x = x
        self.y = y
        self.speed = speed
        self.cooldown = cooldown
        self.last_move_time = pygame.time.get_ticks()
        self.frame = 0
        self.facing_direction = 'up'  # Track which way the robot is facing
        
        # Sprite size (2.5x cell size)
        self.sprite_size = int(CELL_SIZE * 2.5)
        
        # Adjust offsets for larger sprite
        self.offset_x = -self.sprite_size // 2 + CELL_SIZE // 2
        self.offset_y = -self.sprite_size // 2 + CELL_SIZE // 2
        
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

    def move(self, direction, game_map):
        """Handle robot movement and animation."""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_move_time >= self.cooldown:
            new_x, new_y = self.x, self.y
            
            # Handle movement and animation
            if direction == 'down':
                new_y += 1
                self.current_image = self.walk_images['down'][self.frame]
                self.facing_direction = 'down'
            elif direction == 'up':
                new_y -= 1
                self.current_image = self.walk_images['up'][self.frame]
                self.facing_direction = 'up'
            elif direction == 'left':
                new_x -= 1
                self.current_image = self.walk_images['left'][self.frame]
                self.facing_direction = 'left'
            elif direction == 'right':
                new_x += 1
                self.current_image = self.walk_images['right'][self.frame]
                self.facing_direction = 'right'
            elif direction == 'idle':
                # Use the idle frame for current direction
                self.current_image = self.idle_frames[self.facing_direction]
                self.frame = 0
            
            # Update position if movement is valid
            if direction != 'idle' and game_map.is_valid_move(new_x, new_y):
                self.x = new_x
                self.y = new_y
                game_map.place_robot(self.x, self.y)
                # Update animation frame only when actually moving
                self.frame = (self.frame + 1) % len(self.walk_images[self.facing_direction])
            
            self.last_move_time = current_time

    def display(self, surface):
        """Display the robot with corrected positioning."""
        position_x = self.x * CELL_SIZE + self.offset_x
        position_y = self.y * CELL_SIZE + self.offset_y
        surface.blit(self.current_image, (position_x, position_y))
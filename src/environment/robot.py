import pygame
from src.environment.constants import COLORS

class Robot:  
    def __init__(self, x, y, idle_path, walk_paths, speed=1, cooldown=50):  
        self.x = x  
        self.y = y  
        self.speed = speed  
        self.cooldown = cooldown  
        self.last_move_time = pygame.time.get_ticks()  
        self.frame = 0  
        # Füge Offset-Werte hinzu  
        self.offset_x = -256  # -3 * 128  
        self.offset_y = -256  # -3 * 128

        # Lade die Idle- und Geh-Bilder
        self.idle_images = self.load_idle_images(idle_path)
        self.walk_images = {
            'down': self.load_walk_images(walk_paths['down']),
            'up': self.load_walk_images(walk_paths['up']),
            'left': self.load_walk_images(walk_paths['left']),
            'right': self.load_walk_images(walk_paths['right']),
        }
        self.current_image = self.idle_images[0]  # Initialisiere mit Idle-Animation

    def load_idle_images(self, folder_path):
        """Lädt alle Bilder für die Idle-Animation."""
        images = []
        for i in range(60):  # Anzahl der Frames in der Animation
            try:
                image = pygame.image.load(f"{folder_path}/Armature_idle_{i:02}.png")
                images.append(image)  # Keine Skalierung hier!
            except pygame.error as e:
                print(f"Bild nicht gefunden: {folder_path}/Armature_idle_{i:02}.png")
                break
        return images

    def load_walk_images(self, folder_path):
        """Lädt alle Bilder für die Geh-Animation."""
        images = []
        for i in range(60):  # Anzahl der Frames in der Animation
            try:
                image = pygame.image.load(f"{folder_path}/Armature_walk_{i:02}.png")
                images.append(image)  # Keine Skalierung hier!
            except pygame.error as e:
                print(f"Bild nicht gefunden: {folder_path}/Armature_walk_{i:02}.png")
                break
        return images

    def move(self, direction, game_map):  
        current_time = pygame.time.get_ticks()  
        if current_time - self.last_move_time >= self.cooldown:  
            new_x, new_y = self.x, self.y  

            if direction == 'down':  
                new_y += 1  
                self.current_image = self.walk_images['down'][self.frame]  
            elif direction == 'up':  
                new_y -= 1  
                self.current_image = self.walk_images['up'][self.frame]  
            elif direction == 'left':  
                new_x -= 1  
                self.current_image = self.walk_images['left'][self.frame]  
            elif direction == 'right':  
                new_x += 1  
                self.current_image = self.walk_images['right'][self.frame]  
            elif direction == 'idle':  
                self.current_image = self.idle_images[self.frame]  

            if direction != 'idle' and game_map.is_valid_move(new_x, new_y):  
                self.x = new_x  # Hier war der Fehler (self.x, new_y = new_x, new_y)  
                self.y = new_y  # Separate Zuweisungen  
                game_map.place_robot(self.x, self.y)  

            self.frame = (self.frame + 1) % len(self.walk_images['down'])  
            self.last_move_time = current_time

    def display(self, surface):  
        """Zeigt das aktuelle Bild des Roboters auf dem Bildschirm an."""  
        position_x = self.x * 128 + self.offset_x  # Füge Offset hinzu  
        position_y = self.y * 128 + self.offset_y  # Füge Offset hinzu  

        surface.blit(self.current_image, (position_x, position_y))



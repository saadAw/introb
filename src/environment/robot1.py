import pygame

class Robot:
    def __init__(self, x, y, idle_path, walk_paths, speed=1, cooldown=50):
        self.x = x
        self.y = y
        self.speed = speed
        self.cooldown = cooldown
        self.last_move_time = pygame.time.get_ticks()  # Zeit der letzten Bewegung
        self.frame = 0  # Animations-Frame-Index

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

    def move(self, direction):
        """Bewegt den Roboter in die angegebene Richtung oder wechselt den Animationszustand."""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_move_time >= self.cooldown:
            if direction == 'down':
                self.y += 1
                self.current_image = self.walk_images['down'][self.frame]
            elif direction == 'up':
                self.y -= 1
                self.current_image = self.walk_images['up'][self.frame]
            elif direction == 'left':
                self.x -= 1
                self.current_image = self.walk_images['left'][self.frame]
            elif direction == 'right':
                self.x += 1
                self.current_image = self.walk_images['right'][self.frame]
            elif direction == 'idle':
                self.current_image = self.idle_images[self.frame]

            # Animation-Frame erhöhen
            self.frame = (self.frame + 1) % len(self.walk_images['down'])

            # Aktualisiere die Zeit der letzten Bewegung
            self.last_move_time = current_time

    def display(self, surface):
        """Zeigt das aktuelle Bild des Roboters auf dem Bildschirm an."""
        surface.blit(self.current_image, (self.x * 128, self.y * 128))  # Position auf die Zellen abgestimmt

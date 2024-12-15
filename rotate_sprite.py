import pygame
import os

def rotate_images(source_folder, destination_folder, angle):
    """Rotiert alle Bilder im source_folder um den gegebenen Winkel und speichert sie im destination_folder."""
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    
    for i in range(60):  # Angenommene Anzahl der Frames in der Animation
        try:
            image = pygame.image.load(f"{source_folder}/Armature_walk_{i:02}.png")
            rotated_image = pygame.transform.rotate(image, angle)
            pygame.image.save(rotated_image, f"{destination_folder}/Armature_walk_{i:02}.png")
        except pygame.error as e:
            print(f"Fehler beim Laden des Bildes: {source_folder}/Armature_walk_{i:02}.png")
            break

# Beispielaufrufe für die Rotation:
rotate_images("C:/Uni/introb/images/walk60/down", "C:/Uni/introb/images/walk60/up", 180)  # Für "up"
rotate_images("C:/Uni/introb/images/walk60/down", "C:/Uni/introb/images/walk60/left", -90)  # Für "left"
rotate_images("C:/Uni/introb/images/walk60/down", "C:/Uni/introb/images/walk60/right", 90) # Für "right"
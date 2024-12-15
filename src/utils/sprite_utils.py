import pygame
import os

def load_sprite_sheet(image_folder_path, num_frames, frame_width, frame_height, prefix):
    """
    Lädt alle Frames eines Spritesheets mit dem angegebenen Prefix (z. B. 'idle' oder 'walk').

    :param image_folder_path: Pfad zum Ordner mit den Sprite-Bildern
    :param num_frames: Anzahl der Frames im Sprite-Sheet
    :param frame_width: Breite jedes Frames
    :param frame_height: Höhe jedes Frames
    :param prefix: Prefix für die Datei (z. B. 'Armature_idle_' oder 'Armature_walk_')
    :return: Liste von Pygame-Oberflächen (Frames)
    """
    frames = []
    for i in range(num_frames):
        image_name = f"{prefix}{i:02d}.png"  # z. B. Armature_walk_00.png oder Armature_idle_00.png
        image_path = os.path.join(image_folder_path, image_name)
        try:
            sprite = pygame.image.load(image_path).convert_alpha()
            frames.append(sprite)
        except pygame.error as e:
            print(f"Fehler beim Laden von {image_path}: {e}")
    return frames

def rotate_sprite(sprite, angle):
    """
    Rotiert ein Pygame-Bild um den angegebenen Winkel.

    :param sprite: Das Bild, das rotiert werden soll
    :param angle: Der Winkel, um den das Bild rotiert werden soll (im Uhrzeigersinn)
    :return: Das rotierte Bild
    """
    return pygame.transform.rotate(sprite, angle)

def flip_sprite(sprite, flip_horizontally=False, flip_vertically=False):
    """
    Spiegelt ein Pygame-Bild horizontal und/oder vertikal.

    :param sprite: Das Bild, das gespiegelt werden soll
    :param flip_horizontally: True, wenn das Bild horizontal gespiegelt werden soll
    :param flip_vertically: True, wenn das Bild vertikal gespiegelt werden soll
    :return: Das gespiegelte Bild
    """
    return pygame.transform.flip(sprite, flip_horizontally, flip_vertically)

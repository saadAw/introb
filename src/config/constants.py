from enum import Enum
import pygame

class GameState(Enum):
    """Game states enumeration"""
    PLAYING = "playing"
    WIN = "win"
    LOSE = "lose"
    RESET = "reset"

class MapSymbols:
    """Map tile symbols"""
    FREE = 0
    OBSTACLE = 1
    ROBOT = 'R'
    GOAL = 'G'

# Get screen info
pygame.init()
info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h

# UI Configuration
UI_PANEL_WIDTH = 300
PADDING = 20

# Base cell size
BASE_CELL_SIZE = 32

# Function to calculate dimensions based on maze size
def calculate_dimensions(maze_width, maze_height):
    """Calculate appropriate dimensions based on maze size and screen resolution"""
    # Calculate available space
    available_width = SCREEN_WIDTH - UI_PANEL_WIDTH - PADDING * 2
    available_height = SCREEN_HEIGHT - PADDING * 2
    
    # Calculate cell size
    cell_width = available_width // maze_width
    cell_height = available_height // maze_height
    
    # Use the smaller of the two to ensure fit, with a minimum size
    cell_size = max(min(cell_width, cell_height, BASE_CELL_SIZE), 4)
    
    # Calculate actual dimensions
    game_width = maze_width * cell_size
    game_height = maze_height * cell_size
    
    return {
        'cell_size': cell_size,
        'window_width': game_width + UI_PANEL_WIDTH,
        'window_height': game_height,
        'map_width': maze_width,
        'map_height': maze_height
    }

# Game settings
ANIMATION_FRAMES = 60
TIME_LIMIT = 180
FPS = 30

# Colors
COLORS = {
    'WHITE': (255, 255, 255),
    'BLACK': (0, 0, 0),
    'RED': (255, 0, 0),
    'GREEN': (0, 255, 0),
    'GRID': (200, 200, 200),
    'TIMER_WARNING': (255, 165, 0),
    'UI_BACKGROUND': (240, 240, 240),
    'UI_TEXT': (50, 50, 50),
    'UI_HEADER': (70, 70, 70)
}
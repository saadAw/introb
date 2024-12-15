from enum import Enum

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

# Game Configuration
CELL_SIZE = 128
ANIMATION_FRAMES = 60
TIME_LIMIT = 60  # seconds
FPS = 30

# Colors
COLORS = {
    'WHITE': (255, 255, 255),
    'BLACK': (0, 0, 0),
    'RED': (255, 0, 0),
    'GREEN': (0, 255, 0),
    'GRID': (200, 200, 200),
    'TIMER_WARNING': (255, 165, 0)  # Orange for low time warning
}

# constants.py
from enum import Enum

# Spielzustände
class GameState(Enum):
    PLAYING = "playing"
    WIN = "win"
    LOSE = "lose"
    RESET = "reset"

# Kartensymbole
class MapSymbols:
    FREE = 0
    OBSTACLE = 1
    ROBOT = 'R'
    GOAL = 'G'

# Spielkonfiguration
CELL_SIZE = 128
ANIMATION_FRAMES = 60
TIME_LIMIT = 60  # Sekunden
FPS = 30

# Farben
COLORS = {
    'WHITE': (255, 255, 255),
    'BLACK': (0, 0, 0),
    'RED': (255, 0, 0),
    'GREEN': (0, 255, 0),
    'GRID': (200, 200, 200),
    'TIMER_WARNING': (255, 165, 0)  # Orange für wenig Zeit
}
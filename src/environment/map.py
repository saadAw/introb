import pygame  
from typing import Tuple  

from src.config.constants import MapSymbols, COLORS, calculate_dimensions  
from src.environment.mazes.maze_data import LAYOUT  
from src.config.types import AlgorithmType

class Map:  
    """Represents the game map with a single fixed layout"""    

    # Klassenkonstanten am Anfang der Klasse definieren    
    ALGORITHM_COLORS = {    
        AlgorithmType.MANUAL: COLORS['PATH_MANUAL'],    
        AlgorithmType.ASTAR: COLORS['PATH_ASTAR'],    
        AlgorithmType.DIJKSTRA: COLORS['PATH_DIJKSTRA'],
        AlgorithmType.GBFS: COLORS['PATH_GBFS'],
        AlgorithmType.BFS: COLORS['PATH_BFS'],
        AlgorithmType.QL: COLORS['PATH_QL'],    
        AlgorithmType.DQN: COLORS['PATH_DQN']    
 
    }    
    PATH_SCALE = 0.6  # 60% der Zellgröße    

    def __init__(self, width: int, height: int):
        """Initialize map with given dimensions"""
        # Get maze dimensions from LAYOUT
        self.maze_height = len(LAYOUT)
        self.maze_width = len(LAYOUT[0]) if LAYOUT else 0
        
        print(f"Maze dimensions: {self.maze_width}x{self.maze_height}")
        
        # Calculate appropriate dimensions
        dimensions = calculate_dimensions(self.maze_width, self.maze_height)
        
        # Set class attributes
        self.width = dimensions['map_width']
        self.height = dimensions['map_height']
        self.cell_size = dimensions['cell_size']
        self.screen_width = self.width * self.cell_size
        self.screen_height = self.height * self.cell_size
        
        # Set spawn and goal positions 
        self.SPAWN_POS = (1, self.height - 2) # near bottom left
        self.GOAL_POS = (self.width - 2, 1) # near top right
        self.OPTIMAL_PATH_LENGTH = max(self.width, self.height) * 2
        
        # Initialize positions
        self.robot_pos = None
        self.goal_pos = None
        
        # Initialize the grid
        self.grid = [[MapSymbols.FREE for _ in range(self.width)] 
                    for _ in range(self.height)]
        
        self.algorithm_paths = {  
            AlgorithmType.MANUAL: set(),  
            AlgorithmType.ASTAR: set(),  
            AlgorithmType.DIJKSTRA: set(),  
            AlgorithmType.QL: set(),  
            AlgorithmType.DQN: set()  
        }

        self.path_grid = {}      # Speichert {(x,y): AlgorithmType} für besetzte Felder  
        self.paths = {}          # Speichert {AlgorithmType: set(positions)} für jeden Algorithmus
        
        self.load_map()

    def load_map(self) -> None:
        """Load the fixed map layout"""
        try:
            for y, row in enumerate(LAYOUT):
                for x, cell in enumerate(row):
                    self.grid[y][x] = MapSymbols.OBSTACLE if cell == 1 else MapSymbols.FREE
            
            # Find valid spawn and goal positions
            if not self.is_valid_move(*self.SPAWN_POS):
                self.SPAWN_POS = self._find_valid_position(start_from_bottom=True)
            
            if not self.is_valid_move(*self.GOAL_POS):
                self.GOAL_POS = self._find_valid_position(start_from_bottom=False)
            
            # Place robot and goal
            self.place_robot(*self.SPAWN_POS)
            self.place_goal(*self.GOAL_POS)
            
        except Exception as e:
            print(f"Error loading maze: {e}")
            raise

    def _find_valid_position(self, start_from_bottom=True) -> Tuple[int, int]:
        """Find a valid position in the maze"""
        y_range = range(self.height - 1, -1, -1) if start_from_bottom else range(self.height)
        
        for y in y_range:
            for x in range(self.width):
                if self.is_valid_move(x, y):
                    return (x, y)
        
        raise Exception("No valid position found in maze")

    def place_robot(self, x: int, y: int) -> Tuple[int, int]:
        """Place robot at the specified position"""
        if self.robot_pos:
            old_x, old_y = self.robot_pos
            self.grid[old_y][old_x] = MapSymbols.FREE

        self.grid[y][x] = MapSymbols.ROBOT
        self.robot_pos = (x, y)
        return (x, y)

    def place_goal(self, x: int, y: int) -> None:
        """Place goal at the specified position"""
        if self.goal_pos:
            old_x, old_y = self.goal_pos
            self.grid[old_y][old_x] = MapSymbols.FREE

        self.grid[y][x] = MapSymbols.GOAL
        self.goal_pos = (x, y)

    def draw_map(self, surface, offset_x=0):    
        """Draw the map with all elements on given surface"""    
        self._draw_cells(surface, offset_x)    
        self._draw_grid(surface, offset_x)    

        # Zeichne alle markierten Felder gemäß path_grid  
        for pos, algo_type in self.path_grid.items():  
            x, y = pos  
            color = self.ALGORITHM_COLORS[algo_type]  
            rect = pygame.Rect(  
                offset_x + x * self.cell_size,  
                y * self.cell_size,  
                self.cell_size,  
                self.cell_size  
            )  
            # Verwende PATH_SCALE für die Größe  
            pygame.draw.rect(surface, color, rect.inflate(  
                -self.cell_size * self.PATH_SCALE,  
                -self.cell_size * self.PATH_SCALE  
            ))

    def _draw_cells(self, surface, offset_x=0):
        """Draw all cells (private helper method)"""
        for y in range(self.height):
            for x in range(self.width):
                cell_x = offset_x + x * self.cell_size
                cell_y = y * self.cell_size
                cell_rect = (cell_x, cell_y, self.cell_size, self.cell_size)
                
                cell_type = self.grid[y][x]
                color = {
                    MapSymbols.FREE: COLORS['WHITE'],
                    MapSymbols.OBSTACLE: COLORS['BLACK'],
                    MapSymbols.GOAL: COLORS['GREEN'],
                    MapSymbols.ROBOT: COLORS['RED']
                }.get(cell_type, COLORS['WHITE'])
                
                pygame.draw.rect(surface, color, cell_rect)

    def _draw_grid(self, surface, offset_x=0):
        """Draw grid lines (private helper method)"""
        for x in range(self.width + 1):
            start_pos = (offset_x + x * self.cell_size, 0)
            end_pos = (offset_x + x * self.cell_size, self.screen_height)
            pygame.draw.line(surface, COLORS['GRID'], start_pos, end_pos)

        for y in range(self.height + 1):
            start_pos = (offset_x, y * self.cell_size)
            end_pos = (offset_x + self.screen_width, y * self.cell_size)
            pygame.draw.line(surface, COLORS['GRID'], start_pos, end_pos)

    def is_valid_move(self, x: int, y: int) -> bool:
        """Check if position is valid for movement"""
        return (0 <= x < self.width and
                0 <= y < self.height and
                self.grid[y][x] != MapSymbols.OBSTACLE)
    
    def add_to_path(self, pos: Tuple[int, int], algorithm: AlgorithmType):  
        """Add position to algorithm's path and update path_grid"""  
        if algorithm not in self.paths:  
            self.paths[algorithm] = set()  

        self.paths[algorithm].add(pos)  
        self.path_grid[pos] = algorithm  # Überschreibt automatisch existierende Pfade  

    def clear_algorithm_path(self, algorithm: AlgorithmType):  
        """Clear path for specific algorithm"""  
        if algorithm in self.paths:  
            # Entferne alle Positionen dieses Algorithmus aus dem path_grid  
            positions_to_remove = []  
            for pos, algo in self.path_grid.items():  
                if algo == algorithm:  
                    positions_to_remove.append(pos)  

            for pos in positions_to_remove:  
                del self.path_grid[pos]  

            # Lösche den Pfad aus paths  
            self.paths[algorithm].clear()
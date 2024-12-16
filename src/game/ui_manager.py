import pygame
from src.config.constants import COLORS, FPS, GameState

class UIManager:
    """Handles all UI rendering and management"""
    def __init__(self):
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.padding = 5
        
    def draw_game_ui(self, surface, game_logic, current_algorithm):
        """Draw all UI elements"""
        self._draw_time(surface, game_logic)
        self._draw_score(surface, game_logic)
        self._draw_algorithm_info(surface, current_algorithm)
        self._draw_controls_info(surface)
        
        if game_logic.state != GameState.PLAYING:
            self._draw_game_state(surface, game_logic)

    def _draw_time(self, surface, game_logic):
        """Draw time remaining"""
        time_text = f"Time: {game_logic.time_remaining // FPS}"
        color = COLORS['TIMER_WARNING'] if game_logic.time_remaining < 10 * FPS else COLORS['BLACK']
        time_surface = self.font.render(time_text, True, color)
        
        pygame.draw.rect(surface, COLORS['WHITE'],
                        (5, 5, time_surface.get_width() + 2*self.padding,
                         time_surface.get_height() + 2*self.padding))
        surface.blit(time_surface, (10, 10))

    def _draw_score(self, surface, game_logic):
        """Draw score and moves"""
        score_text = f"Score: {game_logic.score} | Moves: {game_logic.moves_made}"
        score_surface = self.font.render(score_text, True, COLORS['BLACK'])
        
        pygame.draw.rect(surface, COLORS['WHITE'],
                        (5, 45, score_surface.get_width() + 2*self.padding,
                         score_surface.get_height() + 2*self.padding))
        surface.blit(score_surface, (10, 50))

    def _draw_algorithm_info(self, surface, current_algorithm):
        """Draw current algorithm information"""
        algo_text = f"Current Mode: {current_algorithm.value}"
        algo_surface = self.font.render(algo_text, True, COLORS['BLACK'])
        
        pygame.draw.rect(surface, COLORS['WHITE'],
                        (5, 85, algo_surface.get_width() + 2*self.padding,
                         algo_surface.get_height() + 2*self.padding))
        surface.blit(algo_surface, (10, 90))

    def _draw_controls_info(self, surface):
        """Draw control information"""
        controls = [
            "Controls:",
            "1: Manual Mode",
            "2: Dijkstra Algorithm",
            "3: A* Algorithm (Coming Soon)",
            "4: DQN (Coming Soon)",
            "5: PPO (Coming Soon)",
            "R: Reset Game",
            "ESC: Quit"
        ]
        
        start_y = 130
        max_width = 0
        surfaces = []
        
        # Prepare all text surfaces
        for text in controls:
            text_surface = self.small_font.render(text, True, COLORS['BLACK'])
            surfaces.append(text_surface)
            max_width = max(max_width, text_surface.get_width())
        
        # Draw background rectangle
        total_height = len(controls) * 25  # 25 pixels per line
        pygame.draw.rect(surface, COLORS['WHITE'],
                        (5, start_y, max_width + 2*self.padding,
                         total_height + 2*self.padding))
        
        # Draw all text
        for i, text_surface in enumerate(surfaces):
            surface.blit(text_surface, (10, start_y + 5 + i * 25))

    def _draw_game_state(self, surface, game_logic):
        """Draw game state message"""
        state_text = f"Game {game_logic.state.value}! Press R to restart"
        state_surface = self.font.render(state_text, True, COLORS['BLACK'])
        
        x = surface.get_width() // 2 - state_surface.get_width() // 2
        y = surface.get_height() // 2 - state_surface.get_height() // 2
        
        pygame.draw.rect(surface, COLORS['WHITE'],
                        (x - self.padding, y - self.padding,
                         state_surface.get_width() + 2*self.padding,
                         state_surface.get_height() + 2*self.padding))
        surface.blit(state_surface, (x, y))

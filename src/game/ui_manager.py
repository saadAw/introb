import pygame
from src.config.constants import COLORS, FPS, GameState, UI_PANEL_WIDTH, PADDING

class UIManager:
    """Handles all UI rendering and management"""
    def __init__(self):
        self.font_large = pygame.font.Font(None, 40)
        self.font = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        self.padding = PADDING
        
    def draw_game_ui(self, surface, game_logic, current_algorithm):
        """Draw all UI elements in the left panel"""
        # Draw UI panel background
        panel_rect = pygame.Rect(0, 0, UI_PANEL_WIDTH, surface.get_height())
        pygame.draw.rect(surface, COLORS['UI_BACKGROUND'], panel_rect)
        pygame.draw.line(surface, COLORS['GRID'], 
                        (UI_PANEL_WIDTH, 0), 
                        (UI_PANEL_WIDTH, surface.get_height()), 2)

        current_y = self.padding
        
        # Game title
        title_surf = self.font_large.render("Robot Navigation", True, COLORS['UI_HEADER'])
        surface.blit(title_surf, (self.padding, current_y))
        current_y += title_surf.get_height() + self.padding

        # Current mode
        current_y = self._draw_section_header("Current Mode", surface, current_y)
        mode_surf = self.font.render(current_algorithm.value, True, COLORS['UI_TEXT'])
        surface.blit(mode_surf, (self.padding, current_y))
        current_y += mode_surf.get_height() + self.padding * 2

        # Time and Score section
        current_y = self._draw_section_header("Statistics", surface, current_y)
        
        # Time
        time_color = COLORS['TIMER_WARNING'] if game_logic.time_remaining < 10 * FPS else COLORS['UI_TEXT']
        time_surf = self.font.render(f"Time: {game_logic.time_remaining // FPS}s", True, time_color)
        surface.blit(time_surf, (self.padding, current_y))
        current_y += time_surf.get_height() + self.padding

        # Score and moves
        score_surf = self.font.render(f"Score: {game_logic.score}", True, COLORS['UI_TEXT'])
        surface.blit(score_surf, (self.padding, current_y))
        current_y += score_surf.get_height() + 5

        moves_surf = self.font.render(f"Moves: {game_logic.moves_made}", True, COLORS['UI_TEXT'])
        surface.blit(moves_surf, (self.padding, current_y))
        current_y += moves_surf.get_height() + self.padding * 2

        # Controls section
        current_y = self._draw_section_header("Controls", surface, current_y)
        controls = [
            "1: Manual Mode",
            "2: A* Algorithm",
            "3: Dijkstra Algorithm",
            "4: Q-Learning",
            "5: Deep Q-Learning",
            "",
            "Arrow Keys: Move",
            "R: Reset Game",
            "ESC: Quit"
        ]

        
        for control in controls:
            if control:  # If not empty string
                control_surf = self.font_small.render(control, True, COLORS['UI_TEXT'])
                surface.blit(control_surf, (self.padding, current_y))
                current_y += control_surf.get_height() + 5
            else:  # Empty string means add extra spacing
                current_y += 10

        # Draw game state if not playing
        if game_logic.state != GameState.PLAYING:
            self._draw_game_state(surface, game_logic)

    def _draw_section_header(self, text, surface, y):
        """Helper to draw section headers with consistent styling"""
        pygame.draw.line(surface, COLORS['GRID'], 
                        (self.padding, y), 
                        (UI_PANEL_WIDTH - self.padding, y), 1)
        y += 5
        header_surf = self.font.render(text, True, COLORS['UI_HEADER'])
        surface.blit(header_surf, (self.padding, y))
        y += header_surf.get_height() + 5
        pygame.draw.line(surface, COLORS['GRID'], 
                        (self.padding, y), 
                        (UI_PANEL_WIDTH - self.padding, y), 1)
        return y + self.padding

    def _draw_game_state(self, surface, game_logic):
        """Draw game state message in the center of the game area"""
        state_text = f"Game {game_logic.state.value}! Press R to restart"
        state_surf = self.font_large.render(state_text, True, COLORS['BLACK'])
        
        # Calculate position to center on game area, not including UI panel
        game_area_center_x = UI_PANEL_WIDTH + (surface.get_width() - UI_PANEL_WIDTH) // 2
        game_area_center_y = surface.get_height() // 2
        
        # Create background rectangle
        rect_width = state_surf.get_width() + self.padding * 2
        rect_height = state_surf.get_height() + self.padding * 2
        rect = pygame.Rect(
            game_area_center_x - rect_width // 2,
            game_area_center_y - rect_height // 2,
            rect_width,
            rect_height
        )
        
        # Draw background and text
        pygame.draw.rect(surface, COLORS['WHITE'], rect)
        surface.blit(state_surf, (
            game_area_center_x - state_surf.get_width() // 2,
            game_area_center_y - state_surf.get_height() // 2
        ))
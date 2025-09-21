import pygame
import json
import os
import subprocess
import sys
from datetime import datetime

# Initialize Pygame
pygame.init()

# Game constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (46, 125, 50)
LIGHT_GREEN = (129, 199, 132)
RED = (211, 47, 47)
BLUE = (25, 118, 210)
LIGHT_BLUE = (100, 181, 246)
YELLOW = (255, 193, 7)
PURPLE = (156, 39, 176)
LIGHT_GRAY = (245, 245, 245)
DARK_GRAY = (100, 100, 100)
PINK = (233, 30, 99)

class GameCard:
    def __init__(self, x, y, width, height, game_info):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.game_info = game_info
        self.hovered = False
        self.hover_scale = 1.0
        self.hover_target = 1.0
        
    def update(self, mouse_pos):
        # Check if mouse is over this card
        was_hovered = self.hovered
        self.hovered = (self.x <= mouse_pos[0] <= self.x + self.width and
                       self.y <= mouse_pos[1] <= self.y + self.height)
        
        # Animate hover effect
        self.hover_target = 1.05 if self.hovered else 1.0
        self.hover_scale += (self.hover_target - self.hover_scale) * 0.1
        
    def draw(self, screen, fonts):
        # Calculate scaled dimensions
        scaled_width = int(self.width * self.hover_scale)
        scaled_height = int(self.height * self.hover_scale)
        scaled_x = self.x + (self.width - scaled_width) // 2
        scaled_y = self.y + (self.height - scaled_height) // 2
        
        # Draw card background
        bg_color = self.game_info['color']
        if self.hovered:
            # Lighten color on hover
            bg_color = tuple(min(255, c + 30) for c in bg_color)
            
        pygame.draw.rect(screen, bg_color, (scaled_x, scaled_y, scaled_width, scaled_height), border_radius=20)
        pygame.draw.rect(screen, BLACK, (scaled_x, scaled_y, scaled_width, scaled_height), 3, border_radius=20)
        
        # Draw game icon
        icon_font = fonts['large']
        icon_surface = icon_font.render(self.game_info['icon'], True, WHITE)
        icon_rect = icon_surface.get_rect(center=(scaled_x + scaled_width // 2, scaled_y + 60))
        screen.blit(icon_surface, icon_rect)
        
        # Draw game title
        title_font = fonts['subtitle']
        title_surface = title_font.render(self.game_info['title'], True, WHITE)
        title_rect = title_surface.get_rect(center=(scaled_x + scaled_width // 2, scaled_y + 120))
        screen.blit(title_surface, title_rect)
        
        # Draw description
        desc_font = fonts['small']
        desc_lines = self.wrap_text(self.game_info['description'], 35)
        y_offset = 150
        for line in desc_lines[:3]:  # Max 3 lines
            line_surface = desc_font.render(line, True, WHITE)
            line_rect = line_surface.get_rect(center=(scaled_x + scaled_width // 2, scaled_y + y_offset))
            screen.blit(line_surface, line_rect)
            y_offset += 20
        
        # Draw progress/stats if available
        if 'stats' in self.game_info:
            stats = self.game_info['stats']
            stats_y = scaled_y + scaled_height - 80
            
            # High score
            if 'high_score' in stats and stats['high_score'] > 0:
                score_text = f"Best: {stats['high_score']:,}"
                score_surface = desc_font.render(score_text, True, YELLOW)
                score_rect = score_surface.get_rect(center=(scaled_x + scaled_width // 2, stats_y))
                screen.blit(score_surface, score_rect)
                stats_y += 20
            
            # Games played
            if 'games_played' in stats and stats['games_played'] > 0:
                games_text = f"Played: {stats['games_played']} times"
                games_surface = desc_font.render(games_text, True, LIGHT_BLUE)
                games_rect = games_surface.get_rect(center=(scaled_x + scaled_width // 2, stats_y))
                screen.blit(games_surface, games_rect)
        
        # Draw "PLAY" button
        button_width = 80
        button_height = 30
        button_x = scaled_x + (scaled_width - button_width) // 2
        button_y = scaled_y + scaled_height - 45
        
        play_color = WHITE if not self.hovered else YELLOW
        pygame.draw.rect(screen, play_color, (button_x, button_y, button_width, button_height), border_radius=15)
        pygame.draw.rect(screen, BLACK, (button_x, button_y, button_width, button_height), 2, border_radius=15)
        
        play_text = fonts['text'].render("PLAY", True, bg_color)
        play_rect = play_text.get_rect(center=(button_x + button_width // 2, button_y + button_height // 2))
        screen.blit(play_text, play_rect)
        
    def wrap_text(self, text, max_chars):
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line + " " + word) <= max_chars:
                if current_line:
                    current_line += " " + word
                else:
                    current_line = word
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def is_clicked(self, pos):
        return (self.x <= pos[0] <= self.x + self.width and
                self.y <= pos[1] <= self.y + self.height)

class PaisabuddyGameLauncher:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Paisabuddy Financial Learning Games")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Fonts
        self.fonts = {
            'title': pygame.font.Font(None, 64),
            'subtitle': pygame.font.Font(None, 32),
            'text': pygame.font.Font(None, 24),
            'small': pygame.font.Font(None, 18),
            'large': pygame.font.Font(None, 48)
        }
        
        # Game information
        self.games = [
            {
                'title': 'Budget Balance',
                'icon': '💰',
                'description': 'Catch income, avoid expenses! Learn to balance your financial life through fast-paced action.',
                'filename': 'budget_balance.py',
                'color': GREEN,
                'stats': self.load_game_stats('games/progress.json')
            },
            {
                'title': 'Investment Garden',
                'icon': '🌱',
                'description': 'Plant and grow investments! Watch your money flourish through compound interest.',
                'filename': 'investment_growth.py',
                'color': BLUE,
                'stats': self.load_game_stats('games/investment_progress.json')
            },
            {
                'title': 'Fraud Detective',
                'icon': '🛡️',
                'description': 'Spot scams and protect others! Become a master at identifying financial fraud.',
                'filename': 'fraud_detection.py',
                'color': RED,
                'stats': self.load_game_stats('games/fraud_progress.json')
            }
        ]
        
        # Create game cards
        self.game_cards = []
        self.setup_game_cards()
        
        # Overall statistics
        self.total_stats = self.calculate_total_stats()
        
    def load_game_stats(self, filename):
        """Load statistics for a specific game"""
        try:
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            pass
        return {}
    
    def calculate_total_stats(self):
        """Calculate overall statistics across all games"""
        total_games = 0
        total_score = 0
        achievements = []
        
        for game in self.games:
            stats = game['stats']
            if 'games_played' in stats:
                total_games += stats['games_played']
            if 'high_score' in stats:
                total_score += stats['high_score']
                
        # Check for achievements
        if total_games >= 10:
            achievements.append("🎮 Game Enthusiast")
        if total_games >= 50:
            achievements.append("🏆 Financial Gaming Master")
        if total_score >= 10000:
            achievements.append("💎 High Scorer")
            
        return {
            'total_games': total_games,
            'total_score': total_score,
            'achievements': achievements
        }
    
    def setup_game_cards(self):
        """Create game cards in a grid layout"""
        card_width = 300
        card_height = 350
        margin = 50
        
        # Calculate positions for centered grid
        total_width = len(self.games) * card_width + (len(self.games) - 1) * margin
        start_x = (SCREEN_WIDTH - total_width) // 2
        start_y = 200
        
        for i, game_info in enumerate(self.games):
            x = start_x + i * (card_width + margin)
            y = start_y
            card = GameCard(x, y, card_width, card_height, game_info)
            self.game_cards.append(card)
    
    def draw_background(self):
        """Draw animated background"""
        # Gradient background
        for y in range(SCREEN_HEIGHT):
            color_ratio = y / SCREEN_HEIGHT
            r = int(247 * (1 - color_ratio) + 234 * color_ratio)
            g = int(230 * (1 - color_ratio) + 211 * color_ratio)
            b = int(228 * (1 - color_ratio) + 207 * color_ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
            
        # Add some decorative elements
        import math
        time_offset = pygame.time.get_ticks() * 0.001
        for i in range(20):
            x = 50 + (i * 60) % SCREEN_WIDTH
            y = 50 + math.sin(time_offset + i * 0.5) * 20
            size = 3 + math.sin(time_offset * 2 + i) * 2
            color = (255, 255, 255, 100)
            pygame.draw.circle(self.screen, (255, 255, 255), (int(x), int(y)), int(size))
    
    def draw_header(self):
        """Draw the main header"""
        # Title
        title_text = self.fonts['title'].render("💰 PAISABUDDY GAMES 💰", True, PURPLE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title_text, title_rect)
        
        # Subtitle
        subtitle_text = self.fonts['subtitle'].render("Learn Financial Literacy Through Interactive Games!", True, BLUE)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, 120))
        self.screen.blit(subtitle_text, subtitle_rect)
    
    def draw_stats_panel(self):
        """Draw overall statistics panel"""
        panel_width = 350
        panel_height = 200
        panel_x = SCREEN_WIDTH - panel_width - 30
        panel_y = 30
        
        # Panel background
        pygame.draw.rect(self.screen, WHITE, (panel_x, panel_y, panel_width, panel_height), border_radius=15)
        pygame.draw.rect(self.screen, BLACK, (panel_x, panel_y, panel_width, panel_height), 2, border_radius=15)
        
        # Title
        stats_title = self.fonts['text'].render("📊 Your Progress", True, PURPLE)
        self.screen.blit(stats_title, (panel_x + 15, panel_y + 15))
        
        # Statistics
        y_offset = 50
        stats_list = [
            f"Games Played: {self.total_stats['total_games']}",
            f"Total Score: {self.total_stats['total_score']:,}",
            "",
            "🏅 Achievements:"
        ]
        
        for stat in stats_list:
            if stat:
                color = BLUE if ":" in stat else PURPLE
                stat_surface = self.fonts['small'].render(stat, True, color)
                self.screen.blit(stat_surface, (panel_x + 15, panel_y + y_offset))
            y_offset += 20
        
        # Draw achievements
        for achievement in self.total_stats['achievements']:
            achievement_surface = self.fonts['small'].render(f"  {achievement}", True, GREEN)
            self.screen.blit(achievement_surface, (panel_x + 15, panel_y + y_offset))
            y_offset += 18
            
        if not self.total_stats['achievements']:
            no_achievements = self.fonts['small'].render("  Play games to earn achievements!", True, DARK_GRAY)
            self.screen.blit(no_achievements, (panel_x + 15, panel_y + y_offset))
    
    def draw_instructions(self):
        """Draw instructions and tips"""
        instructions = [
            "🎮 Click on any game card to start playing",
            "🏆 Complete games to earn achievements and track progress",
            "💡 Each game teaches different financial skills:",
            "   • Budget Balance: Expense management",
            "   • Investment Garden: Compound interest & diversification", 
            "   • Fraud Detective: Security & scam awareness"
        ]
        
        y_start = SCREEN_HEIGHT - 150
        for i, instruction in enumerate(instructions):
            color = BLUE if instruction.startswith("🎮") or instruction.startswith("🏆") else DARK_GRAY
            font = self.fonts['text'] if not instruction.startswith("   •") else self.fonts['small']
            
            instruction_surface = font.render(instruction, True, color)
            self.screen.blit(instruction_surface, (30, y_start + i * 20))
    
    def launch_game(self, game_filename):
        """Launch a specific game"""
        try:
            # Get the absolute path to the game file
            game_path = os.path.join(os.path.dirname(__file__), game_filename)
            
            if os.path.exists(game_path):
                # Launch the game as a separate process
                subprocess.Popen([sys.executable, game_path], 
                               cwd=os.path.dirname(game_path))
                print(f"Launching {game_filename}...")
            else:
                print(f"Game file not found: {game_path}")
                
        except Exception as e:
            print(f"Error launching game: {e}")
    
    def handle_click(self, pos):
        """Handle mouse clicks"""
        for i, card in enumerate(self.game_cards):
            if card.is_clicked(pos):
                game_info = self.games[i]
                self.launch_game(game_info['filename'])
                break
    
    def update(self):
        """Update game state"""
        mouse_pos = pygame.mouse.get_pos()
        
        # Update game cards
        for card in self.game_cards:
            card.update(mouse_pos)
        
        # Refresh stats periodically
        if pygame.time.get_ticks() % 5000 == 0:  # Every 5 seconds
            for i, game in enumerate(self.games):
                if game['filename'] == 'budget_balance.py':
                    self.games[i]['stats'] = self.load_game_stats('games/progress.json')
                elif game['filename'] == 'investment_growth.py':
                    self.games[i]['stats'] = self.load_game_stats('games/investment_progress.json')
                elif game['filename'] == 'fraud_detection.py':
                    self.games[i]['stats'] = self.load_game_stats('games/fraud_progress.json')
            
            self.total_stats = self.calculate_total_stats()
    
    def run(self):
        """Main game loop"""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        self.handle_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_1:
                        self.launch_game('budget_balance.py')
                    elif event.key == pygame.K_2:
                        self.launch_game('investment_growth.py')
                    elif event.key == pygame.K_3:
                        self.launch_game('fraud_detection.py')
            
            self.update()
            
            # Draw everything
            self.draw_background()
            self.draw_header()
            self.draw_stats_panel()
            
            # Draw game cards
            for card in self.game_cards:
                card.draw(self.screen, self.fonts)
            
            self.draw_instructions()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        
    def check_dependencies(self):
        """Check if required dependencies are installed"""
        try:
            import pygame
            print("✓ Pygame is installed")
        except ImportError:
            print("✗ Pygame is not installed. Please run: pip install pygame")
            return False
            
        try:
            import numpy
            print("✓ NumPy is installed") 
        except ImportError:
            print("✗ NumPy is not installed. Please run: pip install numpy")
            return False
            
        return True

if __name__ == "__main__":
    # Create launcher and check dependencies
    launcher = PaisabuddyGameLauncher()
    
    if launcher.check_dependencies():
        print("🚀 Starting Paisabuddy Game Launcher...")
        launcher.run()
    else:
        print("\n📦 Please install missing dependencies first:")
        print("pip install -r requirements.txt")
        input("Press Enter to exit...")
import pygame
import random
import math
import json
import os
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
DARK_GREEN = (27, 94, 32)
BLUE = (25, 118, 210)
LIGHT_BLUE = (100, 181, 246)
RED = (211, 47, 47)
YELLOW = (255, 193, 7)
PURPLE = (156, 39, 176)
BROWN = (121, 85, 72)
SOIL_COLOR = (62, 39, 35)
LIGHT_GRAY = (245, 245, 245)
DARK_GRAY = (100, 100, 100)

class Investment:
    def __init__(self, x, y, investment_type, initial_amount):
        self.x = x
        self.y = y
        self.type = investment_type  # 'stocks', 'bonds', 'mutual_funds', 'gold', 'real_estate'
        self.initial_amount = initial_amount
        self.current_value = initial_amount
        self.growth_rate = self.get_growth_rate()
        self.risk_factor = self.get_risk_factor()
        self.time_planted = 0
        self.maturity_time = self.get_maturity_time()
        self.stage = 0  # 0=seed, 1=sprout, 2=young, 3=mature, 4=flowering
        self.max_stage = 4
        self.width = 80
        self.height = 100
        self.volatility = 0
        self.last_fluctuation = 0
        
        # Visual properties
        self.plant_height = 20
        self.max_height = 80
        
    def get_growth_rate(self):
        rates = {
            'stocks': 0.12,      # 12% annual
            'bonds': 0.06,       # 6% annual
            'mutual_funds': 0.10, # 10% annual
            'gold': 0.08,        # 8% annual
            'real_estate': 0.07   # 7% annual
        }
        return rates.get(self.type, 0.08)
        
    def get_risk_factor(self):
        risks = {
            'stocks': 0.25,      # High volatility
            'bonds': 0.05,       # Low volatility
            'mutual_funds': 0.15, # Medium volatility
            'gold': 0.20,        # Medium-high volatility
            'real_estate': 0.10   # Low-medium volatility
        }
        return risks.get(self.type, 0.15)
        
    def get_maturity_time(self):
        times = {
            'stocks': 300,       # 5 seconds at 60 FPS
            'bonds': 600,        # 10 seconds
            'mutual_funds': 400,  # ~7 seconds
            'gold': 350,         # ~6 seconds
            'real_estate': 800    # ~13 seconds
        }
        return times.get(self.type, 400)
        
    def get_color(self):
        colors = {
            'stocks': BLUE,
            'bonds': GREEN,
            'mutual_funds': PURPLE,
            'gold': YELLOW,
            'real_estate': BROWN
        }
        return colors.get(self.type, GREEN)
        
    def get_icon(self):
        icons = {
            'stocks': "📈",
            'bonds': "🏦",
            'mutual_funds': "📊",
            'gold': "🥇",
            'real_estate': "🏠"
        }
        return icons.get(self.type, "💰")
        
    def update(self):
        self.time_planted += 1
        
        # Calculate compound growth
        time_factor = self.time_planted / 3600  # Convert frames to hours-like units
        base_growth = self.initial_amount * (1 + self.growth_rate) ** time_factor
        
        # Add market volatility
        if self.time_planted % 30 == 0:  # Every half second
            volatility_change = random.uniform(-self.risk_factor, self.risk_factor)
            self.volatility = max(-0.5, min(0.5, volatility_change))
            
        # Apply volatility
        volatile_value = base_growth * (1 + self.volatility)
        self.current_value = max(self.initial_amount * 0.1, volatile_value)  # Minimum 10% of initial
        
        # Update growth stage based on time
        progress = min(1.0, self.time_planted / self.maturity_time)
        self.stage = int(progress * self.max_stage)
        
        # Update visual properties
        self.plant_height = 20 + (self.max_height - 20) * progress
        
    def draw(self, screen, font, small_font):
        # Draw soil
        soil_rect = (self.x, self.y + self.height - 20, self.width, 20)
        pygame.draw.rect(screen, SOIL_COLOR, soil_rect, border_radius=5)
        
        # Draw plant based on stage
        center_x = self.x + self.width // 2
        ground_y = self.y + self.height - 20
        
        color = self.get_color()
        
        if self.stage == 0:  # Seed
            pygame.draw.circle(screen, BROWN, (center_x, ground_y - 5), 3)
        elif self.stage == 1:  # Sprout
            # Small green shoot
            pygame.draw.line(screen, GREEN, (center_x, ground_y), (center_x, ground_y - 15), 3)
            pygame.draw.circle(screen, LIGHT_GREEN, (center_x, ground_y - 15), 4)
        elif self.stage == 2:  # Young plant
            # Stem and small leaves
            pygame.draw.line(screen, DARK_GREEN, (center_x, ground_y), (center_x, ground_y - int(self.plant_height * 0.6)), 4)
            # Leaves
            leaf_y = ground_y - int(self.plant_height * 0.4)
            pygame.draw.ellipse(screen, GREEN, (center_x - 10, leaf_y - 5, 20, 10))
            pygame.draw.ellipse(screen, GREEN, (center_x - 8, leaf_y - 15, 16, 10))
        elif self.stage == 3:  # Mature plant
            # Full stem
            pygame.draw.line(screen, DARK_GREEN, (center_x, ground_y), (center_x, ground_y - int(self.plant_height * 0.8)), 5)
            # Multiple leaves
            for i, leaf_height in enumerate([0.3, 0.5, 0.7]):
                leaf_y = ground_y - int(self.plant_height * leaf_height)
                side = (-1) ** i
                pygame.draw.ellipse(screen, GREEN, (center_x + side * 5, leaf_y - 8, 15, 16))
        else:  # Flowering/Fruiting
            # Full plant with investment symbol
            pygame.draw.line(screen, DARK_GREEN, (center_x, ground_y), (center_x, ground_y - int(self.plant_height)), 5)
            # Leaves
            for i, leaf_height in enumerate([0.3, 0.5, 0.7]):
                leaf_y = ground_y - int(self.plant_height * leaf_height)
                side = (-1) ** i
                pygame.draw.ellipse(screen, GREEN, (center_x + side * 5, leaf_y - 8, 15, 16))
            
            # Investment flower/fruit
            flower_y = ground_y - int(self.plant_height)
            pygame.draw.circle(screen, color, (center_x, flower_y), 12)
            
            # Draw investment icon
            icon = self.get_icon()
            icon_surface = font.render(icon, True, WHITE)
            icon_rect = icon_surface.get_rect(center=(center_x, flower_y))
            screen.blit(icon_surface, icon_rect)
        
        # Draw investment info panel
        panel_y = self.y - 60
        panel_rect = (self.x - 10, panel_y, self.width + 20, 50)
        pygame.draw.rect(screen, WHITE, panel_rect, border_radius=10)
        pygame.draw.rect(screen, BLACK, panel_rect, 2, border_radius=10)
        
        # Investment type and amount
        type_text = small_font.render(self.type.title().replace('_', ' '), True, BLACK)
        screen.blit(type_text, (self.x - 5, panel_y + 5))
        
        # Current value with color coding
        value_change = (self.current_value - self.initial_amount) / self.initial_amount
        value_color = GREEN if value_change > 0 else RED if value_change < 0 else BLACK
        
        value_text = f"₹{self.current_value:,.0f}"
        if value_change != 0:
            value_text += f" ({value_change:+.1%})"
            
        value_surface = small_font.render(value_text, True, value_color)
        screen.blit(value_surface, (self.x - 5, panel_y + 25))
        
        # Progress bar
        progress = min(1.0, self.time_planted / self.maturity_time)
        bar_width = self.width
        bar_height = 4
        bar_rect = (self.x - 5, panel_y + 42, bar_width, bar_height)
        pygame.draw.rect(screen, LIGHT_GRAY, bar_rect, border_radius=2)
        
        if progress > 0:
            progress_rect = (self.x - 5, panel_y + 42, int(bar_width * progress), bar_height)
            pygame.draw.rect(screen, color, progress_rect, border_radius=2)

class InvestmentGrowthGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Investment Growth Garden - Paisabuddy Financial Game")
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_active = False
        self.game_over = False
        
        # Fonts
        self.title_font = pygame.font.Font(None, 48)
        self.subtitle_font = pygame.font.Font(None, 32)
        self.text_font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # Game state
        self.portfolio_value = 10000  # Starting money
        self.investments = []
        self.selected_investment_type = 'stocks'
        self.investment_amount = 1000
        self.time_elapsed = 0
        self.total_invested = 0
        self.total_returns = 0
        self.game_speed = 1
        
        # UI elements
        self.investment_types = ['stocks', 'bonds', 'mutual_funds', 'gold', 'real_estate']
        self.investment_buttons = {}
        self.setup_ui()
        
        # Educational content
        self.financial_lessons = {
            'stocks': "Stocks offer high growth potential but with higher risk. Diversify across sectors!",
            'bonds': "Bonds provide steady, low-risk returns. Great for stable income streams.",
            'mutual_funds': "Mutual funds offer professional management and instant diversification.",
            'gold': "Gold is a hedge against inflation and market uncertainty.",
            'real_estate': "Real estate provides rental income and long-term appreciation."
        }
        
        self.current_lesson = self.financial_lessons['stocks']
        
    def setup_ui(self):
        # Create buttons for investment types
        button_width = 150
        button_height = 40
        start_x = 50
        start_y = SCREEN_HEIGHT - 120
        
        for i, inv_type in enumerate(self.investment_types):
            x = start_x + i * (button_width + 20)
            self.investment_buttons[inv_type] = pygame.Rect(x, start_y, button_width, button_height)
            
    def handle_click(self, pos):
        # Check investment type buttons
        for inv_type, button_rect in self.investment_buttons.items():
            if button_rect.collidepoint(pos):
                self.selected_investment_type = inv_type
                self.current_lesson = self.financial_lessons[inv_type]
                return
                
        # Check planting area (main game area)
        if pos[1] > 100 and pos[1] < SCREEN_HEIGHT - 150:  # In planting area
            if self.portfolio_value >= self.investment_amount:
                self.plant_investment(pos[0], pos[1])
                
    def plant_investment(self, x, y):
        # Find suitable planting spot
        plant_x = max(50, min(SCREEN_WIDTH - 130, x - 40))
        plant_y = max(150, min(SCREEN_HEIGHT - 200, y - 50))
        
        # Check for overlaps
        for investment in self.investments:
            if (abs(investment.x - plant_x) < 100 and 
                abs(investment.y - plant_y) < 120):
                return  # Too close to existing investment
                
        # Create new investment
        investment = Investment(plant_x, plant_y, self.selected_investment_type, self.investment_amount)
        self.investments.append(investment)
        
        # Deduct money
        self.portfolio_value -= self.investment_amount
        self.total_invested += self.investment_amount
        
    def update_investments(self):
        for investment in self.investments:
            investment.update()
            
        # Calculate total returns
        current_portfolio_value = self.portfolio_value + sum(inv.current_value for inv in self.investments)
        self.total_returns = current_portfolio_value - 10000  # Initial amount was 10000
        
    def draw_background(self):
        # Sky gradient
        for y in range(SCREEN_HEIGHT - 150):
            color_ratio = y / (SCREEN_HEIGHT - 150)
            r = int(135 * (1 - color_ratio) + 200 * color_ratio)
            g = int(206 * (1 - color_ratio) + 230 * color_ratio)
            b = int(235 * (1 - color_ratio) + 200 * color_ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
            
        # Ground
        ground_rect = (0, SCREEN_HEIGHT - 150, SCREEN_WIDTH, 150)
        pygame.draw.rect(self.screen, DARK_GREEN, ground_rect)
        
        # Add some grass texture
        for i in range(0, SCREEN_WIDTH, 10):
            grass_height = random.randint(5, 15)
            pygame.draw.line(self.screen, GREEN, (i, SCREEN_HEIGHT - 150), 
                           (i, SCREEN_HEIGHT - 150 + grass_height), 2)
            
    def draw_ui(self):
        # Top panel
        panel_rect = (0, 0, SCREEN_WIDTH, 90)
        pygame.draw.rect(self.screen, WHITE, panel_rect)
        pygame.draw.rect(self.screen, BLACK, panel_rect, 2)
        
        # Portfolio stats
        cash_text = self.subtitle_font.render(f"Cash: ₹{self.portfolio_value:,.0f}", True, GREEN)
        self.screen.blit(cash_text, (20, 20))
        
        total_value = self.portfolio_value + sum(inv.current_value for inv in self.investments)
        portfolio_text = self.subtitle_font.render(f"Portfolio: ₹{total_value:,.0f}", True, BLUE)
        self.screen.blit(portfolio_text, (20, 50))
        
        # Returns
        returns_color = GREEN if self.total_returns >= 0 else RED
        returns_text = self.subtitle_font.render(f"Returns: ₹{self.total_returns:,.0f} ({(self.total_returns/10000)*100:+.1f}%)", True, returns_color)
        self.screen.blit(returns_text, (300, 20))
        
        # Investment count
        count_text = self.text_font.render(f"Active Investments: {len(self.investments)}", True, BLACK)
        self.screen.blit(count_text, (300, 50))
        
        # Speed control
        speed_text = self.text_font.render(f"Speed: {self.game_speed}x (Press +/- to change)", True, DARK_GRAY)
        self.screen.blit(speed_text, (600, 20))
        
        # Investment amount selector
        amount_text = self.text_font.render(f"Investment Amount: ₹{self.investment_amount:,} (Use scroll wheel)", True, DARK_GRAY)
        self.screen.blit(amount_text, (600, 50))
        
        # Bottom panel with investment buttons
        bottom_panel_rect = (0, SCREEN_HEIGHT - 150, SCREEN_WIDTH, 150)
        pygame.draw.rect(self.screen, LIGHT_GRAY, bottom_panel_rect)
        pygame.draw.rect(self.screen, BLACK, bottom_panel_rect, 2)
        
        # Investment type buttons
        for inv_type, button_rect in self.investment_buttons.items():
            # Button color based on selection
            if inv_type == self.selected_investment_type:
                button_color = BLUE
                text_color = WHITE
            else:
                button_color = WHITE
                text_color = BLACK
                
            pygame.draw.rect(self.screen, button_color, button_rect, border_radius=10)
            pygame.draw.rect(self.screen, BLACK, button_rect, 2, border_radius=10)
            
            # Button text
            button_text = self.text_font.render(inv_type.title().replace('_', ' '), True, text_color)
            text_rect = button_text.get_rect(center=button_rect.center)
            self.screen.blit(button_text, text_rect)
            
            # Expected return info
            investment = Investment(0, 0, inv_type, 1000)
            return_info = f"{investment.growth_rate*100:.0f}% return"
            risk_info = f"Risk: {investment.risk_factor*100:.0f}%"
            
            info_font = pygame.font.Font(None, 16)
            return_surface = info_font.render(return_info, True, GREEN)
            risk_surface = info_font.render(risk_info, True, RED)
            
            self.screen.blit(return_surface, (button_rect.x, button_rect.y + button_rect.height + 5))
            self.screen.blit(risk_surface, (button_rect.x, button_rect.y + button_rect.height + 20))
            
        # Current lesson
        lesson_y = SCREEN_HEIGHT - 45
        lesson_text = self.small_font.render(f"💡 {self.current_lesson}", True, DARK_GRAY)
        self.screen.blit(lesson_text, (20, lesson_y))
        
        # Instructions
        if len(self.investments) == 0:
            instruction_text = self.text_font.render("Click in the garden area to plant your first investment!", True, PURPLE)
            instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            
            # Background for instruction
            pygame.draw.rect(self.screen, WHITE, instruction_rect.inflate(40, 20), border_radius=10)
            pygame.draw.rect(self.screen, PURPLE, instruction_rect.inflate(40, 20), 2, border_radius=10)
            self.screen.blit(instruction_text, instruction_rect)
            
    def draw_start_screen(self):
        self.screen.fill(WHITE)
        
        # Title
        title = self.title_font.render("🌱 INVESTMENT GROWTH GARDEN 🌱", True, GREEN)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)
        
        # Instructions
        instructions = [
            "🎯 Plant investments and watch them grow over time",
            "📈 Different investments have different risk/return profiles",
            "💰 Compound interest makes your money grow exponentially",
            "⏰ Longer investments generally yield higher returns",
            "🎮 Learn real investment principles through gameplay!",
            "",
            "How to Play:",
            "• Select an investment type from the bottom panel",
            "• Click in the garden to plant your investment",
            "• Watch your investments grow and mature over time",
            "• Use +/- keys to change game speed",
            "• Use scroll wheel to adjust investment amount",
            "",
            "Press SPACE to start your investment journey!"
        ]
        
        y = 250
        for instruction in instructions:
            if instruction:
                if instruction.startswith("🎯") or instruction.startswith("How to Play:"):
                    color = BLUE
                    font = self.text_font
                elif instruction.startswith("•"):
                    color = DARK_GRAY
                    font = self.small_font
                else:
                    color = BLACK
                    font = self.text_font
                    
                text = font.render(instruction, True, color)
                text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
                self.screen.blit(text, text_rect)
            y += 25
            
    def draw_performance_summary(self):
        if len(self.investments) == 0:
            return
            
        # Performance panel
        panel_width = 300
        panel_height = 200
        panel_x = SCREEN_WIDTH - panel_width - 20
        panel_y = 100
        
        pygame.draw.rect(self.screen, WHITE, (panel_x, panel_y, panel_width, panel_height), border_radius=15)
        pygame.draw.rect(self.screen, BLACK, (panel_x, panel_y, panel_width, panel_height), 2, border_radius=15)
        
        # Title
        title_text = self.text_font.render("📊 Portfolio Analysis", True, BLUE)
        self.screen.blit(title_text, (panel_x + 10, panel_y + 10))
        
        # Investment breakdown
        y_offset = 40
        investment_summary = {}
        
        for inv in self.investments:
            if inv.type not in investment_summary:
                investment_summary[inv.type] = {'count': 0, 'value': 0, 'invested': 0}
            investment_summary[inv.type]['count'] += 1
            investment_summary[inv.type]['value'] += inv.current_value
            investment_summary[inv.type]['invested'] += inv.initial_amount
            
        for inv_type, data in investment_summary.items():
            count_text = f"{inv_type.title()}: {data['count']} plants"
            value_text = f"Value: ₹{data['value']:,.0f}"
            roi = ((data['value'] - data['invested']) / data['invested']) * 100
            roi_text = f"ROI: {roi:+.1f}%"
            roi_color = GREEN if roi >= 0 else RED
            
            # Draw summary
            self.small_font.render(count_text, True, BLACK)
            count_surface = self.small_font.render(count_text, True, BLACK)
            value_surface = self.small_font.render(value_text, True, BLUE)
            roi_surface = self.small_font.render(roi_text, True, roi_color)
            
            self.screen.blit(count_surface, (panel_x + 10, panel_y + y_offset))
            self.screen.blit(value_surface, (panel_x + 10, panel_y + y_offset + 15))
            self.screen.blit(roi_surface, (panel_x + 10, panel_y + y_offset + 30))
            
            y_offset += 50
            
    def save_progress(self):
        """Save investment game progress"""
        progress = {
            'total_invested': self.total_invested,
            'total_returns': self.total_returns,
            'max_portfolio_value': self.portfolio_value + sum(inv.current_value for inv in self.investments),
            'investments_made': len(self.investments),
            'game_time': self.time_elapsed
        }
        
        # Load and merge existing progress
        if os.path.exists('games/investment_progress.json'):
            try:
                with open('games/investment_progress.json', 'r') as f:
                    existing = json.load(f)
                    
                progress['total_invested'] += existing.get('total_invested', 0)
                progress['total_returns'] = max(progress['total_returns'], existing.get('total_returns', 0))
                progress['max_portfolio_value'] = max(progress['max_portfolio_value'], existing.get('max_portfolio_value', 0))
                progress['investments_made'] += existing.get('investments_made', 0)
                progress['game_time'] += existing.get('game_time', 0)
                
            except (json.JSONDecodeError, KeyError):
                pass
                
        with open('games/investment_progress.json', 'w') as f:
            json.dump(progress, f, indent=2)
            
    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and not self.game_active:
                        self.game_active = True
                    elif event.key == pygame.K_ESCAPE:
                        if self.game_active:
                            self.save_progress()
                        self.running = False
                    elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                        self.game_speed = min(5, self.game_speed + 1)
                    elif event.key == pygame.K_MINUS:
                        self.game_speed = max(1, self.game_speed - 1)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1 and self.game_active:  # Left click
                        self.handle_click(event.pos)
                elif event.type == pygame.MOUSEWHEEL:
                    if self.game_active:
                        self.investment_amount = max(500, min(5000, self.investment_amount + event.y * 250))
                        
            if self.game_active:
                # Update game at specified speed
                for _ in range(self.game_speed):
                    self.update_investments()
                    self.time_elapsed += 1
                    
                # Draw game
                self.draw_background()
                
                # Draw investments
                for investment in self.investments:
                    investment.draw(self.screen, self.text_font, self.small_font)
                    
                self.draw_ui()
                self.draw_performance_summary()
            else:
                self.draw_start_screen()
                
            pygame.display.flip()
            self.clock.tick(FPS)
            
        if self.game_active:
            self.save_progress()
        pygame.quit()

if __name__ == "__main__":
    game = InvestmentGrowthGame()
    game.run()
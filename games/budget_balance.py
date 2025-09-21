import pygame
import random
import math
import json
import os

# Import database functions
try:
    from database import init_db, close_db, get_user, start_game, save_game_progress, finish_game, unlock_achievement
    DATABASE_AVAILABLE = True
except ImportError:
    print("⚠️ Database not available - running in offline mode")
    DATABASE_AVAILABLE = False

# Initialize Pygame
pygame.init()

# Game constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (46, 125, 50)
RED = (211, 47, 47)
BLUE = (25, 118, 210)
YELLOW = (255, 193, 7)
PURPLE = (156, 39, 176)
LIGHT_GRAY = (240, 240, 240)
DARK_GRAY = (100, 100, 100)

class GameObject:
    def __init__(self, x, y, width, height, color, value, item_type):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.value = value
        self.item_type = item_type  # 'income', 'expense', 'investment', 'debt'
        self.speed = random.uniform(2, 4)
        self.collected = False
        
    def update(self):
        self.y += self.speed
        
    def draw(self, screen, font):
        # Draw the item
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height), border_radius=10)
        pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height), 2, border_radius=10)
        
        # Draw the value
        if self.item_type == 'income':
            text = f"+₹{self.value}"
            text_color = WHITE
        elif self.item_type == 'investment':
            text = f"📈₹{self.value}"
            text_color = WHITE
        else:
            text = f"-₹{self.value}"
            text_color = WHITE
            
        text_surface = font.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=(self.x + self.width//2, self.y + self.height//2))
        screen.blit(text_surface, text_rect)
        
        # Draw item type icon
        icon_font = pygame.font.Font(None, 24)
        if self.item_type == 'income':
            icon = "💰"
        elif self.item_type == 'expense':
            icon = "🛒"
        elif self.item_type == 'investment':
            icon = "📊"
        else:  # debt
            icon = "💳"
            
        icon_surface = icon_font.render(icon, True, WHITE)
        screen.blit(icon_surface, (self.x + 5, self.y + 5))
        
    def check_collision(self, player_x, player_y, player_width, player_height):
        return (self.x < player_x + player_width and
                self.x + self.width > player_x and
                self.y < player_y + player_height and
                self.y + self.height > player_y)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 60
        self.height = 60
        self.speed = 7
        self.balance = 1000
        self.score = 0
        
    def update(self, keys):
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed
        if keys[pygame.K_UP] and self.y > 0:
            self.y -= self.speed
        if keys[pygame.K_DOWN] and self.y < SCREEN_HEIGHT - self.height:
            self.y += self.speed
            
    def draw(self, screen):
        # Draw player as a wallet
        pygame.draw.rect(screen, PURPLE, (self.x, self.y, self.width, self.height), border_radius=15)
        pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height), 3, border_radius=15)
        
        # Draw wallet details
        pygame.draw.rect(screen, WHITE, (self.x + 10, self.y + 10, self.width - 20, 15))
        pygame.draw.rect(screen, YELLOW, (self.x + 10, self.y + 30, self.width - 20, 10))
        
        # Draw player emoji
        font = pygame.font.Font(None, 36)
        emoji = font.render("💼", True, WHITE)
        screen.blit(emoji, (self.x + 15, self.y + 15))

class BudgetBalanceGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Budget Balance - Paisabuddy Financial Game")
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_active = False
        self.game_over = False
        
        # Fonts
        self.title_font = pygame.font.Font(None, 48)
        self.subtitle_font = pygame.font.Font(None, 32)
        self.text_font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        
        # Game objects
        self.player = Player(SCREEN_WIDTH // 2 - 30, SCREEN_HEIGHT - 100)
        self.objects = []
        self.spawn_timer = 0
        self.spawn_delay = 60  # frames between spawns
        self.level = 1
        self.time_elapsed = 0
        self.combo_multiplier = 1
        self.combo_timer = 0
        
        # Game stats
        self.items_collected = {'income': 0, 'expense': 0, 'investment': 0, 'debt': 0}
        self.financial_tips = [
            "Collect more income than expenses to stay positive!",
            "Investments grow your money over time - grab them!",
            "Avoid debt items - they drain your balance quickly!",
            "Build an emergency fund by saving 20% of income",
            "Diversify investments to reduce risk",
            "Track your spending to identify money leaks"
        ]
        self.current_tip = random.choice(self.financial_tips)
        
        # Database connection
        self.user = None
        self.session_id = None
        self.connect_to_database()
    
    def connect_to_database(self):
        """Initialize database connection and get user"""
        if not DATABASE_AVAILABLE:
            return
            
        try:
            if init_db():
                self.user = get_user("demo_user")
                if self.user:
                    print(f"🎮 Welcome back, {self.user['name']}! (Total Score: {self.user['total_score']})")
                    self.session_id = start_game(self.user['id'], "Budget Balance")
                else:
                    print("❌ Could not create/get user")
            else:
                print("❌ Could not connect to database")
        except Exception as e:
            print(f"⚠️ Database connection failed: {e}. Running in offline mode.")
    
    def save_progress_to_db(self):
        """Save current game progress to database"""
        if not DATABASE_AVAILABLE or not self.session_id:
            return
            
        try:
            save_game_progress(
                self.session_id,
                int(self.player.score),
                self.level,
                self.items_collected,
                {
                    'balance': self.player.balance,
                    'combo_multiplier': self.combo_multiplier,
                    'time_elapsed': self.time_elapsed
                }
            )
        except Exception as e:
            print(f"⚠️ Failed to save progress: {e}")
    
    def check_achievements(self):
        """Check and unlock achievements"""
        if not DATABASE_AVAILABLE or not self.user:
            return
            
        try:
            # Check various achievement conditions
            if self.player.score >= 1000 and self.items_collected['income'] == 0:
                unlock_achievement(self.user['id'], "Budget Balance", "First Steps", "Played your first Budget Balance game")
            
            if self.player.score >= 5000:
                unlock_achievement(self.user['id'], "Budget Balance", "Big Spender", "Achieved 5,000 points in a single game")
            
            if self.level >= 5:
                unlock_achievement(self.user['id'], "Budget Balance", "Level Master", "Reached level 5")
            
            if self.combo_multiplier >= 2.0:
                unlock_achievement(self.user['id'], "Budget Balance", "Combo King", "Achieved 2x combo multiplier")
            
            if self.items_collected['income'] >= 50:
                unlock_achievement(self.user['id'], "Budget Balance", "Income Expert", "Collected 50 income items")
                
        except Exception as e:
            print(f"⚠️ Failed to check achievements: {e}")
        
    def spawn_object(self):
        x = random.randint(0, SCREEN_WIDTH - 80)
        y = -50
        
        # Determine what to spawn based on level and probability
        rand = random.random()
        
        if rand < 0.4:  # 40% income
            value = random.randint(100, 500) * self.level
            obj = GameObject(x, y, 80, 50, GREEN, value, 'income')
        elif rand < 0.6:  # 20% investment
            value = random.randint(200, 800) * self.level
            obj = GameObject(x, y, 80, 50, BLUE, value, 'investment')
        elif rand < 0.85:  # 25% expense
            value = random.randint(50, 300) * self.level
            obj = GameObject(x, y, 80, 50, RED, value, 'expense')
        else:  # 15% debt
            value = random.randint(200, 600) * self.level
            obj = GameObject(x, y, 80, 50, DARK_GRAY, value, 'debt')
            
        self.objects.append(obj)
        
    def handle_collision(self, obj):
        if obj.item_type == 'income':
            self.player.balance += obj.value * self.combo_multiplier
            self.player.score += obj.value * self.combo_multiplier
            self.combo_timer = 180  # 3 seconds
            self.combo_multiplier = min(self.combo_multiplier + 0.1, 3.0)
        elif obj.item_type == 'investment':
            # Investment grows over time
            growth = obj.value * 1.2 * self.combo_multiplier
            self.player.balance += int(growth)
            self.player.score += int(growth)
            self.combo_timer = 180
            self.combo_multiplier = min(self.combo_multiplier + 0.2, 3.0)
        elif obj.item_type == 'expense':
            self.player.balance -= obj.value
            self.combo_multiplier = 1.0
            if self.player.balance < 0:
                self.player.balance = 0
        else:  # debt
            debt_penalty = obj.value * 1.5
            self.player.balance -= int(debt_penalty)
            self.combo_multiplier = 1.0
            if self.player.balance < 0:
                self.player.balance = 0
                
        self.items_collected[obj.item_type] += 1
        
    def update_game(self):
        if not self.game_active or self.game_over:
            return
            
        keys = pygame.key.get_pressed()
        self.player.update(keys)
        
        # Spawn objects
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_delay:
            self.spawn_object()
            self.spawn_timer = 0
            
        # Update objects
        for obj in self.objects[:]:
            obj.update()
            
            # Check collision
            if obj.check_collision(self.player.x, self.player.y, self.player.width, self.player.height):
                self.handle_collision(obj)
                self.objects.remove(obj)
            elif obj.y > SCREEN_HEIGHT:
                self.objects.remove(obj)
                
        # Update combo timer
        if self.combo_timer > 0:
            self.combo_timer -= 1
        else:
            self.combo_multiplier = 1.0
            
        # Update level and difficulty
        self.time_elapsed += 1
        if self.time_elapsed % 1800 == 0:  # Every 30 seconds
            self.level += 1
            self.spawn_delay = max(20, self.spawn_delay - 5)
            self.current_tip = random.choice(self.financial_tips)
        
        # Save progress to database every 5 seconds
        if self.time_elapsed % 300 == 0:
            self.save_progress_to_db()
        
        # Check achievements every 10 seconds
        if self.time_elapsed % 600 == 0:
            self.check_achievements()
            
        # Check game over conditions
        if self.player.balance <= 0 and len([obj for obj in self.objects if obj.item_type in ['expense', 'debt']]) == 0:
            self.game_over = True
            
    def draw_ui(self):
        # Background
        self.screen.fill(LIGHT_GRAY)
        
        # Draw gradient background
        for y in range(SCREEN_HEIGHT):
            color_ratio = y / SCREEN_HEIGHT
            r = int(247 * (1 - color_ratio) + 234 * color_ratio)
            g = int(230 * (1 - color_ratio) + 211 * color_ratio)
            b = int(228 * (1 - color_ratio) + 207 * color_ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
            
        # Top bar with stats
        pygame.draw.rect(self.screen, WHITE, (0, 0, SCREEN_WIDTH, 80))
        pygame.draw.rect(self.screen, BLACK, (0, 0, SCREEN_WIDTH, 80), 2)
        
        # Balance
        balance_text = self.subtitle_font.render(f"Balance: ₹{int(self.player.balance):,}", True, GREEN if self.player.balance > 0 else RED)
        self.screen.blit(balance_text, (20, 20))
        
        # Score  
        score_text = self.subtitle_font.render(f"Score: {int(self.player.score):,}", True, BLUE)
        self.screen.blit(score_text, (20, 45))
        
        # Level
        level_text = self.subtitle_font.render(f"Level: {self.level}", True, PURPLE)
        self.screen.blit(level_text, (350, 20))
        
        # Combo multiplier
        if self.combo_multiplier > 1.0:
            combo_text = self.subtitle_font.render(f"Combo: x{self.combo_multiplier:.1f}", True, YELLOW)
            self.screen.blit(combo_text, (350, 45))
            
        # Items collected
        stats_x = 550
        for i, (item_type, count) in enumerate(self.items_collected.items()):
            color = {
                'income': GREEN,
                'investment': BLUE,
                'expense': RED,
                'debt': DARK_GRAY
            }[item_type]
            
            text = self.text_font.render(f"{item_type.title()}: {count}", True, color)
            self.screen.blit(text, (stats_x + (i % 2) * 200, 20 + (i // 2) * 25))
            
        # Financial tip
        tip_text = self.small_font.render(f"💡 {self.current_tip}", True, DARK_GRAY)
        self.screen.blit(tip_text, (20, SCREEN_HEIGHT - 30))
        
    def draw_start_screen(self):
        self.screen.fill(WHITE)
        
        # Title
        title = self.title_font.render("💰 BUDGET BALANCE GAME 💰", True, PURPLE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)
        
        # Instructions
        instructions = [
            "🎯 Collect green income and blue investment items",
            "❌ Avoid red expenses and gray debt items",
            "🏆 Build combos by collecting good items consecutively",
            "💡 Learn real financial literacy skills while playing!",
            "",
            "Controls: Arrow keys to move",
            "",
            "Press SPACE to start playing!"
        ]
        
        y = 250
        for instruction in instructions:
            if instruction:
                color = BLUE if instruction.startswith("🎯") or instruction.startswith("Controls") else BLACK
                text = self.text_font.render(instruction, True, color)
                text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
                self.screen.blit(text, text_rect)
            y += 35
            
    def draw_game_over_screen(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Game over panel
        panel_width, panel_height = 500, 400
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_y = (SCREEN_HEIGHT - panel_height) // 2
        
        pygame.draw.rect(self.screen, WHITE, (panel_x, panel_y, panel_width, panel_height), border_radius=20)
        pygame.draw.rect(self.screen, BLACK, (panel_x, panel_y, panel_width, panel_height), 3, border_radius=20)
        
        # Game over text
        game_over_text = self.title_font.render("Game Over!", True, RED)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, panel_y + 60))
        self.screen.blit(game_over_text, game_over_rect)
        
        # Final stats
        stats_y = panel_y + 120
        final_stats = [
            f"Final Score: {self.player.score:,}",
            f"Final Balance: ₹{self.player.balance:,}",
            f"Level Reached: {self.level}",
            "",
            f"Income Collected: {self.items_collected['income']}",
            f"Investments Made: {self.items_collected['investment']}",
            f"Expenses Avoided: {len(self.objects)} left",
            "",
            "Press R to restart or ESC to quit"
        ]
        
        for stat in final_stats:
            if stat:
                color = GREEN if "Score" in stat or "Balance" in stat else BLACK
                text = self.text_font.render(stat, True, color)
                text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, stats_y))
                self.screen.blit(text, text_rect)
            stats_y += 25
            
    def save_progress(self):
        """Save final game results to database and JSON backup"""
        # Save to database first
        if DATABASE_AVAILABLE and self.session_id:
            try:
                achievements = []
                if self.player.score >= 1000:
                    achievements.append("First Game")
                if self.level >= 5:
                    achievements.append("Level 5 Reached")
                    
                finish_game(self.session_id, int(self.player.score), achievements if achievements else None)
                print(f"🏆 Game completed! Score: {self.player.score}, Level: {self.level}")
            except Exception as e:
                print(f"⚠️ Failed to save to database: {e}")
        
        # Also save to JSON as backup
        progress = {
            'high_score': self.player.score,
            'max_level': self.level,
            'items_collected': self.items_collected.copy(),
            'games_played': 1
        }
        
        # Load existing progress if it exists
        if os.path.exists('games/progress.json'):
            try:
                with open('games/progress.json', 'r') as f:
                    existing_progress = json.load(f)
                    
                # Update with better scores
                progress['high_score'] = max(progress['high_score'], existing_progress.get('high_score', 0))
                progress['max_level'] = max(progress['max_level'], existing_progress.get('max_level', 1))
                progress['games_played'] = existing_progress.get('games_played', 0) + 1
                
                # Merge item collections
                for item_type in progress['items_collected']:
                    existing_items = existing_progress.get('items_collected', {})
                    progress['items_collected'][item_type] += existing_items.get(item_type, 0)
                    
            except (json.JSONDecodeError, KeyError):
                pass
                
        # Save progress
        with open('games/progress.json', 'w') as f:
            json.dump(progress, f, indent=2)
            
    def reset_game(self):
        self.player = Player(SCREEN_WIDTH // 2 - 30, SCREEN_HEIGHT - 100)
        self.objects = []
        self.spawn_timer = 0
        self.spawn_delay = 60
        self.level = 1
        self.time_elapsed = 0
        self.combo_multiplier = 1
        self.combo_timer = 0
        self.items_collected = {'income': 0, 'expense': 0, 'investment': 0, 'debt': 0}
        self.game_over = False
        self.current_tip = random.choice(self.financial_tips)
        
    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and not self.game_active and not self.game_over:
                        self.game_active = True
                    elif event.key == pygame.K_r and self.game_over:
                        self.reset_game()
                        self.game_active = True
                    elif event.key == pygame.K_ESCAPE:
                        if self.game_over:
                            self.save_progress()
                        self.running = False
                        
            if self.game_active and not self.game_over:
                self.update_game()
                self.draw_ui()
                
                # Draw game objects
                for obj in self.objects:
                    obj.draw(self.screen, self.text_font)
                    
                # Draw player
                self.player.draw(self.screen)
                
            elif self.game_over:
                self.draw_ui()
                for obj in self.objects:
                    obj.draw(self.screen, self.text_font)
                self.player.draw(self.screen)
                self.draw_game_over_screen()
            else:
                self.draw_start_screen()
                
            pygame.display.flip()
            self.clock.tick(FPS)
            
        if self.game_over:
            self.save_progress()
        
        # Close database connection
        if DATABASE_AVAILABLE:
            try:
                close_db()
            except:
                pass
                
        pygame.quit()

if __name__ == "__main__":
    game = BudgetBalanceGame()
    game.run()
import pygame
import random
import math
import json
import os
import time

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
ORANGE = (255, 152, 0)

class ScamAlert:
    def __init__(self, x, y, scam_type, is_real_scam=True):
        self.x = x
        self.y = y
        self.width = 180
        self.height = 120
        self.scam_type = scam_type
        self.is_real_scam = is_real_scam
        self.active_time = 0
        self.max_time = 300  # 5 seconds at 60 FPS
        self.clicked = False
        self.show_feedback = False
        self.feedback_timer = 0
        
        # Visual properties
        self.bounce_offset = 0
        self.pulse_scale = 1.0
        
        # Scam content
        self.content = self.generate_content()
        
    def generate_content(self):
        if self.scam_type == "phishing_email":
            if self.is_real_scam:
                return {
                    "title": "URGENT: Account Suspended",
                    "sender": "security@bank-verify.com",
                    "preview": "Click here to verify account or lose access forever!",
                    "red_flags": ["Suspicious domain", "Urgent language", "Threats"]
                }
            else:
                return {
                    "title": "Monthly Statement Ready",
                    "sender": "noreply@hdfc.com",
                    "preview": "Your account statement is ready for download.",
                    "red_flags": []
                }
        elif self.scam_type == "phone_call":
            if self.is_real_scam:
                return {
                    "title": "Bank Fraud Department",
                    "sender": "+91-XXXXXXXXXX",
                    "preview": "We detected suspicious activity. Share your PIN to secure account.",
                    "red_flags": ["Unknown number", "Asks for PIN", "Creates urgency"]
                }
            else:
                return {
                    "title": "Bank Customer Care",
                    "sender": "+91-1800-XXX-XXXX",
                    "preview": "Thank you for visiting our branch. Rate your experience.",
                    "red_flags": []
                }
        elif self.scam_type == "sms_fraud":
            if self.is_real_scam:
                return {
                    "title": "Lottery Winner!",
                    "sender": "LOTTERY",
                    "preview": "Congratulations! You've won ₹10 lakhs! Pay ₹5000 processing fee.",
                    "red_flags": ["Too good to be true", "Asks for money", "Random lottery"]
                }
            else:
                return {
                    "title": "Bank Transaction Alert",
                    "sender": "HD-HDFCBK",
                    "preview": "Your account debited ₹500 at ATM. Balance: ₹15,000",
                    "red_flags": []
                }
        else:  # fake_website
            if self.is_real_scam:
                return {
                    "title": "Free Credit Card",
                    "sender": "best-credit-cards.co.in",
                    "preview": "Get instant credit card! Just enter Aadhar & PAN details.",
                    "red_flags": ["Suspicious domain", "Asks personal info", "Too easy offer"]
                }
            else:
                return {
                    "title": "Official Bank Login",
                    "sender": "www.hdfcbank.com",
                    "preview": "Secure login with OTP verification.",
                    "red_flags": []
                }
    
    def update(self):
        self.active_time += 1
        
        # Visual effects
        self.bounce_offset = math.sin(self.active_time * 0.1) * 3
        self.pulse_scale = 1.0 + math.sin(self.active_time * 0.2) * 0.05
        
        if self.show_feedback:
            self.feedback_timer += 1
            if self.feedback_timer > 90:  # 1.5 seconds
                self.show_feedback = False
                
        return self.active_time < self.max_time and not self.clicked
        
    def draw(self, screen, font, small_font):
        # Adjust position for bounce effect
        draw_y = self.y + self.bounce_offset
        
        # Scale for pulse effect
        scaled_width = int(self.width * self.pulse_scale)
        scaled_height = int(self.height * self.pulse_scale)
        scaled_x = self.x + (self.width - scaled_width) // 2
        scaled_y = draw_y + (self.height - scaled_height) // 2
        
        # Background color based on scam type
        if self.is_real_scam:
            bg_color = RED if self.scam_type in ["phishing_email", "sms_fraud"] else ORANGE
        else:
            bg_color = GREEN
            
        # Draw main card
        pygame.draw.rect(screen, bg_color, (scaled_x, scaled_y, scaled_width, scaled_height), border_radius=15)
        pygame.draw.rect(screen, BLACK, (scaled_x, scaled_y, scaled_width, scaled_height), 3, border_radius=15)
        
        # Draw scam type icon
        icon_map = {
            "phishing_email": "📧",
            "phone_call": "📞",
            "sms_fraud": "📱",
            "fake_website": "🌐"
        }
        icon = icon_map.get(self.scam_type, "⚠️")
        icon_surface = font.render(icon, True, WHITE)
        screen.blit(icon_surface, (scaled_x + 10, scaled_y + 10))
        
        # Draw content
        title_surface = small_font.render(self.content["title"][:20], True, WHITE)
        screen.blit(title_surface, (scaled_x + 10, scaled_y + 35))
        
        sender_surface = small_font.render(f"From: {self.content['sender'][:18]}", True, WHITE)
        screen.blit(sender_surface, (scaled_x + 10, scaled_y + 55))
        
        # Preview text (wrapped)
        preview_lines = self.wrap_text(self.content["preview"], 25)
        for i, line in enumerate(preview_lines[:2]):  # Max 2 lines
            preview_surface = small_font.render(line, True, WHITE)
            screen.blit(preview_surface, (scaled_x + 10, scaled_y + 75 + i * 15))
        
        # Urgency indicator for scams
        if self.is_real_scam:
            urgency_text = "⚠️ SUSPICIOUS"
            urgency_surface = small_font.render(urgency_text, True, YELLOW)
            screen.blit(urgency_surface, (scaled_x + scaled_width - 100, scaled_y + 5))
        
        # Timer bar
        time_progress = 1.0 - (self.active_time / self.max_time)
        bar_width = scaled_width - 20
        bar_height = 4
        bar_x = scaled_x + 10
        bar_y = scaled_y + scaled_height - 15
        
        pygame.draw.rect(screen, DARK_GRAY, (bar_x, bar_y, bar_width, bar_height))
        if time_progress > 0:
            progress_width = int(bar_width * time_progress)
            progress_color = GREEN if time_progress > 0.5 else YELLOW if time_progress > 0.25 else RED
            pygame.draw.rect(screen, progress_color, (bar_x, bar_y, progress_width, bar_height))
        
        # Show feedback if clicked
        if self.show_feedback:
            feedback_text = "✓ Correct!" if (self.is_real_scam and self.clicked) or (not self.is_real_scam and not self.clicked) else "✗ Wrong!"
            feedback_color = GREEN if "Correct" in feedback_text else RED
            feedback_surface = font.render(feedback_text, True, feedback_color)
            feedback_rect = feedback_surface.get_rect(center=(scaled_x + scaled_width // 2, scaled_y + scaled_height // 2))
            
            # Background for feedback
            pygame.draw.rect(screen, WHITE, feedback_rect.inflate(20, 10), border_radius=5)
            screen.blit(feedback_surface, feedback_rect)
    
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
    
    def check_click(self, pos):
        return (self.x <= pos[0] <= self.x + self.width and
                self.y <= pos[1] <= self.y + self.height)
    
    def handle_click(self):
        if not self.clicked:
            self.clicked = True
            self.show_feedback = True
            self.feedback_timer = 0
            return True
        return False

class FraudDetectionGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Fraud Detection Master - Paisabuddy Security Game")
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
        self.score = 0
        self.lives = 3
        self.level = 1
        self.scam_alerts = []
        self.spawn_timer = 0
        self.spawn_delay = 120  # 2 seconds
        self.time_elapsed = 0
        
        # Statistics
        self.scams_caught = 0
        self.scams_missed = 0
        self.false_positives = 0
        self.legitimate_ignored = 0
        
        # Educational content
        self.fraud_tips = [
            "Banks never ask for PIN/passwords over phone or email",
            "Check sender domains carefully - look for misspellings",
            "Too-good-to-be-true offers are usually scams",
            "Urgent threats are common scammer tactics",
            "Official communications come from verified sources",
            "Never share OTP or personal details with unknown callers"
        ]
        self.current_tip = random.choice(self.fraud_tips)
        self.tip_timer = 0
        
        # Grid positions for alerts
        self.grid_positions = []
        self.setup_grid()
        
    def setup_grid(self):
        # Create a 4x3 grid for scam alerts
        cols, rows = 4, 3
        margin_x = 80
        margin_y = 120
        spacing_x = (SCREEN_WIDTH - 2 * margin_x) // (cols - 1)
        spacing_y = (SCREEN_HEIGHT - margin_y - 150) // (rows - 1)
        
        for row in range(rows):
            for col in range(cols):
                x = margin_x + col * spacing_x - 90  # Offset for alert width
                y = margin_y + row * spacing_y
                self.grid_positions.append((x, y))
    
    def spawn_scam_alert(self):
        if len(self.scam_alerts) >= 6:  # Max 6 active alerts
            return
            
        # Choose random position
        available_positions = []
        for pos in self.grid_positions:
            occupied = False
            for alert in self.scam_alerts:
                if abs(alert.x - pos[0]) < 100 and abs(alert.y - pos[1]) < 100:
                    occupied = True
                    break
            if not occupied:
                available_positions.append(pos)
        
        if not available_positions:
            return
            
        pos = random.choice(available_positions)
        
        # Determine scam type and legitimacy
        scam_types = ["phishing_email", "phone_call", "sms_fraud", "fake_website"]
        scam_type = random.choice(scam_types)
        
        # 70% chance of real scam, 30% legitimate
        is_real_scam = random.random() < 0.7
        
        alert = ScamAlert(pos[0], pos[1], scam_type, is_real_scam)
        self.scam_alerts.append(alert)
    
    def update_game(self):
        if not self.game_active or self.game_over:
            return
        
        self.time_elapsed += 1
        
        # Spawn new alerts
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_delay:
            self.spawn_scam_alert()
            self.spawn_timer = 0
        
        # Update existing alerts
        for alert in self.scam_alerts[:]:
            if not alert.update():
                # Alert expired
                if alert.is_real_scam and not alert.clicked:
                    # Missed a scam
                    self.scams_missed += 1
                    self.lives -= 1
                elif not alert.is_real_scam and not alert.clicked:
                    # Correctly ignored legitimate alert
                    self.legitimate_ignored += 1
                    self.score += 5
                
                self.scam_alerts.remove(alert)
        
        # Update difficulty
        if self.time_elapsed % 1800 == 0:  # Every 30 seconds
            self.level += 1
            self.spawn_delay = max(60, self.spawn_delay - 10)
        
        # Change tip periodically
        self.tip_timer += 1
        if self.tip_timer >= 600:  # Every 10 seconds
            self.current_tip = random.choice(self.fraud_tips)
            self.tip_timer = 0
        
        # Check game over
        if self.lives <= 0:
            self.game_over = True
    
    def handle_click(self, pos):
        for alert in self.scam_alerts[:]:
            if alert.check_click(pos) and not alert.clicked:
                if alert.handle_click():
                    if alert.is_real_scam:
                        # Correctly identified scam
                        self.scams_caught += 1
                        self.score += 20
                    else:
                        # False positive - clicked legitimate alert
                        self.false_positives += 1
                        self.lives -= 1
                    
                    # Remove alert after short delay for feedback
                    break
    
    def draw_background(self):
        # Gradient background
        for y in range(SCREEN_HEIGHT):
            color_ratio = y / SCREEN_HEIGHT
            r = int(240 * (1 - color_ratio) + 200 * color_ratio)
            g = int(245 * (1 - color_ratio) + 220 * color_ratio)
            b = int(250 * (1 - color_ratio) + 230 * color_ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
    
    def draw_ui(self):
        # Top panel
        panel_rect = (0, 0, SCREEN_WIDTH, 80)
        pygame.draw.rect(self.screen, WHITE, panel_rect)
        pygame.draw.rect(self.screen, BLACK, panel_rect, 2)
        
        # Score
        score_text = self.subtitle_font.render(f"Score: {self.score}", True, BLUE)
        self.screen.blit(score_text, (20, 20))
        
        # Lives
        lives_text = self.subtitle_font.render(f"Lives: {'❤️' * self.lives}{'🖤' * (3 - self.lives)}", True, RED)
        self.screen.blit(lives_text, (20, 45))
        
        # Level
        level_text = self.subtitle_font.render(f"Level: {self.level}", True, PURPLE)
        self.screen.blit(level_text, (200, 20))
        
        # Statistics
        stats_text = [
            f"Scams Caught: {self.scams_caught}",
            f"Scams Missed: {self.scams_missed}",
            f"False Alarms: {self.false_positives}"
        ]
        
        for i, stat in enumerate(stats_text):
            color = GREEN if i == 0 else RED if i < 2 else ORANGE
            stat_surface = self.text_font.render(stat, True, color)
            self.screen.blit(stat_surface, (400 + i * 150, 30))
        
        # Current tip
        tip_rect = (0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50)
        pygame.draw.rect(self.screen, LIGHT_GRAY, tip_rect)
        pygame.draw.rect(self.screen, BLACK, tip_rect, 2)
        
        tip_text = self.small_font.render(f"💡 Security Tip: {self.current_tip}", True, DARK_GRAY)
        self.screen.blit(tip_text, (20, SCREEN_HEIGHT - 35))
        
        # Instructions
        instruction_text = self.small_font.render("Click on SCAM alerts to report them. Avoid clicking legitimate messages!", True, DARK_GRAY)
        self.screen.blit(instruction_text, (20, SCREEN_HEIGHT - 20))
    
    def draw_start_screen(self):
        self.screen.fill(WHITE)
        
        # Title
        title = self.title_font.render("🛡️ FRAUD DETECTION MASTER 🛡️", True, RED)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 120))
        self.screen.blit(title, title_rect)
        
        # Subtitle
        subtitle = self.subtitle_font.render("Protect yourself from scams and fraud!", True, BLUE)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 170))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Instructions
        instructions = [
            "🎯 Identify and click on SCAM alerts to report them",
            "✅ Ignore legitimate messages - don't click them!",
            "⚠️ You lose lives for missing scams or false reports",
            "📚 Learn real fraud detection skills while playing",
            "",
            "Types of Threats:",
            "📧 Phishing Emails - Fake bank/service emails",
            "📞 Phone Scams - Fraudsters calling for info",
            "📱 SMS Fraud - Text message scams",
            "🌐 Fake Websites - Copycat sites stealing data",
            "",
            "Scoring:",
            "• +20 points for catching real scams",
            "• +5 points for ignoring legitimate alerts",
            "• Lose 1 life for missing scams or false alarms",
            "",
            "Press SPACE to start protecting people from fraud!"
        ]
        
        y = 230
        for instruction in instructions:
            if instruction:
                if instruction.startswith("🎯") or instruction.startswith("Types") or instruction.startswith("Scoring"):
                    color = BLUE
                    font = self.text_font
                elif instruction.startswith("•") or instruction.startswith("📧"):
                    color = DARK_GRAY
                    font = self.small_font
                else:
                    color = BLACK
                    font = self.text_font
                    
                text = font.render(instruction, True, color)
                text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
                self.screen.blit(text, text_rect)
            y += 25
    
    def draw_game_over_screen(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Game over panel
        panel_width, panel_height = 500, 450
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_y = (SCREEN_HEIGHT - panel_height) // 2
        
        pygame.draw.rect(self.screen, WHITE, (panel_x, panel_y, panel_width, panel_height), border_radius=20)
        pygame.draw.rect(self.screen, BLACK, (panel_x, panel_y, panel_width, panel_height), 3, border_radius=20)
        
        # Title
        game_over_text = self.title_font.render("Game Over!", True, RED)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, panel_y + 50))
        self.screen.blit(game_over_text, game_over_rect)
        
        # Final stats
        total_alerts = self.scams_caught + self.scams_missed + self.false_positives + self.legitimate_ignored
        accuracy = (self.scams_caught + self.legitimate_ignored) / max(1, total_alerts) * 100
        
        stats_y = panel_y + 100
        final_stats = [
            f"Final Score: {self.score}",
            f"Level Reached: {self.level}",
            f"Detection Accuracy: {accuracy:.1f}%",
            "",
            "📊 Detailed Performance:",
            f"✅ Scams Caught: {self.scams_caught}",
            f"❌ Scams Missed: {self.scams_missed}",
            f"⚠️ False Alarms: {self.false_positives}",
            f"✓ Legitimate Ignored: {self.legitimate_ignored}",
            "",
            "🏆 Security Rating:",
            self.get_security_rating(accuracy),
            "",
            "Press R to restart or ESC to quit"
        ]
        
        for stat in final_stats:
            if stat:
                if "Score" in stat or "Level" in stat:
                    color = BLUE
                elif stat.startswith("✅") or stat.startswith("✓"):
                    color = GREEN
                elif stat.startswith("❌") or stat.startswith("⚠️"):
                    color = RED
                elif "📊" in stat or "🏆" in stat:
                    color = PURPLE
                else:
                    color = BLACK
                    
                font = self.text_font if not stat.startswith("🏆 Security Rating:") else self.subtitle_font
                text = font.render(stat, True, color)
                text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, stats_y))
                self.screen.blit(text, text_rect)
            stats_y += 25
    
    def get_security_rating(self, accuracy):
        if accuracy >= 90:
            return "🥇 Cybersecurity Expert"
        elif accuracy >= 80:
            return "🥈 Security Professional" 
        elif accuracy >= 70:
            return "🥉 Fraud Detective"
        elif accuracy >= 60:
            return "🛡️ Security Aware"
        else:
            return "⚠️ Needs More Training"
    
    def save_progress(self):
        """Save fraud detection game progress"""
        progress = {
            'high_score': self.score,
            'max_level': self.level,
            'total_scams_caught': self.scams_caught,
            'total_scams_missed': self.scams_missed,
            'total_false_positives': self.false_positives,
            'games_played': 1
        }
        
        # Load and merge existing progress
        if os.path.exists('games/fraud_progress.json'):
            try:
                with open('games/fraud_progress.json', 'r') as f:
                    existing = json.load(f)
                    
                progress['high_score'] = max(progress['high_score'], existing.get('high_score', 0))
                progress['max_level'] = max(progress['max_level'], existing.get('max_level', 1))
                progress['total_scams_caught'] += existing.get('total_scams_caught', 0)
                progress['total_scams_missed'] += existing.get('total_scams_missed', 0)
                progress['total_false_positives'] += existing.get('total_false_positives', 0)
                progress['games_played'] += existing.get('games_played', 0)
                
            except (json.JSONDecodeError, KeyError):
                pass
                
        with open('games/fraud_progress.json', 'w') as f:
            json.dump(progress, f, indent=2)
    
    def reset_game(self):
        self.score = 0
        self.lives = 3
        self.level = 1
        self.scam_alerts = []
        self.spawn_timer = 0
        self.spawn_delay = 120
        self.time_elapsed = 0
        self.scams_caught = 0
        self.scams_missed = 0
        self.false_positives = 0
        self.legitimate_ignored = 0
        self.game_over = False
        self.current_tip = random.choice(self.fraud_tips)
        
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
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1 and self.game_active and not self.game_over:
                        self.handle_click(event.pos)
            
            if self.game_active and not self.game_over:
                self.update_game()
                self.draw_background()
                
                # Draw scam alerts
                for alert in self.scam_alerts:
                    alert.draw(self.screen, self.text_font, self.small_font)
                
                self.draw_ui()
                
            elif self.game_over:
                self.draw_background()
                for alert in self.scam_alerts:
                    alert.draw(self.screen, self.text_font, self.small_font)
                self.draw_ui()
                self.draw_game_over_screen()
            else:
                self.draw_start_screen()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        if self.game_over:
            self.save_progress()
        pygame.quit()

if __name__ == "__main__":
    game = FraudDetectionGame()
    game.run()
"""
Paisabuddy Database Connection Module
Handles all database operations for games and web activities
"""

import mysql.connector
from mysql.connector import Error
import json
import os
from datetime import datetime, timedelta
import hashlib
import secrets

class PaisabuddyDB:
    def __init__(self):
        self.connection = None
        self.config = {
            'host': 'localhost',
            'database': 'paisabuddy',
            'user': 'root',  # Update with your MySQL username
            'password': '0809202327',  # Update with your MySQL password - commonly 'root' or empty
            'port': 3306,
            'charset': 'utf8mb4',
            'autocommit': True
        }
        
    def connect(self):
        """Establish database connection"""
        try:
            if self.connection is None or not self.connection.is_connected():
                self.connection = mysql.connector.connect(**self.config)
                print("✅ Connected to MySQL database")
                
                # Ensure required game tables exist
                self.create_game_tables()
                
            return self.connection
        except Error as e:
            print(f"❌ Error connecting to MySQL: {e}")
            return None
    
    def disconnect(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("📝 Database connection closed")
    
    def create_game_tables(self):
        """Create additional tables for game progress tracking"""
        cursor = self.connection.cursor()
        
        try:
            # Game Sessions table for detailed game progress
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS GameSessions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    game_name VARCHAR(100) NOT NULL,
                    session_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    session_end TIMESTAMP NULL,
                    final_score INT DEFAULT 0,
                    level_reached INT DEFAULT 1,
                    items_collected JSON NULL,
                    achievements JSON NULL,
                    session_data JSON NULL,
                    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
                    INDEX idx_user_game (user_id, game_name),
                    INDEX idx_session_date (session_start DESC)
                )
            """)
            
            # Game Achievements table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS GameAchievements (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    game_name VARCHAR(100) NOT NULL,
                    achievement_name VARCHAR(150) NOT NULL,
                    achievement_description TEXT,
                    earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    achievement_data JSON NULL,
                    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
                    UNIQUE KEY unique_user_achievement (user_id, game_name, achievement_name),
                    INDEX idx_user_game_date (user_id, game_name, earned_at DESC)
                )
            """)
            
            # Web Activity Tracking table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS WebActivity (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    activity_type ENUM('quiz', 'lesson', 'challenge', 'portfolio', 'budget') NOT NULL,
                    activity_name VARCHAR(150) NOT NULL,
                    score INT DEFAULT 0,
                    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    time_spent INT DEFAULT 0,
                    activity_data JSON NULL,
                    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
                    INDEX idx_user_activity (user_id, activity_type),
                    INDEX idx_activity_date (completed_at DESC)
                )
            """)
            
            # Daily Streaks table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS DailyStreaks (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    activity_date DATE NOT NULL,
                    activities_completed INT DEFAULT 1,
                    points_earned INT DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
                    UNIQUE KEY unique_user_date (user_id, activity_date),
                    INDEX idx_user_date (user_id, activity_date DESC)
                )
            """)
            
            # Insert sample games into Games table if not exists
            cursor.execute("""
                INSERT IGNORE INTO Games (name, description, difficulty, category, file_path) VALUES
                ('Budget Balance', 'Learn expense management through action gameplay', 'Easy', 'Budget Management', 'budget_balance.py'),
                ('Investment Garden', 'Understand compound interest by growing investments', 'Medium', 'Investment', 'investment_growth.py'),
                ('Fraud Detective', 'Master scam detection and security awareness', 'Medium', 'Security', 'fraud_detection.py')
            """)
            
            print("✅ Game tables created/verified successfully")
            
        except Error as e:
            print(f"❌ Error creating game tables: {e}")
        finally:
            cursor.close()
    
    def get_or_create_user(self, username="demo_user", email="demo@paisabuddy.com", name="Demo User"):
        """Get existing user or create a demo user for games"""
        cursor = self.connection.cursor(dictionary=True)
        
        try:
            # Try to find existing user
            cursor.execute("SELECT * FROM Users WHERE username = %s", (username,))
            user = cursor.fetchone()
            
            if user:
                return user
            
            # Create demo user if not exists
            password_hash = self.hash_password("demo123")
            cursor.execute("""
                INSERT INTO Users (name, username, email, password_hash, balance, total_score) 
                VALUES (%s, %s, %s, %s, 100000.00, 0)
            """, (name, username, email, password_hash))
            
            user_id = cursor.lastrowid
            cursor.execute("SELECT * FROM Users WHERE id = %s", (user_id,))
            return cursor.fetchone()
            
        except Error as e:
            print(f"❌ Error managing user: {e}")
            return None
        finally:
            cursor.close()
    
    def start_game_session(self, user_id, game_name):
        """Start a new game session"""
        cursor = self.connection.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO GameSessions (user_id, game_name, session_start) 
                VALUES (%s, %s, %s)
            """, (user_id, game_name, datetime.now()))
            
            session_id = cursor.lastrowid
            print(f"🎮 Started game session {session_id} for {game_name}")
            return session_id
            
        except Error as e:
            print(f"❌ Error starting game session: {e}")
            return None
        finally:
            cursor.close()
    
    def update_game_progress(self, session_id, score=0, level=1, items_collected=None, session_data=None):
        """Update game progress during gameplay"""
        cursor = self.connection.cursor()
        
        try:
            update_data = {
                'final_score': score,
                'level_reached': level,
                'items_collected': json.dumps(items_collected) if items_collected else None,
                'session_data': json.dumps(session_data) if session_data else None
            }
            
            cursor.execute("""
                UPDATE GameSessions 
                SET final_score = %s, level_reached = %s, items_collected = %s, session_data = %s
                WHERE id = %s
            """, (score, level, update_data['items_collected'], update_data['session_data'], session_id))
            
        except Error as e:
            print(f"❌ Error updating game progress: {e}")
        finally:
            cursor.close()
    
    def end_game_session(self, session_id, final_score=0, achievements=None):
        """End game session and save final results"""
        cursor = self.connection.cursor()
        
        try:
            # Update session end time and final score
            cursor.execute("""
                UPDATE GameSessions 
                SET session_end = %s, final_score = %s, achievements = %s
                WHERE id = %s
            """, (datetime.now(), final_score, json.dumps(achievements) if achievements else None, session_id))
            
            # Get session info to update user total score
            cursor.execute("SELECT user_id, game_name FROM GameSessions WHERE id = %s", (session_id,))
            session_info = cursor.fetchone()
            
            if session_info:
                user_id = session_info[0]
                game_name = session_info[1]
                
                # Update user total score
                cursor.execute("""
                    UPDATE Users 
                    SET total_score = total_score + %s 
                    WHERE id = %s
                """, (final_score, user_id))
                
                # Record in UserProgress table
                cursor.execute("SELECT id FROM Games WHERE name = %s", (game_name,))
                game_result = cursor.fetchone()
                
                if game_result:
                    game_id = game_result[0]
                    cursor.execute("""
                        INSERT INTO UserProgress (user_id, game_id, score, completed_at) 
                        VALUES (%s, %s, %s, %s)
                    """, (user_id, game_id, final_score, datetime.now()))
                
                print(f"🏁 Game session {session_id} completed with score {final_score}")
            
        except Error as e:
            print(f"❌ Error ending game session: {e}")
        finally:
            cursor.close()
    
    def add_achievement(self, user_id, game_name, achievement_name, description="", achievement_data=None):
        """Add achievement for user"""
        cursor = self.connection.cursor()
        
        try:
            cursor.execute("""
                INSERT IGNORE INTO GameAchievements 
                (user_id, game_name, achievement_name, achievement_description, achievement_data) 
                VALUES (%s, %s, %s, %s, %s)
            """, (user_id, game_name, achievement_name, description, 
                  json.dumps(achievement_data) if achievement_data else None))
            
            if cursor.rowcount > 0:
                print(f"🏆 Achievement unlocked: {achievement_name}")
                return True
            return False
            
        except Error as e:
            print(f"❌ Error adding achievement: {e}")
            return False
        finally:
            cursor.close()
    
    def record_web_activity(self, user_id, activity_type, activity_name, score=0, time_spent=0, activity_data=None):
        """Record web-based activity (quiz, lesson, etc.)"""
        cursor = self.connection.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO WebActivity 
                (user_id, activity_type, activity_name, score, time_spent, activity_data) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (user_id, activity_type, activity_name, score, time_spent,
                  json.dumps(activity_data) if activity_data else None))
            
            # Update user total score
            cursor.execute("UPDATE Users SET total_score = total_score + %s WHERE id = %s", (score, user_id))
            
            # Update daily streak
            self.update_daily_streak(user_id, score)
            
            print(f"📝 Web activity recorded: {activity_name} (Score: {score})")
            
        except Error as e:
            print(f"❌ Error recording web activity: {e}")
        finally:
            cursor.close()
    
    def update_daily_streak(self, user_id, points=0):
        """Update daily streak for user"""
        cursor = self.connection.cursor()
        
        try:
            today = datetime.now().date()
            
            cursor.execute("""
                INSERT INTO DailyStreaks (user_id, activity_date, activities_completed, points_earned) 
                VALUES (%s, %s, 1, %s)
                ON DUPLICATE KEY UPDATE 
                activities_completed = activities_completed + 1,
                points_earned = points_earned + %s
            """, (user_id, today, points, points))
            
        except Error as e:
            print(f"❌ Error updating daily streak: {e}")
        finally:
            cursor.close()
    
    def get_user_stats(self, user_id):
        """Get comprehensive user statistics"""
        cursor = self.connection.cursor(dictionary=True)
        
        try:
            stats = {}
            
            # Basic user info
            cursor.execute("SELECT * FROM Users WHERE id = %s", (user_id,))
            stats['user'] = cursor.fetchone()
            
            # Game sessions summary
            cursor.execute("""
                SELECT game_name, 
                       COUNT(*) as sessions_played,
                       MAX(final_score) as highest_score,
                       AVG(final_score) as average_score,
                       MAX(level_reached) as max_level
                FROM GameSessions 
                WHERE user_id = %s 
                GROUP BY game_name
            """, (user_id,))
            stats['game_summary'] = cursor.fetchall()
            
            # Recent achievements
            cursor.execute("""
                SELECT game_name, achievement_name, earned_at 
                FROM GameAchievements 
                WHERE user_id = %s 
                ORDER BY earned_at DESC 
                LIMIT 10
            """, (user_id,))
            stats['recent_achievements'] = cursor.fetchall()
            
            # Daily streak
            cursor.execute("""
                SELECT COUNT(*) as streak_days 
                FROM DailyStreaks 
                WHERE user_id = %s 
                AND activity_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
            """, (user_id,))
            result = cursor.fetchone()
            stats['streak_days'] = result['streak_days'] if result else 0
            
            # Web activity summary
            cursor.execute("""
                SELECT activity_type, 
                       COUNT(*) as activities_completed,
                       SUM(score) as total_points
                FROM WebActivity 
                WHERE user_id = %s 
                GROUP BY activity_type
            """, (user_id,))
            stats['web_activity'] = cursor.fetchall()
            
            return stats
            
        except Error as e:
            print(f"❌ Error getting user stats: {e}")
            return None
        finally:
            cursor.close()
    
    def get_leaderboard(self, limit=10):
        """Get top users leaderboard"""
        cursor = self.connection.cursor(dictionary=True)
        
        try:
            cursor.execute("""
                SELECT u.name, u.username, u.total_score,
                       COUNT(gs.id) as games_played,
                       COUNT(ga.id) as achievements_earned
                FROM Users u
                LEFT JOIN GameSessions gs ON u.id = gs.user_id
                LEFT JOIN GameAchievements ga ON u.id = ga.user_id
                GROUP BY u.id
                ORDER BY u.total_score DESC
                LIMIT %s
            """, (limit,))
            
            return cursor.fetchall()
            
        except Error as e:
            print(f"❌ Error getting leaderboard: {e}")
            return []
        finally:
            cursor.close()
    
    @staticmethod
    def hash_password(password):
        """Hash password for storage"""
        return hashlib.sha256(password.encode()).hexdigest()

# Global database instance
db = PaisabuddyDB()

# Convenience functions for games
def init_db():
    """Initialize database connection"""
    return db.connect()

def close_db():
    """Close database connection"""
    db.disconnect()

def get_user(username="demo_user"):
    """Get or create user for games"""
    if db.connect():
        return db.get_or_create_user(username)
    return None

def start_game(user_id, game_name):
    """Start a new game session"""
    if db.connect():
        return db.start_game_session(user_id, game_name)
    return None

def save_game_progress(session_id, score, level, items_collected=None, session_data=None):
    """Save game progress"""
    if db.connect():
        db.update_game_progress(session_id, score, level, items_collected, session_data)

def finish_game(session_id, final_score, achievements=None):
    """End game and save results"""
    if db.connect():
        db.end_game_session(session_id, final_score, achievements)

def unlock_achievement(user_id, game_name, achievement_name, description=""):
    """Unlock achievement for user"""
    if db.connect():
        return db.add_achievement(user_id, game_name, achievement_name, description)
    return False

def record_quiz_activity(user_id, quiz_name, score, time_spent=0, answers=None):
    """Record web quiz activity"""
    if db.connect():
        db.record_web_activity(user_id, 'quiz', quiz_name, score, time_spent, answers)

def get_player_stats(user_id):
    """Get comprehensive player statistics"""
    if db.connect():
        return db.get_user_stats(user_id)
    return None
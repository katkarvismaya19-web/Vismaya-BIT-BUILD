#!/usr/bin/env python3
"""
Enhanced Paisabuddy Database Module
Supports advanced trading simulation, AI personalization, and social features
"""

import mysql.connector
from mysql.connector import Error
import hashlib
import json
import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedPaisabuddyDB:
    def __init__(self, host='localhost', user='root', password='0809202327', database='paisabuddy'):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                autocommit=True
            )
            logger.info("Connected to Paisabuddy database successfully!")
            return True
        except Error as e:
            logger.error(f"Error connecting to database: {e}")
            return False
    
    def create_enhanced_tables(self):
        """Create all enhanced tables for the platform"""
        if not self.connection:
            if not self.connect():
                return False
        
        cursor = self.connection.cursor()
        
        # Enhanced User Profile Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_profiles (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                risk_tolerance ENUM('conservative', 'moderate', 'aggressive') DEFAULT 'moderate',
                investment_goals JSON,
                personality_traits JSON,
                learning_style ENUM('visual', 'auditory', 'kinesthetic', 'reading') DEFAULT 'visual',
                preferred_language VARCHAR(10) DEFAULT 'en',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Historical Market Data
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historical_market_data (
                id INT AUTO_INCREMENT PRIMARY KEY,
                symbol VARCHAR(20) NOT NULL,
                date DATE NOT NULL,
                year INT NOT NULL,
                open_price DECIMAL(10,2),
                high_price DECIMAL(10,2),
                low_price DECIMAL(10,2),
                close_price DECIMAL(10,2),
                volume BIGINT,
                sector VARCHAR(50),
                market_cap_category ENUM('large', 'mid', 'small') DEFAULT 'large',
                INDEX idx_symbol_year (symbol, year),
                INDEX idx_date (date)
            )
        """)
        
        # Market Events & News
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS market_events (
                id INT AUTO_INCREMENT PRIMARY KEY,
                event_date DATE NOT NULL,
                year INT NOT NULL,
                event_type ENUM('crash', 'boom', 'policy', 'earnings', 'scandal', 'merger', 'ipo') NOT NULL,
                title VARCHAR(200) NOT NULL,
                description TEXT,
                impact_level ENUM('low', 'medium', 'high', 'extreme') DEFAULT 'medium',
                affected_sectors JSON,
                market_impact_percentage DECIMAL(5,2),
                learning_content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Trading Simulations
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trading_simulations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                simulation_type ENUM('intraday', 'longterm') NOT NULL,
                simulation_name VARCHAR(100),
                start_date DATE,
                current_date DATE,
                start_year INT,
                current_year INT,
                virtual_balance DECIMAL(15,2) DEFAULT 100000.00,
                total_invested DECIMAL(15,2) DEFAULT 0.00,
                current_portfolio_value DECIMAL(15,2) DEFAULT 100000.00,
                total_returns DECIMAL(15,2) DEFAULT 0.00,
                return_percentage DECIMAL(5,2) DEFAULT 0.00,
                status ENUM('active', 'paused', 'completed') DEFAULT 'active',
                settings JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Portfolio Holdings
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS portfolio_holdings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                simulation_id INT NOT NULL,
                symbol VARCHAR(20) NOT NULL,
                company_name VARCHAR(100),
                quantity INT NOT NULL,
                average_buy_price DECIMAL(10,2),
                current_price DECIMAL(10,2),
                total_investment DECIMAL(15,2),
                current_value DECIMAL(15,2),
                unrealized_pnl DECIMAL(15,2),
                sector VARCHAR(50),
                buy_date DATE,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (simulation_id) REFERENCES trading_simulations(id) ON DELETE CASCADE
            )
        """)
        
        # Trading Transactions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trading_transactions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                simulation_id INT NOT NULL,
                transaction_type ENUM('buy', 'sell') NOT NULL,
                symbol VARCHAR(20) NOT NULL,
                quantity INT NOT NULL,
                price DECIMAL(10,2) NOT NULL,
                total_amount DECIMAL(15,2) NOT NULL,
                transaction_date DATE NOT NULL,
                simulation_year INT,
                fees DECIMAL(8,2) DEFAULT 0.00,
                notes TEXT,
                ai_recommendation BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (simulation_id) REFERENCES trading_simulations(id) ON DELETE CASCADE
            )
        """)
        
        # Achievement System
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS achievements (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL UNIQUE,
                description TEXT NOT NULL,
                category ENUM('trading', 'learning', 'social', 'milestone', 'risk_management') NOT NULL,
                badge_icon VARCHAR(50),
                points_reward INT DEFAULT 0,
                requirements JSON,
                rarity ENUM('common', 'rare', 'epic', 'legendary') DEFAULT 'common',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # User Achievements
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_achievements (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                achievement_id INT NOT NULL,
                earned_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                progress_data JSON,
                UNIQUE KEY unique_user_achievement (user_id, achievement_id),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (achievement_id) REFERENCES achievements(id) ON DELETE CASCADE
            )
        """)
        
        # Trading Competitions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trading_competitions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                competition_type ENUM('monthly', 'weekly', 'event_based', 'challenge') NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                entry_fee INT DEFAULT 0,
                prize_pool JSON,
                rules JSON,
                max_participants INT DEFAULT 1000,
                current_participants INT DEFAULT 0,
                status ENUM('upcoming', 'active', 'completed', 'cancelled') DEFAULT 'upcoming',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Competition Participants
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS competition_participants (
                id INT AUTO_INCREMENT PRIMARY KEY,
                competition_id INT NOT NULL,
                user_id INT NOT NULL,
                simulation_id INT NOT NULL,
                entry_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                final_returns DECIMAL(5,2) DEFAULT 0.00,
                rank_position INT,
                prize_won VARCHAR(100),
                UNIQUE KEY unique_competition_user (competition_id, user_id),
                FOREIGN KEY (competition_id) REFERENCES trading_competitions(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (simulation_id) REFERENCES trading_simulations(id) ON DELETE CASCADE
            )
        """)
        
        # AI Behavioral Analysis
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ai_behavioral_analysis (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                analysis_date DATE NOT NULL,
                trading_patterns JSON,
                emotional_indicators JSON,
                risk_behavior_score DECIMAL(3,2),
                decision_quality_score DECIMAL(3,2),
                learning_progress JSON,
                recommendations JSON,
                personality_insights JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Social Features - Following System
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_follows (
                id INT AUTO_INCREMENT PRIMARY KEY,
                follower_id INT NOT NULL,
                following_id INT NOT NULL,
                followed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY unique_follow (follower_id, following_id),
                FOREIGN KEY (follower_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (following_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Community Posts & Discussions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS community_posts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                title VARCHAR(200),
                content TEXT NOT NULL,
                post_type ENUM('question', 'strategy', 'success_story', 'tip', 'news') NOT NULL,
                tags JSON,
                likes_count INT DEFAULT 0,
                comments_count INT DEFAULT 0,
                views_count INT DEFAULT 0,
                is_pinned BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Performance Analytics
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS performance_analytics (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                simulation_id INT NOT NULL,
                analysis_date DATE NOT NULL,
                total_return DECIMAL(5,2),
                annual_return DECIMAL(5,2),
                volatility DECIMAL(5,2),
                sharpe_ratio DECIMAL(5,2),
                max_drawdown DECIMAL(5,2),
                win_rate DECIMAL(5,2),
                average_holding_period INT,
                sector_allocation JSON,
                risk_metrics JSON,
                benchmark_comparison JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (simulation_id) REFERENCES trading_simulations(id) ON DELETE CASCADE
            )
        """)
        
        cursor.close()
        logger.info("Enhanced database tables created successfully!")
        return True
    
    def insert_sample_market_data(self):
        """Insert sample historical market data"""
        cursor = self.connection.cursor()
        
        # Sample Indian stocks with historical data patterns
        sample_stocks = [
            ('RELIANCE', 'Reliance Industries', 'energy'),
            ('TCS', 'Tata Consultancy Services', 'it'),
            ('INFY', 'Infosys', 'it'),
            ('HDFCBANK', 'HDFC Bank', 'banking'),
            ('ICICIBANK', 'ICICI Bank', 'banking'),
            ('ITC', 'ITC Limited', 'fmcg'),
            ('HINDUNILVR', 'Hindustan Unilever', 'fmcg'),
            ('BHARTIARTL', 'Bharti Airtel', 'telecom'),
            ('ADANIPORTS', 'Adani Ports', 'infrastructure'),
            ('MARUTI', 'Maruti Suzuki', 'auto')
        ]
        
        # Generate sample data for years 2004-2024
        import random
        for symbol, name, sector in sample_stocks:
            base_price = random.uniform(50, 500)
            
            for year in range(2004, 2025):
                # Simulate different market phases
                if year in [2008, 2020]:  # Crisis years
                    growth_factor = random.uniform(0.7, 0.9)
                elif year in [2009, 2014, 2021]:  # Recovery years
                    growth_factor = random.uniform(1.1, 1.4)
                else:  # Normal years
                    growth_factor = random.uniform(0.95, 1.15)
                
                year_price = base_price * growth_factor
                
                # Insert yearly data point
                cursor.execute("""
                    INSERT INTO historical_market_data 
                    (symbol, date, year, open_price, high_price, low_price, close_price, volume, sector, market_cap_category)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE close_price = VALUES(close_price)
                """, (
                    symbol, f"{year}-12-31", year,
                    year_price, year_price * 1.05, year_price * 0.95, year_price,
                    random.randint(1000000, 50000000), sector, 'large'
                ))
                
                base_price = year_price
        
        cursor.close()
        logger.info("Sample market data inserted!")
    
    def insert_sample_events(self):
        """Insert sample historical market events"""
        cursor = self.connection.cursor()
        
        major_events = [
            (2008, '2008-09-15', 'crash', 'Global Financial Crisis', 'Lehman Brothers collapse triggers global recession', 'extreme', -40, '["banking", "real_estate", "it"]'),
            (2016, '2016-11-08', 'policy', 'Demonetization Announced', 'Indian government invalidates high-value currency notes', 'high', -5, '["banking", "retail", "real_estate"]'),
            (2020, '2020-03-23', 'crash', 'COVID-19 Market Crash', 'Pandemic fears cause massive market selloff', 'extreme', -35, '["travel", "hospitality", "retail"]'),
            (2021, '2021-02-01', 'boom', 'Post-COVID Recovery Rally', 'Markets surge as vaccine rollout begins', 'high', 25, '["pharma", "it", "chemicals"]'),
            (2009, '2009-03-09', 'boom', 'Market Bottom Recovery', 'Markets begin historic recovery from crisis lows', 'high', 30, '["banking", "auto", "metals"]'),
            (2014, '2014-05-16', 'policy', 'Modi Government Elected', 'New government promises economic reforms', 'medium', 15, '["infrastructure", "banking", "manufacturing"]'),
            (2017, '2017-07-01', 'policy', 'GST Implementation', 'Goods and Services Tax launched nationwide', 'medium', -3, '["retail", "logistics", "fmcg"]'),
            (2019, '2019-08-30', 'policy', 'Corporate Tax Cut', 'Government slashes corporate tax rates', 'high', 8, '["banking", "auto", "metals"]')
        ]
        
        for year, date, event_type, title, desc, impact, market_impact, sectors in major_events:
            cursor.execute("""
                INSERT INTO market_events 
                (event_date, year, event_type, title, description, impact_level, market_impact_percentage, affected_sectors)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE description = VALUES(description)
            """, (date, year, event_type, title, desc, impact, market_impact, sectors))
        
        cursor.close()
        logger.info("Sample market events inserted!")
    
    def insert_sample_achievements(self):
        """Insert sample achievements"""
        cursor = self.connection.cursor()
        
        achievements_data = [
            # Trading Achievements
            ('First Trade', 'Complete your first stock transaction', 'trading', '🎯', 100, '{"trades_count": 1}', 'common'),
            ('Paper Hands', 'Sell a stock within 24 hours of buying', 'trading', '🧻', 50, '{"quick_sells": 1}', 'common'),
            ('Diamond Hands', 'Hold a stock for over 5 years in simulation', 'trading', '💎', 500, '{"long_holds": 1}', 'rare'),
            ('Crash Survivor', 'Maintain portfolio value during a market crash', 'trading', '🛡️', 750, '{"survive_crash": True}', 'epic'),
            ('Bull Market Champion', 'Achieve 25%+ returns during bull market', 'trading', '🐂', 300, '{"bull_returns": 25}', 'rare'),
            ('Bear Market Warrior', 'Limit losses to <10% during bear market', 'trading', '🐻', 400, '{"bear_losses": -10}', 'rare'),
            ('Diversification Master', 'Hold stocks from 5+ different sectors', 'risk_management', '🎭', 200, '{"sectors_count": 5}', 'common'),
            ('Value Investor', 'Successfully pick undervalued stocks', 'trading', '💰', 600, '{"value_picks": 3}', 'epic'),
            
            # Learning Achievements
            ('Knowledge Seeker', 'Complete first learning module', 'learning', '📚', 150, '{"modules_completed": 1}', 'common'),
            ('Finance Graduate', 'Complete all basic modules', 'learning', '🎓', 1000, '{"all_basic_modules": True}', 'rare'),
            ('Quiz Master', 'Score 90%+ on 5 consecutive quizzes', 'learning', '🧠', 250, '{"quiz_streak": 5, "min_score": 90}', 'common'),
            
            # Social Achievements
            ('Helper', 'Answer 10 community questions', 'social', '🤝', 200, '{"answers_count": 10}', 'common'),
            ('Mentor', 'Help 5 new users get started', 'social', '👨‍🏫', 500, '{"mentees": 5}', 'rare'),
            ('Community Leader', 'Get 100+ likes on posts', 'social', '⭐', 300, '{"total_likes": 100}', 'rare'),
            
            # Milestone Achievements
            ('Millionaire Club', 'Reach ₹10 lakh portfolio value', 'milestone', '💸', 1000, '{"portfolio_value": 1000000}', 'legendary'),
            ('Consistent Performer', 'Positive returns for 12 consecutive months', 'milestone', '📈', 800, '{"consistent_months": 12}', 'epic'),
            ('Speed Trader', 'Complete 100 trades in intraday mode', 'milestone', '⚡', 400, '{"intraday_trades": 100}', 'rare')
        ]
        
        for name, desc, category, icon, points, requirements, rarity in achievements_data:
            cursor.execute("""
                INSERT INTO achievements (name, description, category, badge_icon, points_reward, requirements, rarity)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE description = VALUES(description)
            """, (name, desc, category, icon, points, requirements, rarity))
        
        cursor.close()
        logger.info("Sample achievements inserted!")

# Initialize and setup functions
def setup_enhanced_database():
    """Setup the enhanced database with all tables and sample data"""
    db = EnhancedPaisabuddyDB()
    
    if not db.connect():
        print("Failed to connect to database!")
        return False
    
    print("Creating enhanced database tables...")
    if not db.create_enhanced_tables():
        print("Failed to create tables!")
        return False
    
    print("Inserting sample market data...")
    db.insert_sample_market_data()
    
    print("Inserting sample market events...")
    db.insert_sample_events()
    
    print("Inserting sample achievements...")
    db.insert_sample_achievements()
    
    print("✅ Enhanced database setup completed successfully!")
    return True

if __name__ == "__main__":
    setup_enhanced_database()
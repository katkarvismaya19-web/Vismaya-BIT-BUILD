#!/usr/bin/env python3
"""
Enhanced Engagement System for Paisabuddy
Handles achievements, social features, leaderboards, and competitions
"""

import json
import mysql.connector
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Any, Tuple
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class AchievementCategory(Enum):
    TRADING = "trading"
    LEARNING = "learning"
    SOCIAL = "social"
    MILESTONE = "milestone"
    RISK_MANAGEMENT = "risk_management"

class CompetitionType(Enum):
    MONTHLY = "monthly"
    WEEKLY = "weekly"
    EVENT_BASED = "event_based"
    CHALLENGE = "challenge"

@dataclass
class Achievement:
    id: int
    name: str
    description: str
    category: str
    badge_icon: str
    points_reward: int
    requirements: Dict
    rarity: str

class EngagementSystem:
    def __init__(self, db_connection):
        self.db = db_connection
        
    def check_and_award_achievements(self, user_id: int, activity_type: str = 'all') -> List[Dict]:
        """Check user's activities and award appropriate achievements"""
        cursor = self.db.cursor(dictionary=True)
        newly_earned = []
        
        try:
            # Get all available achievements
            cursor.execute("""
                SELECT * FROM achievements 
                WHERE id NOT IN (
                    SELECT achievement_id FROM user_achievements WHERE user_id = %s
                )
            """, (user_id,))
            
            available_achievements = cursor.fetchall()
            
            # Check each achievement
            for achievement in available_achievements:
                if self._check_achievement_requirement(user_id, achievement):
                    # Award achievement
                    cursor.execute("""
                        INSERT INTO user_achievements (user_id, achievement_id, progress_data)
                        VALUES (%s, %s, %s)
                    """, (user_id, achievement['id'], json.dumps({'earned_date': str(datetime.now())})))
                    
                    newly_earned.append({
                        'id': achievement['id'],
                        'name': achievement['name'],
                        'description': achievement['description'],
                        'badge_icon': achievement['badge_icon'],
                        'points_reward': achievement['points_reward'],
                        'rarity': achievement['rarity']
                    })
                    
                    logger.info(f"Awarded achievement '{achievement['name']}' to user {user_id}")
            
            self.db.commit()
            return newly_earned
            
        except Exception as e:
            logger.error(f"Error checking achievements: {e}")
            return []
        finally:
            cursor.close()
    
    def _check_achievement_requirement(self, user_id: int, achievement: Dict) -> bool:
        """Check if user meets the requirements for a specific achievement"""
        requirements = json.loads(achievement['requirements'])
        cursor = self.db.cursor(dictionary=True)
        
        try:
            # Trading achievements
            if achievement['category'] == 'trading':
                return self._check_trading_achievements(user_id, achievement['name'], requirements, cursor)
            
            # Learning achievements  
            elif achievement['category'] == 'learning':
                return self._check_learning_achievements(user_id, achievement['name'], requirements, cursor)
            
            # Social achievements
            elif achievement['category'] == 'social':
                return self._check_social_achievements(user_id, achievement['name'], requirements, cursor)
            
            # Milestone achievements
            elif achievement['category'] == 'milestone':
                return self._check_milestone_achievements(user_id, achievement['name'], requirements, cursor)
            
            # Risk management achievements
            elif achievement['category'] == 'risk_management':
                return self._check_risk_management_achievements(user_id, achievement['name'], requirements, cursor)
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking achievement requirement: {e}")
            return False
        finally:
            cursor.close()
    
    def _check_trading_achievements(self, user_id: int, achievement_name: str, requirements: Dict, cursor) -> bool:
        """Check trading-related achievements"""
        
        if achievement_name == "First Trade":
            cursor.execute("""
                SELECT COUNT(*) as count FROM trading_transactions tt
                JOIN trading_simulations ts ON tt.simulation_id = ts.id
                WHERE ts.user_id = %s
            """, (user_id,))
            result = cursor.fetchone()
            return result['count'] >= requirements.get('trades_count', 1)
        
        elif achievement_name == "Paper Hands":
            # Check for trades held less than 24 hours
            cursor.execute("""
                SELECT COUNT(*) as count FROM (
                    SELECT tt1.symbol, tt1.created_at as buy_time, MIN(tt2.created_at) as sell_time
                    FROM trading_transactions tt1
                    JOIN trading_transactions tt2 ON tt1.simulation_id = tt2.simulation_id 
                        AND tt1.symbol = tt2.symbol
                    JOIN trading_simulations ts ON tt1.simulation_id = ts.id
                    WHERE ts.user_id = %s AND tt1.transaction_type = 'buy' 
                        AND tt2.transaction_type = 'sell' AND tt2.created_at > tt1.created_at
                    GROUP BY tt1.symbol, tt1.created_at
                    HAVING TIMESTAMPDIFF(HOUR, buy_time, sell_time) < 24
                ) as quick_sells
            """, (user_id,))
            result = cursor.fetchone()
            return result['count'] >= requirements.get('quick_sells', 1)
        
        elif achievement_name == "Diamond Hands":
            # Check for positions held over 5 years in long-term simulation
            cursor.execute("""
                SELECT COUNT(*) as count FROM portfolio_holdings ph
                JOIN trading_simulations ts ON ph.simulation_id = ts.id
                WHERE ts.user_id = %s AND ts.simulation_type = 'longterm'
                    AND DATEDIFF(ts.current_date, ph.buy_date) >= 1825
            """, (user_id,))
            result = cursor.fetchone()
            return result['count'] >= requirements.get('long_holds', 1)
        
        elif achievement_name == "Bull Market Champion":
            cursor.execute("""
                SELECT MAX(return_percentage) as max_return FROM trading_simulations
                WHERE user_id = %s AND return_percentage > 0
            """, (user_id,))
            result = cursor.fetchone()
            return result['max_return'] and result['max_return'] >= requirements.get('bull_returns', 25)
        
        elif achievement_name == "Crash Survivor":
            # Check if maintained portfolio value during major crash events
            cursor.execute("""
                SELECT ts.*, ph.current_value
                FROM trading_simulations ts
                LEFT JOIN portfolio_holdings ph ON ts.id = ph.simulation_id
                WHERE ts.user_id = %s AND ts.simulation_type = 'longterm'
                    AND ts.current_year IN (2008, 2020)  -- Crash years
                    AND ts.return_percentage > -20  -- Lost less than 20%
            """, (user_id,))
            result = cursor.fetchone()
            return result is not None
        
        return False
    
    def _check_learning_achievements(self, user_id: int, achievement_name: str, requirements: Dict, cursor) -> bool:
        """Check learning-related achievements"""
        
        if achievement_name == "Knowledge Seeker":
            # Check completion of learning modules (simulated with game activities)
            cursor.execute("""
                SELECT COUNT(DISTINCT COALESCE(session_id, game_type)) as modules 
                FROM GameSessions WHERE user_id = %s
            """, (user_id,))
            result = cursor.fetchone()
            return result['modules'] >= requirements.get('modules_completed', 1)
        
        elif achievement_name == "Quiz Master":
            # Check for high quiz scores (simulated with game scores)
            cursor.execute("""
                SELECT COUNT(*) as streak FROM (
                    SELECT score FROM GameSessions 
                    WHERE user_id = %s AND score >= %s
                    ORDER BY session_date DESC LIMIT %s
                ) as recent_scores
            """, (user_id, requirements.get('min_score', 90), requirements.get('quiz_streak', 5)))
            result = cursor.fetchone()
            return result['streak'] == requirements.get('quiz_streak', 5)
        
        return False
    
    def _check_social_achievements(self, user_id: int, achievement_name: str, requirements: Dict, cursor) -> bool:
        """Check social-related achievements"""
        
        if achievement_name == "Community Leader":
            cursor.execute("""
                SELECT SUM(likes_count) as total_likes FROM community_posts 
                WHERE user_id = %s
            """, (user_id,))
            result = cursor.fetchone()
            return result['total_likes'] and result['total_likes'] >= requirements.get('total_likes', 100)
        
        elif achievement_name == "Helper":
            cursor.execute("""
                SELECT COUNT(*) as answers FROM community_posts 
                WHERE user_id = %s AND post_type = 'question'
            """, (user_id,))
            result = cursor.fetchone()
            return result['answers'] >= requirements.get('answers_count', 10)
        
        return False
    
    def _check_milestone_achievements(self, user_id: int, achievement_name: str, requirements: Dict, cursor) -> bool:
        """Check milestone achievements"""
        
        if achievement_name == "Millionaire Club":
            cursor.execute("""
                SELECT MAX(current_portfolio_value) as max_value FROM trading_simulations
                WHERE user_id = %s
            """, (user_id,))
            result = cursor.fetchone()
            return result['max_value'] and result['max_value'] >= requirements.get('portfolio_value', 1000000)
        
        elif achievement_name == "Speed Trader":
            cursor.execute("""
                SELECT COUNT(*) as intraday_trades FROM trading_transactions tt
                JOIN trading_simulations ts ON tt.simulation_id = ts.id
                WHERE ts.user_id = %s AND ts.simulation_type = 'intraday'
            """, (user_id,))
            result = cursor.fetchone()
            return result['intraday_trades'] >= requirements.get('intraday_trades', 100)
        
        return False
    
    def _check_risk_management_achievements(self, user_id: int, achievement_name: str, requirements: Dict, cursor) -> bool:
        """Check risk management achievements"""
        
        if achievement_name == "Diversification Master":
            cursor.execute("""
                SELECT COUNT(DISTINCT sector) as sectors FROM portfolio_holdings ph
                JOIN trading_simulations ts ON ph.simulation_id = ts.id
                WHERE ts.user_id = %s AND ts.status = 'active'
            """, (user_id,))
            result = cursor.fetchone()
            return result['sectors'] >= requirements.get('sectors_count', 5)
        
        return False
    
    def get_user_achievements(self, user_id: int) -> Dict:
        """Get user's achievement statistics and badges"""
        cursor = self.db.cursor(dictionary=True)
        
        try:
            # Get earned achievements
            cursor.execute("""
                SELECT ua.*, a.name, a.description, a.badge_icon, a.points_reward, a.rarity, a.category
                FROM user_achievements ua
                JOIN achievements a ON ua.achievement_id = a.id
                WHERE ua.user_id = %s
                ORDER BY ua.earned_date DESC
            """, (user_id,))
            
            earned_achievements = cursor.fetchall()
            
            # Calculate statistics
            total_points = sum(a['points_reward'] for a in earned_achievements)
            
            categories = {}
            rarity_counts = {'common': 0, 'rare': 0, 'epic': 0, 'legendary': 0}
            
            for achievement in earned_achievements:
                category = achievement['category']
                categories[category] = categories.get(category, 0) + 1
                rarity_counts[achievement['rarity']] += 1
            
            # Get total available achievements
            cursor.execute("SELECT COUNT(*) as total FROM achievements")
            total_available = cursor.fetchone()['total']
            
            completion_percentage = (len(earned_achievements) / total_available) * 100 if total_available > 0 else 0
            
            return {
                'earned_achievements': earned_achievements,
                'total_earned': len(earned_achievements),
                'total_available': total_available,
                'completion_percentage': round(completion_percentage, 1),
                'total_points': total_points,
                'categories': categories,
                'rarity_breakdown': rarity_counts,
                'recent_achievements': earned_achievements[:5]  # Last 5 earned
            }
            
        except Exception as e:
            logger.error(f"Error getting user achievements: {e}")
            return {'earned_achievements': [], 'total_earned': 0, 'total_points': 0}
        finally:
            cursor.close()
    
    def create_leaderboard(self, leaderboard_type: str = 'overall', time_period: str = 'all_time') -> List[Dict]:
        """Create various types of leaderboards"""
        cursor = self.db.cursor(dictionary=True)
        
        try:
            if leaderboard_type == 'overall':
                # Overall points leaderboard
                cursor.execute("""
                    SELECT u.username, u.email, SUM(a.points_reward) as total_points,
                           COUNT(ua.achievement_id) as achievement_count
                    FROM users u
                    JOIN user_achievements ua ON u.id = ua.user_id
                    JOIN achievements a ON ua.achievement_id = a.id
                    GROUP BY u.id, u.username, u.email
                    ORDER BY total_points DESC, achievement_count DESC
                    LIMIT 100
                """)
            
            elif leaderboard_type == 'trading_performance':
                # Trading performance leaderboard
                cursor.execute("""
                    SELECT u.username, u.email, 
                           MAX(ts.return_percentage) as best_return,
                           AVG(ts.return_percentage) as avg_return,
                           COUNT(ts.id) as simulations_count
                    FROM users u
                    JOIN trading_simulations ts ON u.id = ts.user_id
                    WHERE ts.status IN ('active', 'completed')
                    GROUP BY u.id, u.username, u.email
                    HAVING simulations_count >= 1
                    ORDER BY best_return DESC
                    LIMIT 100
                """)
            
            elif leaderboard_type == 'social':
                # Social engagement leaderboard
                cursor.execute("""
                    SELECT u.username, u.email,
                           COUNT(cp.id) as posts_count,
                           SUM(cp.likes_count) as total_likes,
                           SUM(cp.comments_count) as total_comments
                    FROM users u
                    LEFT JOIN community_posts cp ON u.id = cp.user_id
                    GROUP BY u.id, u.username, u.email
                    HAVING posts_count > 0
                    ORDER BY total_likes DESC, posts_count DESC
                    LIMIT 100
                """)
            
            elif leaderboard_type == 'learning':
                # Learning progress leaderboard
                cursor.execute("""
                    SELECT u.username, u.email,
                           COUNT(CASE WHEN a.category = 'learning' THEN 1 END) as learning_achievements,
                           COUNT(ua.achievement_id) as total_achievements,
                           SUM(a.points_reward) as total_points
                    FROM users u
                    LEFT JOIN user_achievements ua ON u.id = ua.user_id
                    LEFT JOIN achievements a ON ua.achievement_id = a.id
                    GROUP BY u.id, u.username, u.email
                    HAVING total_achievements > 0
                    ORDER BY learning_achievements DESC, total_points DESC
                    LIMIT 100
                """)
            
            results = cursor.fetchall()
            
            # Add rankings
            for i, user in enumerate(results, 1):
                user['rank'] = i
            
            return results
            
        except Exception as e:
            logger.error(f"Error creating leaderboard: {e}")
            return []
        finally:
            cursor.close()
    
    def create_trading_competition(self, name: str, description: str, 
                                  start_date: date, end_date: date, 
                                  competition_type: str = 'monthly',
                                  prize_pool: Dict = None,
                                  rules: Dict = None) -> Optional[int]:
        """Create a new trading competition"""
        cursor = self.db.cursor()
        
        try:
            default_prize_pool = {
                '1st': 'Gold Badge + 5000 Points',
                '2nd': 'Silver Badge + 3000 Points', 
                '3rd': 'Bronze Badge + 1000 Points'
            }
            
            default_rules = {
                'starting_balance': 100000,
                'simulation_type': 'intraday',
                'max_participants': 1000,
                'minimum_trades': 5,
                'evaluation_metric': 'total_return'
            }
            
            cursor.execute("""
                INSERT INTO trading_competitions 
                (name, description, competition_type, start_date, end_date, prize_pool, rules)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                name, description, competition_type, start_date, end_date,
                json.dumps(prize_pool or default_prize_pool),
                json.dumps(rules or default_rules)
            ))
            
            competition_id = cursor.lastrowid
            self.db.commit()
            
            logger.info(f"Created trading competition: {name} (ID: {competition_id})")
            return competition_id
            
        except Exception as e:
            logger.error(f"Error creating competition: {e}")
            return None
        finally:
            cursor.close()
    
    def join_competition(self, user_id: int, competition_id: int) -> bool:
        """Allow user to join a trading competition"""
        cursor = self.db.cursor()
        
        try:
            # Check if competition is active and has space
            cursor.execute("""
                SELECT * FROM trading_competitions 
                WHERE id = %s AND status = 'upcoming' 
                AND current_participants < max_participants
                AND start_date > CURDATE()
            """, (competition_id,))
            
            competition = cursor.fetchone()
            if not competition:
                return False
            
            # Check if user already joined
            cursor.execute("""
                SELECT id FROM competition_participants 
                WHERE competition_id = %s AND user_id = %s
            """, (competition_id, user_id))
            
            if cursor.fetchone():
                return False  # Already joined
            
            # Create simulation for the competition
            rules = json.loads(competition[7])  # rules column
            
            # Create a new trading simulation for this competition
            cursor.execute("""
                INSERT INTO trading_simulations 
                (user_id, simulation_type, simulation_name, virtual_balance, current_portfolio_value, settings)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                user_id, rules.get('simulation_type', 'intraday'),
                f"Competition: {competition[1]}", rules.get('starting_balance', 100000),
                rules.get('starting_balance', 100000), json.dumps(rules)
            ))
            
            simulation_id = cursor.lastrowid
            
            # Join competition
            cursor.execute("""
                INSERT INTO competition_participants 
                (competition_id, user_id, simulation_id)
                VALUES (%s, %s, %s)
            """, (competition_id, user_id, simulation_id))
            
            # Update participant count
            cursor.execute("""
                UPDATE trading_competitions 
                SET current_participants = current_participants + 1
                WHERE id = %s
            """, (competition_id,))
            
            self.db.commit()
            logger.info(f"User {user_id} joined competition {competition_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error joining competition: {e}")
            return False
        finally:
            cursor.close()
    
    def get_active_competitions(self) -> List[Dict]:
        """Get list of active competitions"""
        cursor = self.db.cursor(dictionary=True)
        
        try:
            cursor.execute("""
                SELECT * FROM trading_competitions 
                WHERE status IN ('upcoming', 'active')
                ORDER BY start_date ASC
            """)
            
            competitions = cursor.fetchall()
            
            # Parse JSON fields and add participant info
            for competition in competitions:
                competition['prize_pool'] = json.loads(competition['prize_pool'])
                competition['rules'] = json.loads(competition['rules'])
                
                # Get participant count and top performers
                cursor.execute("""
                    SELECT COUNT(*) as count FROM competition_participants 
                    WHERE competition_id = %s
                """, (competition['id'],))
                
                competition['participant_count'] = cursor.fetchone()['count']
            
            return competitions
            
        except Exception as e:
            logger.error(f"Error getting active competitions: {e}")
            return []
        finally:
            cursor.close()
    
    def get_competition_leaderboard(self, competition_id: int) -> List[Dict]:
        """Get leaderboard for specific competition"""
        cursor = self.db.cursor(dictionary=True)
        
        try:
            cursor.execute("""
                SELECT u.username, cp.final_returns, cp.rank_position,
                       ts.return_percentage, ts.current_portfolio_value,
                       COUNT(tt.id) as trade_count
                FROM competition_participants cp
                JOIN users u ON cp.user_id = u.id
                JOIN trading_simulations ts ON cp.simulation_id = ts.id
                LEFT JOIN trading_transactions tt ON ts.id = tt.simulation_id
                WHERE cp.competition_id = %s
                GROUP BY cp.id, u.username, cp.final_returns, cp.rank_position,
                         ts.return_percentage, ts.current_portfolio_value
                ORDER BY ts.return_percentage DESC
            """, (competition_id,))
            
            leaderboard = cursor.fetchall()
            
            # Add current rankings
            for i, participant in enumerate(leaderboard, 1):
                participant['current_rank'] = i
            
            return leaderboard
            
        except Exception as e:
            logger.error(f"Error getting competition leaderboard: {e}")
            return []
        finally:
            cursor.close()
    
    def create_social_post(self, user_id: int, title: str, content: str, 
                          post_type: str = 'question', tags: List[str] = None) -> Optional[int]:
        """Create a new social post"""
        cursor = self.db.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO community_posts 
                (user_id, title, content, post_type, tags)
                VALUES (%s, %s, %s, %s, %s)
            """, (user_id, title, content, post_type, json.dumps(tags or [])))
            
            post_id = cursor.lastrowid
            self.db.commit()
            
            # Check for social achievements
            self.check_and_award_achievements(user_id, 'social')
            
            return post_id
            
        except Exception as e:
            logger.error(f"Error creating social post: {e}")
            return None
        finally:
            cursor.close()
    
    def get_community_feed(self, user_id: int = None, limit: int = 50) -> List[Dict]:
        """Get community feed posts"""
        cursor = self.db.cursor(dictionary=True)
        
        try:
            cursor.execute("""
                SELECT cp.*, u.username,
                       (SELECT COUNT(*) FROM user_follows WHERE following_id = cp.user_id) as follower_count
                FROM community_posts cp
                JOIN users u ON cp.user_id = u.id
                ORDER BY cp.created_at DESC
                LIMIT %s
            """, (limit,))
            
            posts = cursor.fetchall()
            
            # Parse tags
            for post in posts:
                post['tags'] = json.loads(post['tags']) if post['tags'] else []
            
            return posts
            
        except Exception as e:
            logger.error(f"Error getting community feed: {e}")
            return []
        finally:
            cursor.close()
    
    def get_user_stats_summary(self, user_id: int) -> Dict:
        """Get comprehensive user statistics for dashboard"""
        cursor = self.db.cursor(dictionary=True)
        
        try:
            stats = {}
            
            # Achievement stats
            cursor.execute("""
                SELECT COUNT(*) as earned, SUM(a.points_reward) as points
                FROM user_achievements ua
                JOIN achievements a ON ua.achievement_id = a.id
                WHERE ua.user_id = %s
            """, (user_id,))
            
            achievement_stats = cursor.fetchone()
            stats['achievements'] = {
                'earned': achievement_stats['earned'] or 0,
                'total_points': achievement_stats['points'] or 0
            }
            
            # Trading stats
            cursor.execute("""
                SELECT COUNT(*) as simulations, 
                       AVG(return_percentage) as avg_return,
                       MAX(return_percentage) as best_return,
                       SUM(CASE WHEN return_percentage > 0 THEN 1 ELSE 0 END) as profitable_sims
                FROM trading_simulations
                WHERE user_id = %s
            """, (user_id,))
            
            trading_stats = cursor.fetchone()
            stats['trading'] = {
                'simulations': trading_stats['simulations'] or 0,
                'avg_return': round(float(trading_stats['avg_return'] or 0), 2),
                'best_return': round(float(trading_stats['best_return'] or 0), 2),
                'win_rate': round(((trading_stats['profitable_sims'] or 0) / max(1, trading_stats['simulations'] or 1)) * 100, 1)
            }
            
            # Social stats
            cursor.execute("""
                SELECT COUNT(*) as posts, SUM(likes_count) as total_likes,
                       (SELECT COUNT(*) FROM user_follows WHERE follower_id = %s) as following,
                       (SELECT COUNT(*) FROM user_follows WHERE following_id = %s) as followers
                FROM community_posts
                WHERE user_id = %s
            """, (user_id, user_id, user_id))
            
            social_stats = cursor.fetchone()
            stats['social'] = {
                'posts': social_stats['posts'] or 0,
                'total_likes': social_stats['total_likes'] or 0,
                'following': social_stats['following'] or 0,
                'followers': social_stats['followers'] or 0
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting user stats summary: {e}")
            return {'achievements': {}, 'trading': {}, 'social': {}}
        finally:
            cursor.close()

# Factory function
def create_engagement_system(db_connection):
    """Create engagement system instance"""
    return EngagementSystem(db_connection)
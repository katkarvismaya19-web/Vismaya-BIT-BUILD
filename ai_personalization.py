#!/usr/bin/env python3
"""
AI-Powered Personalization Engine for Paisabuddy
Provides behavioral analysis, personalized recommendations, and adaptive learning
"""

import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class RiskTolerance(Enum):
    CONSERVATIVE = "conservative"
    MODERATE = "moderate" 
    AGGRESSIVE = "aggressive"

class TradingPattern(Enum):
    DAY_TRADER = "day_trader"
    SWING_TRADER = "swing_trader"
    LONG_TERM_INVESTOR = "long_term_investor"
    PANIC_TRADER = "panic_trader"
    MOMENTUM_TRADER = "momentum_trader"

class EmotionalState(Enum):
    CONFIDENT = "confident"
    FEARFUL = "fearful"
    GREEDY = "greedy"
    DISCIPLINED = "disciplined"
    IMPULSIVE = "impulsive"

@dataclass
class BehavioralInsight:
    pattern: str
    confidence: float
    description: str
    recommendation: str
    impact_level: str

class AIPersonalizationEngine:
    def __init__(self, db_connection):
        self.db = db_connection
        
    def analyze_user_behavior(self, user_id: int, days_back: int = 90) -> Dict:
        """Comprehensive analysis of user's trading behavior"""
        cursor = self.db.cursor(dictionary=True)
        
        try:
            # Get user's trading simulations and transactions
            cursor.execute("""
                SELECT ts.*, tt.* FROM trading_simulations ts
                LEFT JOIN trading_transactions tt ON ts.id = tt.simulation_id
                WHERE ts.user_id = %s AND ts.created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
                ORDER BY tt.created_at DESC
            """, (user_id, days_back))
            
            data = cursor.fetchall()
            
            if not data:
                return self._create_default_analysis(user_id)
            
            # Separate simulation and transaction data
            simulations = {}
            transactions = []
            
            for row in data:
                sim_id = row.get('id')
                if sim_id and sim_id not in simulations:
                    simulations[sim_id] = {
                        'simulation_type': row.get('simulation_type'),
                        'return_percentage': row.get('return_percentage', 0),
                        'total_returns': row.get('total_returns', 0),
                        'current_portfolio_value': row.get('current_portfolio_value', 0),
                        'start_date': row.get('start_date'),
                        'transactions': []
                    }
                
                if row.get('transaction_type'):
                    transaction = {
                        'simulation_id': row.get('simulation_id'),
                        'type': row.get('transaction_type'),
                        'symbol': row.get('symbol'),
                        'quantity': row.get('quantity'),
                        'price': float(row.get('price', 0)),
                        'total_amount': float(row.get('total_amount', 0)),
                        'created_at': row.get('created_at')
                    }
                    transactions.append(transaction)
                    if sim_id in simulations:
                        simulations[sim_id]['transactions'].append(transaction)
            
            # Perform behavioral analysis
            analysis = {
                'user_id': user_id,
                'analysis_date': datetime.now().date(),
                'trading_patterns': self._analyze_trading_patterns(transactions),
                'emotional_indicators': self._analyze_emotional_indicators(transactions, simulations),
                'risk_behavior_score': self._calculate_risk_behavior_score(transactions, simulations),
                'decision_quality_score': self._calculate_decision_quality_score(simulations),
                'learning_progress': self._analyze_learning_progress(user_id, simulations),
                'recommendations': [],
                'personality_insights': {}
            }
            
            # Generate personalized recommendations
            analysis['recommendations'] = self._generate_recommendations(analysis)
            analysis['personality_insights'] = self._generate_personality_insights(analysis)
            
            # Store analysis in database
            self._store_behavioral_analysis(user_id, analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing user behavior: {e}")
            return self._create_default_analysis(user_id)
        finally:
            cursor.close()
    
    def _analyze_trading_patterns(self, transactions: List[Dict]) -> Dict:
        """Analyze trading patterns to identify user's trading style"""
        if not transactions:
            return {'primary_pattern': 'beginner', 'confidence': 0.5}
        
        patterns = {}
        
        # Calculate trading frequency
        total_trades = len(transactions)
        if total_trades > 0:
            # Time-based analysis
            first_trade = min(transactions, key=lambda x: x['created_at'])['created_at']
            last_trade = max(transactions, key=lambda x: x['created_at'])['created_at']
            
            if isinstance(first_trade, str):
                first_trade = datetime.fromisoformat(first_trade)
            if isinstance(last_trade, str):
                last_trade = datetime.fromisoformat(last_trade)
            
            days_trading = max(1, (last_trade - first_trade).days)
            trades_per_day = total_trades / days_trading
            
            # Pattern identification
            if trades_per_day > 5:
                patterns['day_trader'] = min(1.0, trades_per_day / 10)
            elif trades_per_day > 1:
                patterns['swing_trader'] = min(1.0, trades_per_day / 3)
            else:
                patterns['long_term_investor'] = 1.0 - (trades_per_day / 2)
        
        # Analyze buy/sell ratio
        buys = [t for t in transactions if t['type'] == 'buy']
        sells = [t for t in transactions if t['type'] == 'sell']
        
        if len(buys) > 0:
            buy_sell_ratio = len(sells) / len(buys)
            if buy_sell_ratio < 0.3:
                patterns['hodler'] = 1.0 - buy_sell_ratio
            elif buy_sell_ratio > 1.5:
                patterns['panic_trader'] = min(1.0, buy_sell_ratio - 1.0)
        
        # Determine primary pattern
        if patterns:
            primary_pattern = max(patterns.items(), key=lambda x: x[1])
            return {
                'primary_pattern': primary_pattern[0],
                'confidence': primary_pattern[1],
                'all_patterns': patterns,
                'trades_per_day': trades_per_day if 'trades_per_day' in locals() else 0,
                'total_trades': total_trades
            }
        
        return {'primary_pattern': 'beginner', 'confidence': 0.5}
    
    def _analyze_emotional_indicators(self, transactions: List[Dict], simulations: Dict) -> Dict:
        """Analyze emotional trading indicators"""
        emotions = {
            'fear': 0.0,
            'greed': 0.0,
            'discipline': 0.0,
            'impulsiveness': 0.0,
            'confidence': 0.0
        }
        
        if not transactions:
            return emotions
        
        # Analyze transaction timing and amounts
        transaction_amounts = [t['total_amount'] for t in transactions]
        if transaction_amounts:
            avg_amount = np.mean(transaction_amounts)
            std_amount = np.std(transaction_amounts)
            
            # High variance in trade amounts suggests impulsiveness
            if std_amount > avg_amount:
                emotions['impulsiveness'] = min(1.0, std_amount / avg_amount - 1.0)
            
            # Very small amounts suggest fear
            small_trades = [amt for amt in transaction_amounts if amt < avg_amount * 0.5]
            if len(small_trades) / len(transaction_amounts) > 0.6:
                emotions['fear'] = 0.7
            
            # Very large amounts suggest overconfidence
            large_trades = [amt for amt in transaction_amounts if amt > avg_amount * 2]
            if len(large_trades) / len(transaction_amounts) > 0.3:
                emotions['greed'] = 0.6
        
        # Analyze performance vs behavior
        for sim_id, sim_data in simulations.items():
            return_pct = sim_data.get('return_percentage', 0)
            
            # Good returns with consistent trading suggests discipline
            if return_pct > 10 and emotions['impulsiveness'] < 0.3:
                emotions['discipline'] = 0.8
            
            # Positive returns suggest confidence
            if return_pct > 0:
                emotions['confidence'] = min(1.0, return_pct / 20)
            
            # Negative returns with high trading activity suggests panic
            if return_pct < -10 and len(sim_data.get('transactions', [])) > 10:
                emotions['fear'] = 0.9
        
        return emotions
    
    def _calculate_risk_behavior_score(self, transactions: List[Dict], simulations: Dict) -> float:
        """Calculate user's risk behavior score (0-1, higher = more risky)"""
        if not transactions:
            return 0.5
        
        risk_factors = []
        
        # Trading frequency risk
        total_trades = len(transactions)
        if total_trades > 0:
            # More than 2 trades per day is considered risky
            first_trade = min(transactions, key=lambda x: x['created_at'])['created_at']
            last_trade = max(transactions, key=lambda x: x['created_at'])['created_at']
            
            if isinstance(first_trade, str):
                first_trade = datetime.fromisoformat(first_trade)
            if isinstance(last_trade, str):
                last_trade = datetime.fromisoformat(last_trade)
            
            days_trading = max(1, (last_trade - first_trade).days)
            trades_per_day = total_trades / days_trading
            
            risk_factors.append(min(1.0, trades_per_day / 5))  # Normalize to 5 trades/day = max risk
        
        # Trade size variance (high variance = risky)
        amounts = [t['total_amount'] for t in transactions]
        if len(amounts) > 1:
            variance_factor = np.std(amounts) / np.mean(amounts)
            risk_factors.append(min(1.0, variance_factor))
        
        # Portfolio concentration risk
        symbols = list(set(t['symbol'] for t in transactions))
        if len(symbols) < 3:  # Less than 3 stocks is risky
            risk_factors.append(1.0 - (len(symbols) / 5))  # Normalize to 5 stocks = min risk
        
        # Performance-adjusted risk
        for sim_data in simulations.values():
            return_pct = sim_data.get('return_percentage', 0)
            if return_pct < -20:  # Large losses indicate risky behavior
                risk_factors.append(min(1.0, abs(return_pct) / 50))
        
        return np.mean(risk_factors) if risk_factors else 0.5
    
    def _calculate_decision_quality_score(self, simulations: Dict) -> float:
        """Calculate quality of user's investment decisions (0-1, higher = better)"""
        if not simulations:
            return 0.5
        
        quality_factors = []
        
        for sim_data in simulations.values():
            return_pct = sim_data.get('return_percentage', 0)
            
            # Positive returns contribute to good decision quality
            if return_pct > 0:
                quality_factors.append(min(1.0, return_pct / 30))  # 30% return = perfect score
            else:
                quality_factors.append(max(0.0, 0.5 + return_pct / 50))  # Penalize losses
            
            # Consistency bonus
            transactions = sim_data.get('transactions', [])
            if len(transactions) > 3:  # Need multiple trades to assess consistency
                amounts = [t['total_amount'] for t in transactions]
                consistency = 1.0 - (np.std(amounts) / np.mean(amounts)) if np.mean(amounts) > 0 else 0
                quality_factors.append(max(0.0, min(1.0, consistency)))
        
        return np.mean(quality_factors) if quality_factors else 0.5
    
    def _analyze_learning_progress(self, user_id: int, simulations: Dict) -> Dict:
        """Analyze user's learning progress and growth"""
        cursor = self.db.cursor(dictionary=True)
        
        try:
            # Get user's completed modules and achievements
            cursor.execute("""
                SELECT ua.earned_date, a.category, a.points_reward
                FROM user_achievements ua
                JOIN achievements a ON ua.achievement_id = a.id
                WHERE ua.user_id = %s
                ORDER BY ua.earned_date
            """, (user_id,))
            
            achievements = cursor.fetchall()
            
            progress = {
                'total_achievements': len(achievements),
                'learning_achievements': len([a for a in achievements if a['category'] == 'learning']),
                'trading_achievements': len([a for a in achievements if a['category'] == 'trading']),
                'total_points': sum(a['points_reward'] for a in achievements),
                'learning_velocity': 0,
                'improvement_trend': 'stable'
            }
            
            # Calculate learning velocity (achievements per week)
            if achievements:
                first_achievement = min(achievements, key=lambda x: x['earned_date'])['earned_date']
                weeks_active = max(1, (datetime.now().date() - first_achievement).days / 7)
                progress['learning_velocity'] = len(achievements) / weeks_active
            
            # Analyze improvement trend from simulation performance
            sim_returns = [(sim['start_date'], sim['return_percentage']) 
                          for sim in simulations.values() if sim.get('return_percentage') is not None]
            
            if len(sim_returns) >= 2:
                sim_returns.sort(key=lambda x: x[0])  # Sort by start date
                early_returns = [r[1] for r in sim_returns[:len(sim_returns)//2]]
                recent_returns = [r[1] for r in sim_returns[len(sim_returns)//2:]]
                
                if np.mean(recent_returns) > np.mean(early_returns) + 5:
                    progress['improvement_trend'] = 'improving'
                elif np.mean(recent_returns) < np.mean(early_returns) - 5:
                    progress['improvement_trend'] = 'declining'
            
            return progress
            
        except Exception as e:
            logger.error(f"Error analyzing learning progress: {e}")
            return {'total_achievements': 0, 'learning_velocity': 0, 'improvement_trend': 'unknown'}
        finally:
            cursor.close()
    
    def _generate_recommendations(self, analysis: Dict) -> List[Dict]:
        """Generate personalized recommendations based on analysis"""
        recommendations = []
        
        # Risk behavior recommendations
        risk_score = analysis.get('risk_behavior_score', 0.5)
        if risk_score > 0.7:
            recommendations.append({
                'type': 'risk_management',
                'priority': 'high',
                'title': 'Consider Diversification',
                'description': 'Your trading pattern shows high risk concentration. Consider diversifying across more sectors.',
                'action': 'Learn about portfolio diversification',
                'icon': '🛡️'
            })
        
        # Trading pattern recommendations
        trading_pattern = analysis.get('trading_patterns', {}).get('primary_pattern', '')
        if trading_pattern == 'panic_trader':
            recommendations.append({
                'type': 'emotional_discipline',
                'priority': 'high',
                'title': 'Develop Trading Discipline',
                'description': 'You tend to make emotional trading decisions. Try setting stop-losses and profit targets.',
                'action': 'Complete the emotional trading module',
                'icon': '🧘'
            })
        elif trading_pattern == 'day_trader':
            recommendations.append({
                'type': 'strategy',
                'priority': 'medium',
                'title': 'Consider Long-term Investing',
                'description': 'Frequent trading can be costly. Consider some long-term investments for stability.',
                'action': 'Try the long-term simulation mode',
                'icon': '📈'
            })
        
        # Decision quality recommendations
        decision_score = analysis.get('decision_quality_score', 0.5)
        if decision_score < 0.4:
            recommendations.append({
                'type': 'education',
                'priority': 'high',
                'title': 'Improve Analysis Skills',
                'description': 'Your investment decisions could benefit from better fundamental analysis.',
                'action': 'Learn about financial statement analysis',
                'icon': '📊'
            })
        
        # Emotional indicators recommendations
        emotions = analysis.get('emotional_indicators', {})
        if emotions.get('fear', 0) > 0.6:
            recommendations.append({
                'type': 'psychological',
                'priority': 'medium',
                'title': 'Build Confidence Gradually',
                'description': 'Start with smaller positions to build confidence before increasing investment size.',
                'action': 'Practice with paper trading',
                'icon': '💪'
            })
        
        if emotions.get('greed', 0) > 0.6:
            recommendations.append({
                'type': 'psychological',
                'priority': 'medium',
                'title': 'Practice Risk Management',
                'description': 'Avoid putting too much capital in single trades. Use position sizing rules.',
                'action': 'Set maximum position size limits',
                'icon': '⚖️'
            })
        
        return recommendations[:5]  # Return top 5 recommendations
    
    def _generate_personality_insights(self, analysis: Dict) -> Dict:
        """Generate personality insights based on trading behavior"""
        insights = {}
        
        risk_score = analysis.get('risk_behavior_score', 0.5)
        decision_score = analysis.get('decision_quality_score', 0.5)
        emotions = analysis.get('emotional_indicators', {})
        
        # Risk tolerance classification
        if risk_score > 0.7:
            insights['risk_tolerance'] = 'aggressive'
            insights['risk_description'] = 'You have a high risk tolerance and prefer potentially high-reward investments.'
        elif risk_score < 0.3:
            insights['risk_tolerance'] = 'conservative'
            insights['risk_description'] = 'You prefer safer investments with lower volatility.'
        else:
            insights['risk_tolerance'] = 'moderate'
            insights['risk_description'] = 'You balance risk and reward in your investment approach.'
        
        # Trading style
        pattern = analysis.get('trading_patterns', {}).get('primary_pattern', 'beginner')
        insights['trading_style'] = pattern
        
        style_descriptions = {
            'day_trader': 'You prefer active, short-term trading strategies.',
            'swing_trader': 'You hold positions for days to weeks, capturing medium-term moves.',
            'long_term_investor': 'You focus on long-term wealth building through patient investing.',
            'panic_trader': 'You tend to make emotional decisions during market volatility.',
            'momentum_trader': 'You like to follow market trends and momentum.',
            'beginner': 'You are still developing your trading style and learning the basics.'
        }
        
        insights['style_description'] = style_descriptions.get(pattern, 'You have a unique trading approach.')
        
        # Emotional profile
        dominant_emotion = max(emotions.items(), key=lambda x: x[1])[0] if emotions else 'balanced'
        insights['emotional_profile'] = dominant_emotion
        
        emotional_descriptions = {
            'fear': 'You tend to be cautious and may miss opportunities due to overthinking.',
            'greed': 'You are optimistic but may take on too much risk when markets are good.',
            'discipline': 'You maintain good emotional control and stick to your strategies.',
            'impulsiveness': 'You sometimes make quick decisions without full analysis.',
            'confidence': 'You believe in your abilities and are willing to act on your convictions.'
        }
        
        insights['emotional_description'] = emotional_descriptions.get(dominant_emotion, 'You maintain balanced emotions in trading.')
        
        # Strengths and areas for improvement
        strengths = []
        improvements = []
        
        if decision_score > 0.6:
            strengths.append('Good investment decision making')
        else:
            improvements.append('Investment analysis skills')
        
        if emotions.get('discipline', 0) > 0.6:
            strengths.append('Trading discipline')
        else:
            improvements.append('Emotional control')
        
        if risk_score < 0.7:
            strengths.append('Risk management')
        else:
            improvements.append('Position sizing and diversification')
        
        insights['strengths'] = strengths
        insights['areas_for_improvement'] = improvements
        
        return insights
    
    def _create_default_analysis(self, user_id: int) -> Dict:
        """Create default analysis for new users"""
        return {
            'user_id': user_id,
            'analysis_date': datetime.now().date(),
            'trading_patterns': {'primary_pattern': 'beginner', 'confidence': 0.5},
            'emotional_indicators': {'confidence': 0.5, 'discipline': 0.5, 'fear': 0.3, 'greed': 0.3},
            'risk_behavior_score': 0.5,
            'decision_quality_score': 0.5,
            'learning_progress': {'total_achievements': 0, 'learning_velocity': 0},
            'recommendations': [
                {
                    'type': 'getting_started',
                    'priority': 'high',
                    'title': 'Welcome to Paisabuddy!',
                    'description': 'Start with the basics of investing and try your first simulation.',
                    'action': 'Complete the investment fundamentals course',
                    'icon': '🚀'
                }
            ],
            'personality_insights': {
                'risk_tolerance': 'moderate',
                'trading_style': 'beginner',
                'emotional_profile': 'learning'
            }
        }
    
    def _store_behavioral_analysis(self, user_id: int, analysis: Dict):
        """Store behavioral analysis in database"""
        cursor = self.db.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO ai_behavioral_analysis 
                (user_id, analysis_date, trading_patterns, emotional_indicators, 
                 risk_behavior_score, decision_quality_score, learning_progress, 
                 recommendations, personality_insights)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                trading_patterns = VALUES(trading_patterns),
                emotional_indicators = VALUES(emotional_indicators),
                risk_behavior_score = VALUES(risk_behavior_score),
                decision_quality_score = VALUES(decision_quality_score),
                learning_progress = VALUES(learning_progress),
                recommendations = VALUES(recommendations),
                personality_insights = VALUES(personality_insights)
            """, (
                user_id, analysis['analysis_date'], 
                json.dumps(analysis['trading_patterns']),
                json.dumps(analysis['emotional_indicators']),
                analysis['risk_behavior_score'],
                analysis['decision_quality_score'],
                json.dumps(analysis['learning_progress']),
                json.dumps(analysis['recommendations']),
                json.dumps(analysis['personality_insights'])
            ))
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error storing behavioral analysis: {e}")
        finally:
            cursor.close()
    
    def get_personalized_stock_suggestions(self, user_id: int, simulation_id: int = None) -> List[Dict]:
        """Generate personalized stock suggestions based on user profile"""
        cursor = self.db.cursor(dictionary=True)
        
        try:
            # Get latest behavioral analysis
            cursor.execute("""
                SELECT * FROM ai_behavioral_analysis 
                WHERE user_id = %s ORDER BY analysis_date DESC LIMIT 1
            """, (user_id,))
            
            analysis = cursor.fetchone()
            if not analysis:
                return self._get_beginner_suggestions()
            
            # Parse analysis data
            risk_score = float(analysis['risk_behavior_score'])
            personality = json.loads(analysis['personality_insights'])
            
            # Get available stocks based on risk tolerance
            if risk_score > 0.7:  # Aggressive
                sectors = ['technology', 'pharmaceuticals', 'renewable_energy']
                volatility_preference = 'high'
            elif risk_score < 0.3:  # Conservative
                sectors = ['utilities', 'consumer_staples', 'banking']
                volatility_preference = 'low'
            else:  # Moderate
                sectors = ['healthcare', 'consumer_goods', 'finance']
                volatility_preference = 'medium'
            
            # Get stock suggestions from historical data
            cursor.execute("""
                SELECT DISTINCT symbol, sector, close_price
                FROM historical_market_data 
                WHERE sector IN ('{}') AND year = 2024
                ORDER BY RAND() LIMIT 10
            """.format("','".join(sectors)))
            
            stocks = cursor.fetchall()
            
            suggestions = []
            for stock in stocks:
                suggestion = {
                    'symbol': stock['symbol'],
                    'sector': stock['sector'],
                    'current_price': float(stock['close_price']),
                    'reason': self._generate_suggestion_reason(stock, personality, risk_score),
                    'risk_level': volatility_preference,
                    'confidence': min(1.0, 0.6 + (risk_score * 0.4))
                }
                suggestions.append(suggestion)
            
            return suggestions[:5]  # Return top 5 suggestions
            
        except Exception as e:
            logger.error(f"Error generating stock suggestions: {e}")
            return self._get_beginner_suggestions()
        finally:
            cursor.close()
    
    def _generate_suggestion_reason(self, stock: Dict, personality: Dict, risk_score: float) -> str:
        """Generate explanation for why a stock is suggested"""
        reasons = []
        
        sector = stock['sector']
        risk_tolerance = personality.get('risk_tolerance', 'moderate')
        
        if risk_tolerance == 'aggressive' and sector in ['technology', 'pharmaceuticals']:
            reasons.append(f"Matches your aggressive risk tolerance with high growth potential in {sector}")
        elif risk_tolerance == 'conservative' and sector in ['utilities', 'banking']:
            reasons.append(f"Aligns with your conservative approach - {sector} stocks tend to be stable")
        else:
            reasons.append(f"Good fit for your moderate risk profile in the {sector} sector")
        
        if risk_score > 0.6:
            reasons.append("Potential for higher returns given your risk appetite")
        else:
            reasons.append("Offers balanced risk-reward for steady growth")
        
        return ". ".join(reasons)
    
    def _get_beginner_suggestions(self) -> List[Dict]:
        """Default suggestions for beginners"""
        return [
            {
                'symbol': 'TCS',
                'sector': 'technology',
                'current_price': 3500,
                'reason': 'Large, stable IT company - good for beginners',
                'risk_level': 'low',
                'confidence': 0.8
            },
            {
                'symbol': 'RELIANCE',
                'sector': 'energy',
                'current_price': 2800,
                'reason': 'Diversified business model with stable returns',
                'risk_level': 'medium',
                'confidence': 0.7
            }
        ]

# Factory function
def create_ai_engine(db_connection):
    """Create AI personalization engine instance"""
    return AIPersonalizationEngine(db_connection)
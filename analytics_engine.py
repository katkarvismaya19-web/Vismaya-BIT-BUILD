#!/usr/bin/env python3
"""
Advanced Analytics & Insights Engine for Paisabuddy
Provides comprehensive performance analysis, risk metrics, and decision insights
"""

import json
import numpy as np
import mysql.connector
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
import math

logger = logging.getLogger(__name__)

class RiskMetric(Enum):
    VOLATILITY = "volatility"
    SHARPE_RATIO = "sharpe_ratio"
    MAX_DRAWDOWN = "max_drawdown"
    VAR = "value_at_risk"
    BETA = "beta"

class PerformanceMetric(Enum):
    TOTAL_RETURN = "total_return"
    ANNUAL_RETURN = "annual_return"
    WIN_RATE = "win_rate"
    PROFIT_FACTOR = "profit_factor"
    AVERAGE_HOLDING_PERIOD = "avg_holding_period"

@dataclass
class AnalyticsInsight:
    metric_name: str
    current_value: float
    benchmark_value: float
    performance_rating: str  # excellent, good, average, poor
    interpretation: str
    recommendation: str

class AdvancedAnalyticsEngine:
    def __init__(self, db_connection):
        self.db = db_connection
        
    def generate_portfolio_analytics(self, user_id: int, simulation_id: int) -> Dict:
        """Generate comprehensive portfolio analytics"""
        cursor = self.db.cursor(dictionary=True)
        
        try:
            # Get simulation details
            cursor.execute("""
                SELECT * FROM trading_simulations WHERE id = %s AND user_id = %s
            """, (simulation_id, user_id))
            
            simulation = cursor.fetchone()
            if not simulation:
                return {'error': 'Simulation not found'}
            
            # Get all transactions for this simulation
            cursor.execute("""
                SELECT * FROM trading_transactions 
                WHERE simulation_id = %s 
                ORDER BY created_at ASC
            """, (simulation_id,))
            
            transactions = cursor.fetchall()
            
            # Get current holdings
            cursor.execute("""
                SELECT * FROM portfolio_holdings WHERE simulation_id = %s
            """, (simulation_id,))
            
            holdings = cursor.fetchall()
            
            # Calculate comprehensive analytics
            analytics = {
                'simulation_info': simulation,
                'performance_metrics': self._calculate_performance_metrics(simulation, transactions, holdings),
                'risk_metrics': self._calculate_risk_metrics(simulation, transactions, holdings),
                'sector_analysis': self._analyze_sector_allocation(holdings),
                'trading_patterns': self._analyze_trading_patterns(transactions),
                'benchmarks': self._calculate_benchmark_comparison(simulation, transactions),
                'insights': [],
                'recommendations': []
            }
            
            # Generate insights and recommendations
            analytics['insights'] = self._generate_analytics_insights(analytics)
            analytics['recommendations'] = self._generate_analytics_recommendations(analytics)
            
            # Store analytics in database
            self._store_analytics(user_id, simulation_id, analytics)
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error generating portfolio analytics: {e}")
            return {'error': str(e)}
        finally:
            cursor.close()
    
    def _calculate_performance_metrics(self, simulation: Dict, transactions: List[Dict], holdings: List[Dict]) -> Dict:
        """Calculate key performance metrics"""
        metrics = {}
        
        # Basic return metrics
        initial_balance = float(simulation.get('virtual_balance', 100000))
        current_value = float(simulation.get('current_portfolio_value', initial_balance))
        
        total_return = current_value - initial_balance
        total_return_pct = (total_return / initial_balance) * 100
        
        metrics['total_return'] = round(total_return, 2)
        metrics['total_return_percentage'] = round(total_return_pct, 2)
        
        # Time-based returns
        start_date = simulation.get('start_date')
        current_date = simulation.get('current_date', datetime.now().date())
        
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date).date()
        if isinstance(current_date, str):
            current_date = datetime.fromisoformat(current_date).date()
        
        days_invested = max(1, (current_date - start_date).days)
        years_invested = days_invested / 365.25
        
        if years_invested > 0:
            annual_return = (((current_value / initial_balance) ** (1 / years_invested)) - 1) * 100
            metrics['annual_return'] = round(annual_return, 2)
        else:
            metrics['annual_return'] = 0
        
        # Trading metrics
        if transactions:
            buy_trades = [t for t in transactions if t['transaction_type'] == 'buy']
            sell_trades = [t for t in transactions if t['transaction_type'] == 'sell']
            
            metrics['total_trades'] = len(transactions)
            metrics['buy_trades'] = len(buy_trades)
            metrics['sell_trades'] = len(sell_trades)
            
            # Win rate calculation
            profitable_trades = 0
            total_completed_trades = 0
            
            # Match buy/sell pairs to calculate individual trade P&L
            for buy_trade in buy_trades:
                matching_sells = [s for s in sell_trades 
                                if s['symbol'] == buy_trade['symbol'] 
                                and s['created_at'] > buy_trade['created_at']]
                
                if matching_sells:
                    # Find the first matching sell
                    first_sell = min(matching_sells, key=lambda x: x['created_at'])
                    
                    buy_price = float(buy_trade['price'])
                    sell_price = float(first_sell['price'])
                    
                    if sell_price > buy_price:
                        profitable_trades += 1
                    total_completed_trades += 1
            
            if total_completed_trades > 0:
                metrics['win_rate'] = round((profitable_trades / total_completed_trades) * 100, 1)
            else:
                metrics['win_rate'] = 0
            
            # Average trade size
            trade_amounts = [float(t['total_amount']) for t in transactions]
            metrics['avg_trade_size'] = round(np.mean(trade_amounts), 2)
            metrics['largest_trade'] = round(max(trade_amounts), 2)
            metrics['smallest_trade'] = round(min(trade_amounts), 2)
        else:
            metrics.update({
                'total_trades': 0,
                'buy_trades': 0,
                'sell_trades': 0,
                'win_rate': 0,
                'avg_trade_size': 0,
                'largest_trade': 0,
                'smallest_trade': 0
            })
        
        # Portfolio composition
        if holdings:
            total_invested = sum(float(h['total_investment']) for h in holdings)
            metrics['total_invested'] = round(total_invested, 2)
            metrics['cash_percentage'] = round(((current_value - total_invested) / current_value) * 100, 1)
            metrics['invested_percentage'] = round((total_invested / current_value) * 100, 1)
        else:
            metrics.update({
                'total_invested': 0,
                'cash_percentage': 100,
                'invested_percentage': 0
            })
        
        return metrics
    
    def _calculate_risk_metrics(self, simulation: Dict, transactions: List[Dict], holdings: List[Dict]) -> Dict:
        """Calculate risk-related metrics"""
        risk_metrics = {}
        
        # Portfolio concentration risk
        if holdings:
            holding_values = [float(h['current_value']) for h in holdings]
            total_portfolio_value = sum(holding_values)
            
            if total_portfolio_value > 0:
                # Calculate Herfindahl-Hirschman Index for concentration
                market_shares = [value / total_portfolio_value for value in holding_values]
                hhi = sum(share ** 2 for share in market_shares)
                
                # Convert to concentration risk score (0-100, higher = more concentrated)
                concentration_risk = round(hhi * 100, 1)
                risk_metrics['concentration_risk'] = concentration_risk
                
                # Largest position percentage
                largest_position_pct = round(max(market_shares) * 100, 1)
                risk_metrics['largest_position_percentage'] = largest_position_pct
            
            # Sector diversification
            sectors = [h['sector'] for h in holdings if h.get('sector')]
            unique_sectors = len(set(sectors))
            risk_metrics['sector_count'] = unique_sectors
            
            # Diversification score (0-100, higher = better diversified)
            max_sectors = 10  # Assume max 10 sectors available
            diversification_score = min(100, (unique_sectors / max_sectors) * 100)
            risk_metrics['diversification_score'] = round(diversification_score, 1)
        else:
            risk_metrics.update({
                'concentration_risk': 0,
                'largest_position_percentage': 0,
                'sector_count': 0,
                'diversification_score': 0
            })
        
        # Volatility estimation based on transaction patterns
        if len(transactions) > 1:
            # Calculate daily trade frequency as proxy for activity level
            dates = [t['created_at'] for t in transactions]
            if len(set(dates)) > 1:
                days_with_activity = len(set(dates))
                total_days = max(1, (max(dates) - min(dates)).days if isinstance(dates[0], datetime) else 30)
                activity_ratio = days_with_activity / total_days
                
                # Higher activity generally indicates higher volatility tolerance
                volatility_proxy = round(activity_ratio * 100, 1)
                risk_metrics['activity_based_volatility'] = volatility_proxy
            else:
                risk_metrics['activity_based_volatility'] = 0
        else:
            risk_metrics['activity_based_volatility'] = 0
        
        # Maximum drawdown simulation (simplified)
        current_value = float(simulation.get('current_portfolio_value', 100000))
        initial_value = float(simulation.get('virtual_balance', 100000))
        
        # Estimate max drawdown based on current performance and risk factors
        if current_value < initial_value:
            current_drawdown = ((initial_value - current_value) / initial_value) * 100
            risk_metrics['current_drawdown'] = round(current_drawdown, 2)
        else:
            risk_metrics['current_drawdown'] = 0
        
        # Risk score (0-100, higher = riskier)
        concentration_penalty = min(50, risk_metrics.get('concentration_risk', 0) * 0.5)
        diversification_bonus = max(0, 30 - risk_metrics.get('diversification_score', 0) * 0.3)
        activity_penalty = min(20, risk_metrics.get('activity_based_volatility', 0) * 0.2)
        
        overall_risk_score = concentration_penalty + diversification_bonus + activity_penalty
        risk_metrics['overall_risk_score'] = round(min(100, max(0, overall_risk_score)), 1)
        
        return risk_metrics
    
    def _analyze_sector_allocation(self, holdings: List[Dict]) -> Dict:
        """Analyze sector allocation and diversification"""
        if not holdings:
            return {'sectors': {}, 'diversification_analysis': {}}
        
        sector_analysis = {}
        sector_values = {}
        
        total_value = sum(float(h['current_value']) for h in holdings)
        
        # Calculate sector weights
        for holding in holdings:
            sector = holding.get('sector', 'Unknown')
            value = float(holding['current_value'])
            
            if sector in sector_values:
                sector_values[sector] += value
            else:
                sector_values[sector] = value
        
        # Convert to percentages and create analysis
        sectors = {}
        for sector, value in sector_values.items():
            percentage = (value / total_value) * 100
            sectors[sector] = {
                'value': round(value, 2),
                'percentage': round(percentage, 1),
                'holdings_count': len([h for h in holdings if h.get('sector') == sector])
            }
        
        # Sort sectors by allocation
        sorted_sectors = dict(sorted(sectors.items(), key=lambda x: x[1]['percentage'], reverse=True))
        
        # Diversification analysis
        diversification = {
            'total_sectors': len(sectors),
            'largest_sector': max(sectors.keys(), key=lambda x: sectors[x]['percentage']) if sectors else None,
            'largest_allocation': max(sectors.values(), key=lambda x: x['percentage'])['percentage'] if sectors else 0,
            'is_well_diversified': len(sectors) >= 5 and max(sectors.values(), key=lambda x: x['percentage'])['percentage'] < 30
        }
        
        return {
            'sectors': sorted_sectors,
            'diversification_analysis': diversification
        }
    
    def _analyze_trading_patterns(self, transactions: List[Dict]) -> Dict:
        """Analyze user's trading patterns and behavior"""
        if not transactions:
            return {'pattern_type': 'inactive', 'analysis': {}}
        
        patterns = {}
        
        # Time-based analysis
        dates = [t['created_at'] for t in transactions]
        if len(set(dates)) > 1:
            date_range = max(dates) - min(dates)
            trading_days = date_range.days if hasattr(date_range, 'days') else 30
            
            patterns['trading_frequency'] = round(len(transactions) / max(1, trading_days), 2)
            patterns['active_trading_days'] = len(set(dates))
        
        # Trade size analysis
        amounts = [float(t['total_amount']) for t in transactions]
        patterns['avg_trade_size'] = round(np.mean(amounts), 2)
        patterns['trade_size_std'] = round(np.std(amounts), 2)
        patterns['trade_size_consistency'] = 'high' if patterns['trade_size_std'] < patterns['avg_trade_size'] * 0.5 else 'low'
        
        # Buy/sell ratio
        buy_trades = [t for t in transactions if t['transaction_type'] == 'buy']
        sell_trades = [t for t in transactions if t['transaction_type'] == 'sell']
        
        if buy_trades:
            buy_sell_ratio = len(sell_trades) / len(buy_trades)
            patterns['buy_sell_ratio'] = round(buy_sell_ratio, 2)
            
            if buy_sell_ratio < 0.5:
                patterns['trading_style'] = 'accumulator'
            elif buy_sell_ratio > 1.5:
                patterns['trading_style'] = 'active_trader'
            else:
                patterns['trading_style'] = 'balanced'
        
        # Stock picking diversity
        symbols = [t['symbol'] for t in transactions]
        unique_symbols = len(set(symbols))
        patterns['stock_diversity'] = unique_symbols
        patterns['repeat_trades'] = len(symbols) - unique_symbols
        
        # Pattern classification
        frequency = patterns.get('trading_frequency', 0)
        if frequency > 2:
            patterns['pattern_type'] = 'day_trader'
        elif frequency > 0.5:
            patterns['pattern_type'] = 'active_trader'
        elif frequency > 0.1:
            patterns['pattern_type'] = 'regular_investor'
        else:
            patterns['pattern_type'] = 'long_term_investor'
        
        return patterns
    
    def _calculate_benchmark_comparison(self, simulation: Dict, transactions: List[Dict]) -> Dict:
        """Compare performance against market benchmarks"""
        cursor = self.db.cursor(dictionary=True)
        
        try:
            # Get benchmark performance (using broad market as proxy)
            start_year = simulation.get('start_year', 2024)
            current_year = simulation.get('current_year', 2024)
            
            # Calculate market benchmark return
            cursor.execute("""
                SELECT AVG(
                    ((end_price.close_price - start_price.close_price) / start_price.close_price) * 100
                ) as market_return
                FROM historical_market_data start_price
                JOIN historical_market_data end_price ON start_price.symbol = end_price.symbol
                WHERE start_price.year = %s AND end_price.year = %s
                AND start_price.symbol IN ('TCS', 'RELIANCE', 'HDFCBANK', 'INFY', 'ITC')
            """, (start_year, current_year))
            
            benchmark_result = cursor.fetchone()
            market_return = float(benchmark_result['market_return'] or 0)
            
            # User's portfolio return
            portfolio_return = float(simulation.get('return_percentage', 0))
            
            # Calculate alpha (excess return over benchmark)
            alpha = portfolio_return - market_return
            
            # Determine performance category
            if alpha > 10:
                performance_category = 'exceptional'
            elif alpha > 5:
                performance_category = 'excellent'
            elif alpha > 0:
                performance_category = 'outperforming'
            elif alpha > -5:
                performance_category = 'underperforming'
            else:
                performance_category = 'significantly_underperforming'
            
            return {
                'portfolio_return': round(portfolio_return, 2),
                'market_benchmark': round(market_return, 2),
                'alpha': round(alpha, 2),
                'performance_category': performance_category,
                'outperformed_market': alpha > 0
            }
            
        except Exception as e:
            logger.error(f"Error calculating benchmark comparison: {e}")
            return {
                'portfolio_return': float(simulation.get('return_percentage', 0)),
                'market_benchmark': 0,
                'alpha': 0,
                'performance_category': 'unknown',
                'outperformed_market': False
            }
        finally:
            cursor.close()
    
    def _generate_analytics_insights(self, analytics: Dict) -> List[AnalyticsInsight]:
        """Generate actionable insights from analytics data"""
        insights = []
        
        performance = analytics.get('performance_metrics', {})
        risk = analytics.get('risk_metrics', {})
        benchmarks = analytics.get('benchmarks', {})
        
        # Performance insights
        total_return = performance.get('total_return_percentage', 0)
        if total_return > 20:
            insights.append(AnalyticsInsight(
                metric_name="Total Return",
                current_value=total_return,
                benchmark_value=10,  # Assumed benchmark
                performance_rating="excellent",
                interpretation="Your portfolio has generated exceptional returns",
                recommendation="Consider taking some profits and diversifying further"
            ))
        elif total_return < -10:
            insights.append(AnalyticsInsight(
                metric_name="Total Return",
                current_value=total_return,
                benchmark_value=10,
                performance_rating="poor",
                interpretation="Your portfolio is experiencing significant losses",
                recommendation="Review your investment strategy and consider risk management"
            ))
        
        # Risk insights
        concentration_risk = risk.get('concentration_risk', 0)
        if concentration_risk > 50:
            insights.append(AnalyticsInsight(
                metric_name="Concentration Risk",
                current_value=concentration_risk,
                benchmark_value=25,
                performance_rating="poor",
                interpretation="Your portfolio is highly concentrated in few positions",
                recommendation="Diversify across more stocks and sectors to reduce risk"
            ))
        
        # Diversification insights
        sector_count = risk.get('sector_count', 0)
        if sector_count < 3:
            insights.append(AnalyticsInsight(
                metric_name="Sector Diversification",
                current_value=sector_count,
                benchmark_value=5,
                performance_rating="poor",
                interpretation="Your portfolio lacks sector diversification",
                recommendation="Consider investing in different sectors to spread risk"
            ))
        
        # Benchmark comparison insights
        alpha = benchmarks.get('alpha', 0)
        if alpha > 5:
            insights.append(AnalyticsInsight(
                metric_name="Market Outperformance",
                current_value=alpha,
                benchmark_value=0,
                performance_rating="excellent",
                interpretation="You are significantly outperforming the market",
                recommendation="Document your successful strategies for future reference"
            ))
        
        return insights
    
    def _generate_analytics_recommendations(self, analytics: Dict) -> List[Dict]:
        """Generate specific recommendations based on analytics"""
        recommendations = []
        
        performance = analytics.get('performance_metrics', {})
        risk = analytics.get('risk_metrics', {})
        sectors = analytics.get('sector_analysis', {})
        patterns = analytics.get('trading_patterns', {})
        
        # Performance-based recommendations
        win_rate = performance.get('win_rate', 0)
        if win_rate < 40:
            recommendations.append({
                'category': 'Strategy',
                'priority': 'high',
                'title': 'Improve Trade Selection',
                'description': f'Your win rate is {win_rate}%. Focus on better entry points and stock analysis.',
                'action': 'Study fundamental analysis and technical indicators',
                'icon': '🎯'
            })
        
        # Risk-based recommendations
        concentration_risk = risk.get('concentration_risk', 0)
        if concentration_risk > 40:
            recommendations.append({
                'category': 'Risk Management',
                'priority': 'high',
                'title': 'Reduce Concentration Risk',
                'description': 'Your portfolio is too concentrated. Spread investments across more positions.',
                'action': 'Limit individual positions to 10-15% of portfolio',
                'icon': '⚖️'
            })
        
        # Diversification recommendations
        sector_analysis = sectors.get('diversification_analysis', {})
        if not sector_analysis.get('is_well_diversified', False):
            recommendations.append({
                'category': 'Diversification',
                'priority': 'medium',
                'title': 'Improve Sector Allocation',
                'description': 'Add exposure to different sectors for better diversification.',
                'action': 'Research and invest in underrepresented sectors',
                'icon': '🌐'
            })
        
        # Trading pattern recommendations
        pattern_type = patterns.get('pattern_type', 'unknown')
        if pattern_type == 'day_trader':
            recommendations.append({
                'category': 'Trading Style',
                'priority': 'medium',
                'title': 'Consider Long-term Investing',
                'description': 'Frequent trading can be costly. Consider some long-term positions.',
                'action': 'Allocate a portion of portfolio to buy-and-hold investments',
                'icon': '📈'
            })
        
        return recommendations[:5]  # Return top 5 recommendations
    
    def _store_analytics(self, user_id: int, simulation_id: int, analytics: Dict):
        """Store analytics results in database"""
        cursor = self.db.cursor()
        
        try:
            performance = analytics.get('performance_metrics', {})
            risk = analytics.get('risk_metrics', {})
            benchmarks = analytics.get('benchmarks', {})
            sectors = analytics.get('sector_analysis', {})
            
            cursor.execute("""
                INSERT INTO performance_analytics 
                (user_id, simulation_id, analysis_date, total_return, annual_return, 
                 volatility, max_drawdown, win_rate, sector_allocation, risk_metrics, benchmark_comparison)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                total_return = VALUES(total_return),
                annual_return = VALUES(annual_return),
                volatility = VALUES(volatility),
                max_drawdown = VALUES(max_drawdown),
                win_rate = VALUES(win_rate),
                sector_allocation = VALUES(sector_allocation),
                risk_metrics = VALUES(risk_metrics),
                benchmark_comparison = VALUES(benchmark_comparison)
            """, (
                user_id, simulation_id, datetime.now().date(),
                performance.get('total_return_percentage', 0),
                performance.get('annual_return', 0),
                risk.get('activity_based_volatility', 0),
                risk.get('current_drawdown', 0),
                performance.get('win_rate', 0),
                json.dumps(sectors),
                json.dumps(risk),
                json.dumps(benchmarks)
            ))
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error storing analytics: {e}")
        finally:
            cursor.close()
    
    def get_user_analytics_summary(self, user_id: int) -> Dict:
        """Get comprehensive analytics summary for user dashboard"""
        cursor = self.db.cursor(dictionary=True)
        
        try:
            # Get latest analytics for all user's simulations
            cursor.execute("""
                SELECT pa.*, ts.simulation_name, ts.simulation_type
                FROM performance_analytics pa
                JOIN trading_simulations ts ON pa.simulation_id = ts.id
                WHERE pa.user_id = %s
                ORDER BY pa.analysis_date DESC
                LIMIT 10
            """, (user_id,))
            
            recent_analytics = cursor.fetchall()
            
            if not recent_analytics:
                return self._get_default_analytics_summary(user_id)
            
            # Aggregate metrics
            avg_return = np.mean([float(a['total_return']) for a in recent_analytics])
            avg_win_rate = np.mean([float(a['win_rate']) for a in recent_analytics])
            avg_volatility = np.mean([float(a['volatility']) for a in recent_analytics])
            
            # Performance trend analysis
            sorted_analytics = sorted(recent_analytics, key=lambda x: x['analysis_date'])
            if len(sorted_analytics) >= 2:
                early_returns = [float(a['total_return']) for a in sorted_analytics[:len(sorted_analytics)//2]]
                recent_returns = [float(a['total_return']) for a in sorted_analytics[len(sorted_analytics)//2:]]
                
                trend = 'improving' if np.mean(recent_returns) > np.mean(early_returns) else 'declining'
            else:
                trend = 'stable'
            
            return {
                'overall_metrics': {
                    'avg_return': round(avg_return, 2),
                    'avg_win_rate': round(avg_win_rate, 1),
                    'avg_volatility': round(avg_volatility, 1),
                    'performance_trend': trend,
                    'total_simulations': len(recent_analytics)
                },
                'recent_analytics': recent_analytics[:5],  # Last 5
                'performance_distribution': {
                    'profitable_simulations': len([a for a in recent_analytics if float(a['total_return']) > 0]),
                    'loss_making_simulations': len([a for a in recent_analytics if float(a['total_return']) < 0]),
                    'break_even_simulations': len([a for a in recent_analytics if float(a['total_return']) == 0])
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting analytics summary: {e}")
            return self._get_default_analytics_summary(user_id)
        finally:
            cursor.close()
    
    def _get_default_analytics_summary(self, user_id: int) -> Dict:
        """Default analytics summary for new users"""
        return {
            'overall_metrics': {
                'avg_return': 0,
                'avg_win_rate': 0,
                'avg_volatility': 0,
                'performance_trend': 'new_user',
                'total_simulations': 0
            },
            'recent_analytics': [],
            'performance_distribution': {
                'profitable_simulations': 0,
                'loss_making_simulations': 0,
                'break_even_simulations': 0
            }
        }
    
    def generate_decision_analysis(self, user_id: int, simulation_id: int) -> Dict:
        """Analyze individual trading decisions and their outcomes"""
        cursor = self.db.cursor(dictionary=True)
        
        try:
            # Get all transactions for analysis
            cursor.execute("""
                SELECT tt.*, ts.simulation_type, hmd.close_price as market_price
                FROM trading_transactions tt
                JOIN trading_simulations ts ON tt.simulation_id = ts.id
                LEFT JOIN historical_market_data hmd ON tt.symbol = hmd.symbol 
                    AND hmd.year = tt.simulation_year
                WHERE tt.simulation_id = %s AND ts.user_id = %s
                ORDER BY tt.created_at ASC
            """, (simulation_id, user_id))
            
            transactions = cursor.fetchall()
            
            if not transactions:
                return {'message': 'No transactions to analyze'}
            
            decision_analysis = {
                'good_decisions': [],
                'poor_decisions': [],
                'decision_quality_score': 0,
                'learning_opportunities': []
            }
            
            # Analyze buy/sell pairs
            buys = {t['symbol']: [] for t in transactions if t['transaction_type'] == 'buy'}
            
            for transaction in transactions:
                if transaction['transaction_type'] == 'buy':
                    buys[transaction['symbol']].append(transaction)
            
            total_decisions = 0
            good_decisions = 0
            
            for symbol, buy_transactions in buys.items():
                sells = [t for t in transactions if t['transaction_type'] == 'sell' and t['symbol'] == symbol]
                
                for buy in buy_transactions:
                    buy_price = float(buy['price'])
                    buy_date = buy['created_at']
                    
                    # Find corresponding sell or current price
                    corresponding_sell = None
                    for sell in sells:
                        if sell['created_at'] > buy_date:
                            corresponding_sell = sell
                            break
                    
                    if corresponding_sell:
                        sell_price = float(corresponding_sell['price'])
                        profit_loss = ((sell_price - buy_price) / buy_price) * 100
                        
                        decision_data = {
                            'symbol': symbol,
                            'buy_price': buy_price,
                            'sell_price': sell_price,
                            'profit_loss_pct': round(profit_loss, 2),
                            'holding_period': (corresponding_sell['created_at'] - buy_date).days,
                            'decision_quality': 'good' if profit_loss > 0 else 'poor'
                        }
                        
                        if profit_loss > 0:
                            decision_analysis['good_decisions'].append(decision_data)
                            good_decisions += 1
                        else:
                            decision_analysis['poor_decisions'].append(decision_data)
                        
                        total_decisions += 1
            
            # Calculate decision quality score
            if total_decisions > 0:
                decision_analysis['decision_quality_score'] = round((good_decisions / total_decisions) * 100, 1)
            
            # Generate learning opportunities
            if decision_analysis['poor_decisions']:
                avg_loss = np.mean([d['profit_loss_pct'] for d in decision_analysis['poor_decisions']])
                decision_analysis['learning_opportunities'].append(
                    f"Average loss per poor decision: {avg_loss:.1f}%. Consider better exit strategies."
                )
            
            if decision_analysis['good_decisions']:
                avg_gain = np.mean([d['profit_loss_pct'] for d in decision_analysis['good_decisions']])
                decision_analysis['learning_opportunities'].append(
                    f"Average gain per good decision: {avg_gain:.1f}%. Try to replicate these strategies."
                )
            
            return decision_analysis
            
        except Exception as e:
            logger.error(f"Error generating decision analysis: {e}")
            return {'error': str(e)}
        finally:
            cursor.close()

# Factory function
def create_analytics_engine(db_connection):
    """Create analytics engine instance"""
    return AdvancedAnalyticsEngine(db_connection)
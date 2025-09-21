#!/usr/bin/env python3
"""
Enhanced Trading Simulator for Paisabuddy
Supports both intraday and long-term trading with historical data simulation
"""

import mysql.connector
import json
import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Any, Tuple
import threading
import time
import random
import logging

logger = logging.getLogger(__name__)

class TradingSimulator:
    def __init__(self, db_connection):
        self.db = db_connection
        self.active_simulations = {}  # Track running simulations
        self.simulation_threads = {}  # Track timer threads for long-term simulations
        
    def create_simulation(self, user_id: int, simulation_type: str, simulation_name: str, 
                         start_year: int = None, settings: Dict = None) -> Optional[int]:
        """Create a new trading simulation"""
        cursor = self.db.cursor()
        
        try:
            # Default settings
            default_settings = {
                'initial_balance': 100000,
                'time_acceleration': 15 if simulation_type == 'longterm' else 0,  # minutes per year
                'enable_events': True,
                'auto_rebalance': False,
                'risk_warnings': True
            }
            
            if settings:
                default_settings.update(settings)
            
            # Set start year and date
            if simulation_type == 'longterm':
                start_year = start_year or 2004
                start_date = f"{start_year}-01-01"
                current_date = start_date
                current_year = start_year
            else:
                start_date = datetime.date.today().isoformat()
                current_date = start_date
                start_year = datetime.date.today().year
                current_year = start_year
            
            cursor.execute("""
                INSERT INTO trading_simulations 
                (user_id, simulation_type, simulation_name, start_date, current_date, 
                 start_year, current_year, virtual_balance, current_portfolio_value, settings)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                user_id, simulation_type, simulation_name, start_date, current_date,
                start_year, current_year, default_settings['initial_balance'],
                default_settings['initial_balance'], json.dumps(default_settings)
            ))
            
            simulation_id = cursor.lastrowid
            
            # Start time acceleration thread for long-term simulations
            if simulation_type == 'longterm':
                self.start_time_acceleration(simulation_id)
            
            logger.info(f"Created {simulation_type} simulation {simulation_id} for user {user_id}")
            return simulation_id
            
        except Exception as e:
            logger.error(f"Error creating simulation: {e}")
            return None
        finally:
            cursor.close()
    
    def start_time_acceleration(self, simulation_id: int):
        """Start time acceleration thread for long-term simulation"""
        def time_accelerator():
            while True:
                try:
                    # Check if simulation is still active
                    cursor = self.db.cursor()
                    cursor.execute("""
                        SELECT status, current_year, settings FROM trading_simulations 
                        WHERE id = %s
                    """, (simulation_id,))
                    
                    result = cursor.fetchone()
                    cursor.close()
                    
                    if not result or result[0] != 'active':
                        break
                    
                    current_year = result[1]
                    settings = json.loads(result[2]) if result[2] else {}
                    acceleration_minutes = settings.get('time_acceleration', 15)
                    
                    # Stop if we've reached current year
                    if current_year >= 2024:
                        self.pause_simulation(simulation_id)
                        break
                    
                    # Wait for acceleration period (15 minutes default)
                    time.sleep(acceleration_minutes * 60)  # Convert to seconds
                    
                    # Advance to next year
                    self.advance_simulation_year(simulation_id)
                    
                except Exception as e:
                    logger.error(f"Error in time acceleration for simulation {simulation_id}: {e}")
                    break
        
        # Start the thread
        thread = threading.Thread(target=time_accelerator, daemon=True)
        thread.start()
        self.simulation_threads[simulation_id] = thread
    
    def advance_simulation_year(self, simulation_id: int):
        """Advance simulation by one year and trigger events"""
        cursor = self.db.cursor()
        
        try:
            # Get current simulation state
            cursor.execute("""
                SELECT current_year, user_id, settings FROM trading_simulations 
                WHERE id = %s AND status = 'active'
            """, (simulation_id,))
            
            result = cursor.fetchone()
            if not result:
                return False
            
            current_year, user_id, settings_json = result
            new_year = current_year + 1
            new_date = f"{new_year}-01-01"
            
            # Update simulation year
            cursor.execute("""
                UPDATE trading_simulations 
                SET current_year = %s, current_date = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (new_year, new_date, simulation_id))
            
            # Update portfolio values based on historical data
            self.update_portfolio_values(simulation_id, new_year)
            
            # Check for market events in this year
            market_events = self.get_market_events(new_year)
            
            # Apply market events to portfolio
            for event in market_events:
                self.apply_market_event(simulation_id, event)
                
                # Notify user of significant events
                if event['impact_level'] in ['high', 'extreme']:
                    self.create_event_notification(simulation_id, user_id, event)
            
            # Calculate and update performance metrics
            self.update_performance_analytics(simulation_id, new_year)
            
            # Check for achievements
            self.check_achievements(user_id, simulation_id)
            
            logger.info(f"Advanced simulation {simulation_id} to year {new_year}")
            return True
            
        except Exception as e:
            logger.error(f"Error advancing simulation year: {e}")
            return False
        finally:
            cursor.close()
    
    def update_portfolio_values(self, simulation_id: int, year: int):
        """Update portfolio values based on historical market data"""
        cursor = self.db.cursor()
        
        try:
            # Get all holdings for this simulation
            cursor.execute("""
                SELECT id, symbol, quantity, average_buy_price, current_price
                FROM portfolio_holdings WHERE simulation_id = %s
            """, (simulation_id,))
            
            holdings = cursor.fetchall()
            total_portfolio_value = 0
            
            for holding_id, symbol, quantity, avg_buy_price, old_price in holdings:
                # Get new price from historical data
                cursor.execute("""
                    SELECT close_price FROM historical_market_data 
                    WHERE symbol = %s AND year = %s
                    ORDER BY date DESC LIMIT 1
                """, (symbol, year))
                
                price_result = cursor.fetchone()
                if price_result:
                    new_price = float(price_result[0])
                    
                    # Update holding values
                    current_value = quantity * new_price
                    unrealized_pnl = current_value - (quantity * float(avg_buy_price))
                    
                    cursor.execute("""
                        UPDATE portfolio_holdings 
                        SET current_price = %s, current_value = %s, unrealized_pnl = %s,
                            last_updated = CURRENT_TIMESTAMP
                        WHERE id = %s
                    """, (new_price, current_value, unrealized_pnl, holding_id))
                    
                    total_portfolio_value += current_value
            
            # Get current cash balance
            cursor.execute("""
                SELECT virtual_balance FROM trading_simulations WHERE id = %s
            """, (simulation_id,))
            
            balance_result = cursor.fetchone()
            if balance_result:
                cash_balance = float(balance_result[0])
                total_value = total_portfolio_value + cash_balance
                
                # Calculate returns
                cursor.execute("""
                    SELECT settings FROM trading_simulations WHERE id = %s
                """, (simulation_id,))
                
                settings_result = cursor.fetchone()
                settings = json.loads(settings_result[0]) if settings_result[0] else {}
                initial_balance = settings.get('initial_balance', 100000)
                
                total_returns = total_value - initial_balance
                return_percentage = (total_returns / initial_balance) * 100
                
                # Update simulation totals
                cursor.execute("""
                    UPDATE trading_simulations 
                    SET current_portfolio_value = %s, total_returns = %s, 
                        return_percentage = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (total_value, total_returns, return_percentage, simulation_id))
        
        except Exception as e:
            logger.error(f"Error updating portfolio values: {e}")
        finally:
            cursor.close()
    
    def get_market_events(self, year: int) -> List[Dict]:
        """Get market events for a specific year"""
        cursor = self.db.cursor(dictionary=True)
        
        try:
            cursor.execute("""
                SELECT * FROM market_events WHERE year = %s ORDER BY event_date
            """, (year,))
            
            return cursor.fetchall()
        
        except Exception as e:
            logger.error(f"Error fetching market events: {e}")
            return []
        finally:
            cursor.close()
    
    def apply_market_event(self, simulation_id: int, event: Dict):
        """Apply market event effects to portfolio"""
        cursor = self.db.cursor()
        
        try:
            if not event.get('affected_sectors') or not event.get('market_impact_percentage'):
                return
            
            affected_sectors = json.loads(event['affected_sectors'])
            impact_percentage = float(event['market_impact_percentage'])
            
            # Get holdings in affected sectors
            cursor.execute("""
                SELECT id, symbol, sector, current_price, quantity
                FROM portfolio_holdings 
                WHERE simulation_id = %s AND sector IN ({})
            """.format(','.join(['%s'] * len(affected_sectors))), 
            [simulation_id] + affected_sectors)
            
            affected_holdings = cursor.fetchall()
            
            for holding_id, symbol, sector, current_price, quantity in affected_holdings:
                # Apply impact to stock price
                new_price = float(current_price) * (1 + impact_percentage / 100)
                current_value = quantity * new_price
                
                cursor.execute("""
                    UPDATE portfolio_holdings 
                    SET current_price = %s, current_value = %s, last_updated = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (new_price, current_value, holding_id))
        
        except Exception as e:
            logger.error(f"Error applying market event: {e}")
        finally:
            cursor.close()
    
    def create_event_notification(self, simulation_id: int, user_id: int, event: Dict):
        """Create notification for significant market events"""
        # This would integrate with a notification system
        # For now, we'll log it
        logger.info(f"Market Event for Simulation {simulation_id}: {event['title']}")
    
    def execute_trade(self, simulation_id: int, transaction_type: str, symbol: str, 
                     quantity: int, notes: str = None) -> Dict:
        """Execute a buy or sell trade"""
        cursor = self.db.cursor()
        
        try:
            # Get current simulation state
            cursor.execute("""
                SELECT current_year, virtual_balance, simulation_type FROM trading_simulations 
                WHERE id = %s AND status = 'active'
            """, (simulation_id,))
            
            result = cursor.fetchone()
            if not result:
                return {'success': False, 'message': 'Simulation not found or inactive'}
            
            current_year, balance, sim_type = result
            
            # Get current stock price
            if sim_type == 'longterm':
                cursor.execute("""
                    SELECT close_price, sector FROM historical_market_data 
                    WHERE symbol = %s AND year = %s
                    ORDER BY date DESC LIMIT 1
                """, (symbol, current_year))
            else:
                # For intraday, use more recent/real-time data simulation
                cursor.execute("""
                    SELECT close_price, sector FROM historical_market_data 
                    WHERE symbol = %s ORDER BY date DESC LIMIT 1
                """, (symbol,))
            
            price_result = cursor.fetchone()
            if not price_result:
                return {'success': False, 'message': 'Stock not found'}
            
            current_price, sector = price_result
            current_price = float(current_price)
            
            # Add some intraday volatility for intraday trading
            if sim_type == 'intraday':
                volatility = random.uniform(-0.02, 0.02)  # ±2% volatility
                current_price *= (1 + volatility)
            
            if transaction_type == 'buy':
                total_cost = current_price * quantity
                
                # Check if user has enough balance
                if total_cost > float(balance):
                    return {'success': False, 'message': 'Insufficient balance'}
                
                # Update balance
                new_balance = float(balance) - total_cost
                cursor.execute("""
                    UPDATE trading_simulations 
                    SET virtual_balance = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (new_balance, simulation_id))
                
                # Add to portfolio or update existing holding
                cursor.execute("""
                    SELECT id, quantity, average_buy_price, total_investment 
                    FROM portfolio_holdings 
                    WHERE simulation_id = %s AND symbol = %s
                """, (simulation_id, symbol))
                
                existing_holding = cursor.fetchone()
                
                if existing_holding:
                    # Update existing holding
                    holding_id, existing_qty, avg_price, total_investment = existing_holding
                    new_total_qty = existing_qty + quantity
                    new_total_investment = float(total_investment) + total_cost
                    new_avg_price = new_total_investment / new_total_qty
                    new_current_value = new_total_qty * current_price
                    new_unrealized_pnl = new_current_value - new_total_investment
                    
                    cursor.execute("""
                        UPDATE portfolio_holdings 
                        SET quantity = %s, average_buy_price = %s, current_price = %s,
                            total_investment = %s, current_value = %s, unrealized_pnl = %s,
                            last_updated = CURRENT_TIMESTAMP
                        WHERE id = %s
                    """, (new_total_qty, new_avg_price, current_price, new_total_investment,
                          new_current_value, new_unrealized_pnl, holding_id))
                else:
                    # Create new holding
                    cursor.execute("""
                        INSERT INTO portfolio_holdings 
                        (simulation_id, symbol, quantity, average_buy_price, current_price,
                         total_investment, current_value, unrealized_pnl, sector, buy_date)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (simulation_id, symbol, quantity, current_price, current_price,
                          total_cost, total_cost, 0, sector, f"{current_year}-01-01"))
            
            elif transaction_type == 'sell':
                # Check if user has enough shares
                cursor.execute("""
                    SELECT id, quantity, average_buy_price, total_investment
                    FROM portfolio_holdings 
                    WHERE simulation_id = %s AND symbol = %s
                """, (simulation_id, symbol))
                
                holding_result = cursor.fetchone()
                if not holding_result:
                    return {'success': False, 'message': 'No shares to sell'}
                
                holding_id, available_qty, avg_buy_price, total_investment = holding_result
                
                if quantity > available_qty:
                    return {'success': False, 'message': 'Not enough shares'}
                
                # Calculate sale proceeds
                sale_proceeds = current_price * quantity
                
                # Update balance
                new_balance = float(balance) + sale_proceeds
                cursor.execute("""
                    UPDATE trading_simulations 
                    SET virtual_balance = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (new_balance, simulation_id))
                
                if quantity == available_qty:
                    # Sell all shares - remove holding
                    cursor.execute("""
                        DELETE FROM portfolio_holdings WHERE id = %s
                    """, (holding_id,))
                else:
                    # Partial sell - update holding
                    new_qty = available_qty - quantity
                    sold_investment = (quantity / available_qty) * float(total_investment)
                    new_total_investment = float(total_investment) - sold_investment
                    new_current_value = new_qty * current_price
                    new_unrealized_pnl = new_current_value - new_total_investment
                    
                    cursor.execute("""
                        UPDATE portfolio_holdings 
                        SET quantity = %s, total_investment = %s, current_value = %s,
                            unrealized_pnl = %s, current_price = %s, last_updated = CURRENT_TIMESTAMP
                        WHERE id = %s
                    """, (new_qty, new_total_investment, new_current_value, 
                          new_unrealized_pnl, current_price, holding_id))
            
            # Record transaction
            cursor.execute("""
                INSERT INTO trading_transactions 
                (simulation_id, transaction_type, symbol, quantity, price, total_amount,
                 transaction_date, simulation_year, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (simulation_id, transaction_type, symbol, quantity, current_price,
                  current_price * quantity, f"{current_year}-01-01", current_year, notes))
            
            self.db.commit()
            
            return {
                'success': True, 
                'message': f'{transaction_type.title()} order executed',
                'price': current_price,
                'total_amount': current_price * quantity,
                'new_balance': new_balance if transaction_type == 'buy' else new_balance
            }
        
        except Exception as e:
            logger.error(f"Error executing trade: {e}")
            self.db.rollback()
            return {'success': False, 'message': str(e)}
        finally:
            cursor.close()
    
    def get_simulation_status(self, simulation_id: int) -> Optional[Dict]:
        """Get current simulation status and portfolio"""
        cursor = self.db.cursor(dictionary=True)
        
        try:
            # Get simulation details
            cursor.execute("""
                SELECT * FROM trading_simulations WHERE id = %s
            """, (simulation_id,))
            
            simulation = cursor.fetchone()
            if not simulation:
                return None
            
            # Get portfolio holdings
            cursor.execute("""
                SELECT * FROM portfolio_holdings WHERE simulation_id = %s
                ORDER BY current_value DESC
            """, (simulation_id,))
            
            holdings = cursor.fetchall()
            
            # Get recent transactions
            cursor.execute("""
                SELECT * FROM trading_transactions WHERE simulation_id = %s
                ORDER BY created_at DESC LIMIT 10
            """, (simulation_id,))
            
            transactions = cursor.fetchall()
            
            return {
                'simulation': simulation,
                'holdings': holdings,
                'recent_transactions': transactions
            }
        
        except Exception as e:
            logger.error(f"Error getting simulation status: {e}")
            return None
        finally:
            cursor.close()
    
    def pause_simulation(self, simulation_id: int):
        """Pause a simulation"""
        cursor = self.db.cursor()
        
        try:
            cursor.execute("""
                UPDATE trading_simulations 
                SET status = 'paused', updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (simulation_id,))
            
            # Stop time acceleration thread if exists
            if simulation_id in self.simulation_threads:
                # Thread will stop automatically when it checks status
                del self.simulation_threads[simulation_id]
        
        except Exception as e:
            logger.error(f"Error pausing simulation: {e}")
        finally:
            cursor.close()
    
    def resume_simulation(self, simulation_id: int):
        """Resume a paused simulation"""
        cursor = self.db.cursor()
        
        try:
            cursor.execute("""
                UPDATE trading_simulations 
                SET status = 'active', updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (simulation_id,))
            
            # Restart time acceleration for long-term simulations
            cursor.execute("""
                SELECT simulation_type FROM trading_simulations WHERE id = %s
            """, (simulation_id,))
            
            result = cursor.fetchone()
            if result and result[0] == 'longterm':
                self.start_time_acceleration(simulation_id)
        
        except Exception as e:
            logger.error(f"Error resuming simulation: {e}")
        finally:
            cursor.close()
    
    def update_performance_analytics(self, simulation_id: int, year: int):
        """Update performance analytics for the simulation"""
        # This would calculate various performance metrics
        # Implementation would include Sharpe ratio, volatility, max drawdown, etc.
        pass
    
    def check_achievements(self, user_id: int, simulation_id: int):
        """Check and award achievements based on trading activity"""
        # This would check for various achievement conditions
        # Implementation would analyze trading patterns and award badges
        pass

# Factory function to create simulator instance
def create_trading_simulator(db_connection):
    """Create a trading simulator instance"""
    return TradingSimulator(db_connection)
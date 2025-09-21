"""
Dynamic Portfolio Service for Unified Portfolio Management
Handles portfolio creation, updates, and synchronization with trading activity
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class PortfolioService:
    """
    Service to manage dynamic user portfolios with real-time updates
    """
    
    def __init__(self):
        # In-memory storage for demo purposes
        # In production, this would connect to a database
        self.portfolios = {}
        self.user_trades = {}
        self.portfolio_templates = self._create_portfolio_templates()
    
    def _create_portfolio_templates(self) -> List[Dict[str, Any]]:
        """Create predefined portfolio templates for users"""
        return [
            {
                "id": 1,
                "name": "Conservative Growth",
                "description": "Low-risk portfolio focused on stable growth",
                "risk_level": "low",
                "allocation": {
                    "Banking": 40,
                    "IT": 25,
                    "FMCG": 20,
                    "Healthcare": 15
                },
                "stocks": [
                    {"symbol": "HDFCBANK", "allocation": 20, "sector": "Banking"},
                    {"symbol": "SBIN", "allocation": 20, "sector": "Banking"},
                    {"symbol": "TCS", "allocation": 15, "sector": "IT"},
                    {"symbol": "INFY", "allocation": 10, "sector": "IT"},
                    {"symbol": "HINDUNILVR", "allocation": 10, "sector": "FMCG"},
                    {"symbol": "ITC", "allocation": 10, "sector": "FMCG"},
                    {"symbol": "KOTAKBANK", "allocation": 15, "sector": "Banking"}
                ]
            },
            {
                "id": 2,
                "name": "Aggressive Growth",
                "description": "High-growth portfolio with higher risk tolerance",
                "risk_level": "high",
                "allocation": {
                    "IT": 45,
                    "Energy": 25,
                    "Telecom": 15,
                    "Banking": 15
                },
                "stocks": [
                    {"symbol": "TCS", "allocation": 25, "sector": "IT"},
                    {"symbol": "INFY", "allocation": 20, "sector": "IT"},
                    {"symbol": "RELIANCE", "allocation": 25, "sector": "Energy"},
                    {"symbol": "BHARTIARTL", "allocation": 15, "sector": "Telecom"},
                    {"symbol": "ICICIBANK", "allocation": 15, "sector": "Banking"}
                ]
            },
            {
                "id": 3,
                "name": "Balanced Portfolio",
                "description": "Well-diversified portfolio balancing growth and stability",
                "risk_level": "medium",
                "allocation": {
                    "IT": 30,
                    "Banking": 25,
                    "FMCG": 15,
                    "Energy": 15,
                    "Telecom": 10,
                    "Healthcare": 5
                },
                "stocks": [
                    {"symbol": "TCS", "allocation": 15, "sector": "IT"},
                    {"symbol": "INFY", "allocation": 15, "sector": "IT"},
                    {"symbol": "HDFCBANK", "allocation": 15, "sector": "Banking"},
                    {"symbol": "ICICIBANK", "allocation": 10, "sector": "Banking"},
                    {"symbol": "HINDUNILVR", "allocation": 10, "sector": "FMCG"},
                    {"symbol": "ITC", "allocation": 5, "sector": "FMCG"},
                    {"symbol": "RELIANCE", "allocation": 15, "sector": "Energy"},
                    {"symbol": "BHARTIARTL", "allocation": 10, "sector": "Telecom"},
                    {"symbol": "KOTAKBANK", "allocation": 5, "sector": "Banking"}
                ]
            }
        ]
    
    def get_user_portfolio(self, user_id: int, portfolio_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Get user's portfolio with real-time calculations
        """
        try:
            if portfolio_id:
                # Get specific portfolio
                portfolio_key = f"{user_id}_{portfolio_id}"
            else:
                # Get default portfolio for user
                portfolio_key = f"{user_id}_default"
            
            if portfolio_key not in self.portfolios:
                # Create default portfolio for user
                self.portfolios[portfolio_key] = self._create_default_portfolio(user_id)
            
            portfolio = self.portfolios[portfolio_key]
            
            # Update with real-time data
            return self._calculate_portfolio_metrics(portfolio)
            
        except Exception as e:
            logger.error(f"Error getting portfolio for user {user_id}: {e}")
            return self._get_fallback_portfolio()
    
    def _create_default_portfolio(self, user_id: int) -> Dict[str, Any]:
        """Create a default portfolio for a new user"""
        # Start with balanced template
        template = self.portfolio_templates[2]  # Balanced Portfolio
        
        return {
            "user_id": user_id,
            "portfolio_id": 1,
            "name": "My Portfolio",
            "description": "Your personalized investment portfolio",
            "created_at": datetime.now().isoformat(),
            "initial_balance": 100000,
            "current_balance": 95000,  # Some money invested
            "holdings": [
                {
                    "symbol": "TCS",
                    "name": "Tata Consultancy Services",
                    "sector": "IT",
                    "quantity": 5,
                    "avg_price": 3450,
                    "current_price": 3500,
                    "invested_amount": 17250,
                    "current_value": 17500,
                    "profit_loss": 250,
                    "profit_loss_percent": 1.45,
                    "allocation_percent": 35.0
                },
                {
                    "symbol": "HDFCBANK",
                    "name": "HDFC Bank",
                    "sector": "Banking", 
                    "quantity": 10,
                    "avg_price": 1620,
                    "current_price": 1650,
                    "invested_amount": 16200,
                    "current_value": 16500,
                    "profit_loss": 300,
                    "profit_loss_percent": 1.85,
                    "allocation_percent": 33.0
                },
                {
                    "symbol": "RELIANCE",
                    "name": "Reliance Industries",
                    "sector": "Energy",
                    "quantity": 6,
                    "avg_price": 2750,
                    "current_price": 2800,
                    "invested_amount": 16500,
                    "current_value": 16800,
                    "profit_loss": 300,
                    "profit_loss_percent": 1.82,
                    "allocation_percent": 32.0
                }
            ],
            "trade_history": [
                {
                    "trade_id": 1,
                    "symbol": "TCS",
                    "transaction_type": "buy",
                    "quantity": 5,
                    "price": 3450,
                    "total_amount": 17250,
                    "timestamp": (datetime.now() - timedelta(days=10)).isoformat(),
                    "fees": 25
                },
                {
                    "trade_id": 2,
                    "symbol": "HDFCBANK", 
                    "transaction_type": "buy",
                    "quantity": 10,
                    "price": 1620,
                    "total_amount": 16200,
                    "timestamp": (datetime.now() - timedelta(days=8)).isoformat(),
                    "fees": 25
                },
                {
                    "trade_id": 3,
                    "symbol": "RELIANCE",
                    "transaction_type": "buy",
                    "quantity": 6,
                    "price": 2750,
                    "total_amount": 16500,
                    "timestamp": (datetime.now() - timedelta(days=5)).isoformat(),
                    "fees": 25
                }
            ]
        }
    
    def _calculate_portfolio_metrics(self, portfolio: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate real-time portfolio metrics"""
        try:
            holdings = portfolio.get("holdings", [])
            total_invested = sum(h["invested_amount"] for h in holdings)
            total_current_value = sum(h["current_value"] for h in holdings)
            total_profit_loss = total_current_value - total_invested
            total_profit_loss_percent = (total_profit_loss / total_invested * 100) if total_invested > 0 else 0
            
            # Calculate sector allocation
            sector_allocation = {}
            for holding in holdings:
                sector = holding["sector"]
                current_value = holding["current_value"]
                if sector not in sector_allocation:
                    sector_allocation[sector] = 0
                sector_allocation[sector] += current_value
            
            # Convert to percentages
            for sector in sector_allocation:
                sector_allocation[sector] = round(
                    (sector_allocation[sector] / total_current_value * 100) if total_current_value > 0 else 0, 1
                )
            
            # Performance metrics
            portfolio_metrics = {
                "total_invested": round(total_invested, 2),
                "current_value": round(total_current_value, 2),
                "total_profit_loss": round(total_profit_loss, 2),
                "total_return_percent": round(total_profit_loss_percent, 2),
                "cash_balance": portfolio.get("current_balance", 0),
                "total_portfolio_value": round(total_current_value + portfolio.get("current_balance", 0), 2),
                "sector_allocation": sector_allocation,
                "holdings_count": len(holdings),
                "day_change": round(random.uniform(-500, 800), 2),  # Simulated daily change
                "day_change_percent": round(random.uniform(-1.5, 2.3), 2)
            }
            
            # Add metrics to portfolio
            portfolio["metrics"] = portfolio_metrics
            portfolio["last_updated"] = datetime.now().isoformat()
            
            return portfolio
            
        except Exception as e:
            logger.error(f"Error calculating portfolio metrics: {e}")
            return portfolio
    
    def update_portfolio_with_trade(
        self, 
        user_id: int, 
        trade_data: Dict[str, Any], 
        portfolio_id: Optional[int] = None
    ) -> bool:
        """
        Update portfolio when a trade is executed
        """
        try:
            portfolio_key = f"{user_id}_{portfolio_id or 'default'}"
            
            if portfolio_key not in self.portfolios:
                self.portfolios[portfolio_key] = self._create_default_portfolio(user_id)
            
            portfolio = self.portfolios[portfolio_key]
            
            symbol = trade_data["symbol"]
            transaction_type = trade_data["transaction_type"]
            quantity = trade_data["quantity"]
            price = trade_data["execution_price"]
            total_amount = quantity * price
            fees = trade_data.get("fees", 0)
            
            # Update cash balance
            if transaction_type == "buy":
                portfolio["current_balance"] -= (total_amount + fees)
            else:
                portfolio["current_balance"] += (total_amount - fees)
            
            # Update holdings
            holding_found = False
            for holding in portfolio["holdings"]:
                if holding["symbol"] == symbol:
                    if transaction_type == "buy":
                        # Add to existing holding
                        total_quantity = holding["quantity"] + quantity
                        total_invested = holding["invested_amount"] + total_amount
                        holding["avg_price"] = total_invested / total_quantity
                        holding["quantity"] = total_quantity
                        holding["invested_amount"] = total_invested
                    else:  # sell
                        # Reduce holding
                        holding["quantity"] -= quantity
                        holding["invested_amount"] -= (holding["avg_price"] * quantity)
                        if holding["quantity"] <= 0:
                            portfolio["holdings"].remove(holding)
                    
                    holding_found = True
                    break
            
            if not holding_found and transaction_type == "buy":
                # Add new holding with proper stock data
                stock_info = self._get_stock_info(symbol)
                portfolio["holdings"].append({
                    "symbol": symbol,
                    "name": stock_info.get("name", f"{symbol} Company"),
                    "sector": stock_info.get("sector", "Unknown"),
                    "quantity": quantity,
                    "avg_price": price,
                    "current_price": price,
                    "invested_amount": total_amount,
                    "current_value": total_amount,
                    "profit_loss": 0,
                    "profit_loss_percent": 0,
                    "allocation_percent": 0
                })
            
            # Add to trade history
            trade_record = {
                "trade_id": len(portfolio.get("trade_history", [])) + 1,
                "symbol": symbol,
                "transaction_type": transaction_type,
                "quantity": quantity,
                "price": price,
                "total_amount": total_amount,
                "fees": fees,
                "timestamp": datetime.now().isoformat()
            }
            
            if "trade_history" not in portfolio:
                portfolio["trade_history"] = []
            portfolio["trade_history"].append(trade_record)
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating portfolio with trade: {e}")
            return False
    
    def get_portfolio_templates(self) -> List[Dict[str, Any]]:
        """Get available portfolio templates"""
        return self.portfolio_templates
    
    def create_portfolio_from_template(
        self, 
        user_id: int, 
        template_id: int, 
        initial_balance: float = 100000
    ) -> Optional[int]:
        """
        Create a new portfolio from a template
        """
        try:
            template = next((t for t in self.portfolio_templates if t["id"] == template_id), None)
            if not template:
                return None
            
            portfolio_id = random.randint(1000, 9999)
            portfolio_key = f"{user_id}_{portfolio_id}"
            
            # Create portfolio based on template
            portfolio = {
                "user_id": user_id,
                "portfolio_id": portfolio_id,
                "name": template["name"],
                "description": template["description"],
                "risk_level": template["risk_level"],
                "created_at": datetime.now().isoformat(),
                "initial_balance": initial_balance,
                "current_balance": initial_balance,
                "holdings": [],
                "trade_history": []
            }
            
            self.portfolios[portfolio_key] = portfolio
            return portfolio_id
            
        except Exception as e:
            logger.error(f"Error creating portfolio from template: {e}")
            return None
    
    def _get_stock_info(self, symbol: str) -> Dict[str, Any]:
        """Get stock information from mock stocks data"""
        mock_stocks = {
            "TCS": {"name": "Tata Consultancy Services", "sector": "IT"},
            "RELIANCE": {"name": "Reliance Industries", "sector": "Energy"},
            "HDFCBANK": {"name": "HDFC Bank", "sector": "Banking"},
            "INFY": {"name": "Infosys Limited", "sector": "IT"},
            "ICICIBANK": {"name": "ICICI Bank", "sector": "Banking"},
            "HINDUNILVR": {"name": "Hindustan Unilever", "sector": "FMCG"},
            "ITC": {"name": "ITC Limited", "sector": "FMCG"},
            "SBIN": {"name": "State Bank of India", "sector": "Banking"},
            "BHARTIARTL": {"name": "Bharti Airtel", "sector": "Telecom"},
            "KOTAKBANK": {"name": "Kotak Mahindra Bank", "sector": "Banking"}
        }
        
        return mock_stocks.get(symbol, {"name": f"{symbol} Company", "sector": "Unknown"})

    def _get_fallback_portfolio(self) -> Dict[str, Any]:
        """Fallback portfolio data when errors occur"""
        return {
            "user_id": 1,
            "portfolio_id": 1,
            "name": "Demo Portfolio",
            "description": "Sample portfolio for demonstration",
            "holdings": [],
            "metrics": {
                "total_invested": 0,
                "current_value": 0,
                "total_profit_loss": 0,
                "total_return_percent": 0,
                "cash_balance": 100000,
                "total_portfolio_value": 100000
            },
            "trade_history": [],
            "last_updated": datetime.now().isoformat()
        }

# Create global instance
portfolio_service = PortfolioService()
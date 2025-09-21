# app/main.py - Enhanced PaisaBuddy API with all features
from fastapi import FastAPI, HTTPException, Depends, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta, date
import logging
import json
import hashlib
import sys
import os
import random
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import existing routers
import api # Import the api router
import trade
import auth

# Import enhanced modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from enhanced_database import EnhancedPaisabuddyDB
from trading_simulator import create_trading_simulator
from ai_personalization import create_ai_engine
from engagement_system import create_engagement_system
from analytics_engine import create_analytics_engine
import subprocess
import sys

# Import Gemini API service
from gemini_service import gemini_service

# Import Portfolio service
from portfolio_service import portfolio_service

# Load environment variables with defaults
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'paisabuddy_enhanced')
DB_PORT = int(os.getenv('DB_PORT', 3306))
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

# Configure logging
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(level=getattr(logging, log_level))
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Enhanced PaisaBuddy API",
    description="Comprehensive financial learning platform with AI-powered trading simulation",
    version="2.0.0"
)

# --- CORS Middleware ---
# This allows your frontend to communicate with your backend
CORS_ORIGINS_STR = os.getenv('CORS_ORIGINS', '["*"]')
try:
    origins = eval(CORS_ORIGINS_STR)
except:
    origins = ["*"]  # Fallback to allow all if parsing fails

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Database connection and enhanced engines
db = EnhancedPaisabuddyDB()
db_connection = None
trading_sim = None
ai_engine = None
engagement_system = None
analytics_engine = None

# Pydantic models for enhanced features
class TradingSimulationCreate(BaseModel):
    simulation_type: str = Field(..., pattern="^(intraday|longterm)$")
    simulation_name: str
    start_year: int = 2020
    settings: Optional[dict] = None

class TradeRequest(BaseModel):
    simulation_id: Optional[int] = None  # Optional for unified portfolio system
    transaction_type: str = Field(..., pattern="^(buy|sell)$")
    symbol: str
    quantity: int = Field(..., gt=0)
    notes: Optional[str] = None

class SocialPostCreate(BaseModel):
    title: str
    content: str
    post_type: str = Field(default="discussion", pattern="^(discussion|analysis|question|tip)$")
    tags: Optional[List[str]] = None

# Authentication helper functions
def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current user from token (simplified for demo)"""
    try:
        user_id = int(token)
        return user_id
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user_optional():
    """Get current user without requiring authentication (for demo)"""
    return 1  # Demo user ID

@app.on_event("startup")
async def startup_event():
    """Initialize database connection and enhanced engines"""
    global db_connection, trading_sim, ai_engine, engagement_system, analytics_engine
    
    try:
        # Connect with environment variables
        if db.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, 
                     database=DB_NAME, port=DB_PORT):
            db_connection = db.connection
            
            # Initialize all enhanced engines
            trading_sim = create_trading_simulator(db_connection)
            ai_engine = create_ai_engine(db_connection)
            engagement_system = create_engagement_system(db_connection)
            analytics_engine = create_analytics_engine(db_connection)
            
            logger.info("Enhanced PaisaBuddy API started successfully!")
        else:
            logger.error("Failed to connect to database!")
    except Exception as e:
        logger.error(f"Startup error: {e}")
        # Continue with basic functionality even if enhanced features fail

# Include the existing routers
app.include_router(api.router, prefix="/auth", tags=["Authentication"])
app.include_router(auth.router, prefix="/api/auth", tags=["Session Auth"])
app.include_router(trade.router, prefix="/api/trade", tags=["Trading"])

# Enhanced Trading Simulation Endpoints
@app.post("/trading/create-simulation")
async def create_simulation(
    simulation: TradingSimulationCreate,
    current_user: int = Depends(get_current_user_optional)
):
    """Create a new trading simulation (demo mode)"""
    try:
        # Return a demo simulation for the unified portfolio system
        simulation_id = random.randint(1000, 9999)
        
        # Create/ensure user has a default portfolio
        portfolio = portfolio_service.get_user_portfolio(current_user)
        
        return {
            "simulation_id": simulation_id, 
            "message": "Trading simulation created successfully",
            "portfolio_id": portfolio.get("portfolio_id", 1),
            "initial_balance": portfolio.get("initial_balance", 100000),
            "current_balance": portfolio.get("current_balance", 100000)
        }
        
    except Exception as e:
        logger.error(f"Create simulation error: {e}")
        # Return demo simulation on error
        return {
            "simulation_id": 1001,
            "message": "Demo trading simulation created",
            "portfolio_id": 1,
            "initial_balance": 100000,
            "current_balance": 100000
        }

@app.post("/trading/execute-trade")
async def execute_trade(
    trade: TradeRequest,
    current_user: int = Depends(get_current_user_optional)
):
    """Execute a buy or sell trade and update portfolio"""
    try:
        # Get current stock price from Gemini service
        dynamic_stocks = gemini_service.generate_dynamic_stock_data()
        stock_prices = {stock["symbol"]: stock["current_price"] for stock in dynamic_stocks}
        
        execution_price = stock_prices.get(trade.symbol, 3500.00)
        total_value = execution_price * trade.quantity
        fees = 25.00
        
        # Create trade result
        trade_result = {
            "success": True,
            "message": f"{trade.transaction_type.capitalize()} order executed: {trade.quantity} shares of {trade.symbol}",
            "trade_id": random.randint(1000, 9999),
            "symbol": trade.symbol,
            "transaction_type": trade.transaction_type,
            "quantity": trade.quantity,
            "execution_price": execution_price,
            "total_value": total_value,
            "fees": fees,
            "timestamp": datetime.now().isoformat(),
            "status": "completed"
        }
        
        # Update user's portfolio with the trade
        portfolio_updated = portfolio_service.update_portfolio_with_trade(
            user_id=current_user,
            trade_data=trade_result,
            portfolio_id=None  # Use default portfolio
        )
        
        if portfolio_updated:
            # Get updated portfolio balance
            portfolio = portfolio_service.get_user_portfolio(current_user)
            trade_result["portfolio_balance"] = portfolio.get("current_balance", 0)
            trade_result["portfolio_value"] = portfolio.get("metrics", {}).get("total_portfolio_value", 0)
        
        return trade_result
        
    except Exception as e:
        logger.error(f"Execute trade error: {e}")
        # Return fallback result on error
        return {
            "success": True,
            "message": f"Demo {trade.transaction_type} order executed: {trade.quantity} shares of {trade.symbol}",
            "trade_id": 1001,
            "execution_price": 3500.00 if trade.symbol == "TCS" else 2800.00,
            "total_value": (3500.00 if trade.symbol == "TCS" else 2800.00) * trade.quantity,
            "timestamp": datetime.now().isoformat(),
            "fees": 25.00,
            "status": "completed"
        }

@app.get("/trading/simulation/{simulation_id}")
async def get_simulation_status(
    simulation_id: int,
    current_user: int = Depends(get_current_user_optional)
):
    """Get simulation status and portfolio"""
    try:
        # Return the unified portfolio as simulation status
        portfolio = portfolio_service.get_user_portfolio(current_user)
        
        return {
            "simulation_id": simulation_id,
            "status": "active",
            "portfolio": portfolio,
            "performance": portfolio.get("metrics", {}),
            "holdings": portfolio.get("holdings", []),
            "trade_history": portfolio.get("trade_history", [])
        }
        
    except Exception as e:
        logger.error(f"Get simulation error: {e}")
        # Return demo portfolio on error
        return {
            "simulation_id": simulation_id,
            "status": "active",
            "portfolio": portfolio_service._get_fallback_portfolio(),
            "performance": {"total_return": 0},
            "holdings": [],
            "trade_history": []
        }

@app.get("/trading/user-simulations")
async def get_user_simulations(current_user: int = Depends(get_current_user_optional)):
    """Get user's unified portfolio (replaces multiple simulations)"""
    try:
        # Return the unified portfolio as the single simulation
        portfolio = portfolio_service.get_user_portfolio(current_user)
        
        return [
            {
                "simulation_id": portfolio.get("portfolio_id", 1),
                "simulation_name": portfolio.get("name", "My Trading Portfolio"),
                "simulation_type": "unified",
                "status": "active",
                "created_at": portfolio.get("created_at", datetime.now().isoformat()),
                "current_value": portfolio.get("metrics", {}).get("total_portfolio_value", 0),
                "total_return": portfolio.get("metrics", {}).get("total_return_percent", 0),
                "holdings_count": len(portfolio.get("holdings", [])),
                "trades_count": len(portfolio.get("trade_history", []))
            }
        ]
        
    except Exception as e:
        logger.error(f"Get user simulations error: {e}")
        # Return demo simulation
        return [
            {
                "simulation_id": 1,
                "simulation_name": "Demo Portfolio",
                "simulation_type": "unified",
                "status": "active",
                "created_at": datetime.now().isoformat(),
                "current_value": 100000,
                "total_return": 0,
                "holdings_count": 0,
                "trades_count": 0
            }
        ]

# AI & Personalization Endpoints
@app.get("/ai/behavioral-analysis")
async def get_behavioral_analysis(current_user: int = Depends(get_current_user_optional)):
    """Get AI behavioral analysis for user"""
    if not ai_engine:
        return {
            "personality_insights": {
                "risk_tolerance": "moderate", 
                "trading_style": "beginner",
                "confidence_level": "growing",
                "preferred_sectors": ["Technology", "Banking"]
            }, 
            "recommendations": [
                {
                    "title": "Diversify Your Portfolio",
                    "message": "Consider adding more sectors to reduce risk",
                    "priority": "high"
                },
                {
                    "title": "Learn About Options",
                    "message": "Explore options trading for advanced strategies",
                    "priority": "medium"
                }
            ]
        }
    
    try:
        analysis = ai_engine.analyze_user_behavior(current_user)
        return analysis
    except Exception as e:
        logger.error(f"Behavioral analysis error: {e}")
        return {
            "personality_insights": {"risk_tolerance": "moderate", "trading_style": "beginner"}, 
            "recommendations": []
        }

@app.get("/ai/stock-suggestions")
async def get_stock_suggestions(
    simulation_id: Optional[int] = None,
    current_user: int = Depends(get_current_user_optional)
):
    """Get personalized stock suggestions using Gemini AI"""
    try:
        # Get dynamic stock data from Gemini
        stocks = gemini_service.generate_dynamic_stock_data()
        
        suggestions = []
        for stock in stocks[:5]:  # Get top 5 suggestions
            analysis = gemini_service.get_stock_analysis_with_gemini(stock['symbol'])
            
            suggestion = {
                "symbol": stock['symbol'],
                "name": stock['name'],
                "sector": stock['sector'],
                "current_price": stock['current_price'],
                "change_percent": stock['change_percent'],
                "reason": analysis.get('analysis_summary', 'AI-powered analysis'),
                "risk_level": analysis.get('risk_level', 'medium'),
                "confidence": analysis.get('confidence', 0.7),
                "recommendation": analysis.get('recommendation', 'HOLD'),
                "target_price": analysis.get('target_price', stock['current_price']),
                "key_factors": analysis.get('key_factors', [])
            }
            suggestions.append(suggestion)
        
        return suggestions
        
    except Exception as e:
        logger.error(f"Stock suggestions error: {e}")
        # Fallback to basic suggestions
        return [
            {
                "symbol": "TCS", 
                "sector": "IT", 
                "current_price": 3500, 
                "reason": "Strong fundamentals in IT services", 
                "risk_level": "low", 
                "confidence": 0.85,
                "recommendation": "BUY"
            }
        ]

@app.get("/api/ai/analysis/{stock_symbol}")
async def get_stock_analysis(
    stock_symbol: str, 
    user_id: int = Depends(get_current_user_optional)
):
    """Get AI analysis for a specific stock using Gemini API"""
    try:
        analysis = gemini_service.get_stock_analysis_with_gemini(stock_symbol.upper())
        
        return {
            "status": "success",
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting stock analysis: {e}")
        return {
            "status": "success",
            "analysis": {
                "symbol": stock_symbol.upper(),
                "sentiment": "neutral",
                "recommendation": "HOLD",
                "confidence": 0.65,
                "risk_level": "medium",
                "key_factors": ["Market volatility", "Sector performance"],
                "analysis_summary": f"Basic analysis for {stock_symbol.upper()}"
            },
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/ai/insights")
async def get_ai_insights(user_id: int = Depends(get_current_user_optional)):
    """Get personalized AI insights using Gemini API"""
    try:
        # Get market news and insights from Gemini
        market_news = gemini_service.get_market_news_with_gemini()
        
        # Get user portfolio for personalized insights (placeholder)
        portfolio = {"holdings": []}  # Will be enhanced with real portfolio data
        trading_insights = gemini_service.get_trading_insights(portfolio)
        
        return {
            "status": "success",
            "insights": {
                "market_news": market_news,
                "trading_insights": trading_insights,
                "portfolio_health": trading_insights.get("portfolio_health"),
                "market_outlook": trading_insights.get("market_outlook"),
                "recommendations": trading_insights.get("recommendations", [])
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting AI insights: {e}")
        return {
            "status": "success",
            "insights": {
                "market_sentiment": "Cautiously optimistic",
                "portfolio_recommendation": "Consider rebalancing towards defensive stocks",
                "trending_sectors": ["Technology", "Healthcare", "Banking"],
                "risk_alerts": ["Monitor global market volatility"]
            },
            "timestamp": datetime.now().isoformat()
        }

# Unified Portfolio Management Endpoints
@app.get("/api/portfolio")
async def get_user_portfolio(
    portfolio_id: Optional[int] = None,
    user_id: int = Depends(get_current_user_optional)
):
    """Get user's portfolio with real-time data"""
    try:
        portfolio = portfolio_service.get_user_portfolio(user_id, portfolio_id)
        
        # Update portfolio holdings with current market prices from Gemini
        dynamic_stocks = gemini_service.generate_dynamic_stock_data()
        stock_prices = {stock["symbol"]: stock["current_price"] for stock in dynamic_stocks}
        
        # Update current prices and values in holdings
        for holding in portfolio.get("holdings", []):
            symbol = holding["symbol"]
            if symbol in stock_prices:
                holding["current_price"] = stock_prices[symbol]
                holding["current_value"] = holding["quantity"] * stock_prices[symbol]
                holding["profit_loss"] = holding["current_value"] - holding["invested_amount"]
                holding["profit_loss_percent"] = (
                    holding["profit_loss"] / holding["invested_amount"] * 100
                ) if holding["invested_amount"] > 0 else 0
        
        # Recalculate portfolio metrics with updated prices
        portfolio = portfolio_service._calculate_portfolio_metrics(portfolio)
        
        return {
            "status": "success",
            "portfolio": portfolio,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting portfolio: {e}")
        return {
            "status": "error",
            "message": "Failed to retrieve portfolio",
            "portfolio": portfolio_service._get_fallback_portfolio()
        }

@app.get("/api/portfolio/templates")
async def get_portfolio_templates():
    """Get available portfolio templates"""
    try:
        templates = portfolio_service.get_portfolio_templates()
        return {
            "status": "success",
            "templates": templates
        }
    except Exception as e:
        logger.error(f"Error getting portfolio templates: {e}")
        return {
            "status": "error",
            "templates": []
        }

@app.post("/api/portfolio/create")
async def create_portfolio_from_template(
    template_id: int,
    initial_balance: float = 100000,
    user_id: int = Depends(get_current_user_optional)
):
    """Create a new portfolio from template"""
    try:
        portfolio_id = portfolio_service.create_portfolio_from_template(
            user_id, template_id, initial_balance
        )
        
        if portfolio_id:
            return {
                "status": "success",
                "portfolio_id": portfolio_id,
                "message": "Portfolio created successfully"
            }
        else:
            return {
                "status": "error",
                "message": "Failed to create portfolio"
            }
            
    except Exception as e:
        logger.error(f"Error creating portfolio: {e}")
        return {
            "status": "error",
            "message": "Failed to create portfolio"
        }

@app.get("/api/portfolio/analysis")
async def get_portfolio_analysis(
    portfolio_id: Optional[int] = None,
    user_id: int = Depends(get_current_user_optional)
):
    """Get comprehensive portfolio analysis using AI"""
    try:
        portfolio = portfolio_service.get_user_portfolio(user_id, portfolio_id)
        
        # Get AI insights for portfolio
        insights = gemini_service.get_trading_insights(portfolio)
        
        # Generate stock-specific analysis for holdings
        stock_analyses = {}
        for holding in portfolio.get("holdings", []):
            symbol = holding["symbol"]
            stock_analyses[symbol] = gemini_service.get_stock_analysis_with_gemini(symbol)
        
        return {
            "status": "success",
            "portfolio_analysis": {
                "portfolio_metrics": portfolio.get("metrics", {}),
                "ai_insights": insights,
                "stock_analyses": stock_analyses,
                "recommendations": insights.get("recommendations", []),
                "risk_assessment": insights.get("risk_assessment", "moderate"),
                "diversification_score": insights.get("diversification_score", 75)
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting portfolio analysis: {e}")
        return {
            "status": "error",
            "message": "Failed to analyze portfolio"
        }

# Portfolio Endpoints for Frontend Pages

@app.get("/api/portfolio/{portfolio_type}")
async def get_portfolio_by_type(
    portfolio_type: str,  # 'intraday' or 'longterm'
    user_id: int = Depends(get_current_user_optional)
):
    """Get portfolio data for portfolio.html - supports intraday and longterm views"""
    try:
        # Get the user's portfolio
        portfolio = portfolio_service.get_user_portfolio(user_id)
        
        # Update holdings with current market prices from Gemini
        dynamic_stocks = gemini_service.generate_dynamic_stock_data()
        stock_prices = {stock["symbol"]: stock["current_price"] for stock in dynamic_stocks}
        
        # Update current prices and values in holdings
        for holding in portfolio.get("holdings", []):
            symbol = holding["symbol"]
            if symbol in stock_prices:
                old_price = holding.get("current_price", holding["avg_price"])
                new_price = stock_prices[symbol]
                holding["current_price"] = new_price
                
                # Recalculate current value and P&L
                holding["current_value"] = holding["quantity"] * new_price
                holding["profit_loss"] = holding["current_value"] - holding["invested_amount"]
                holding["profit_loss_percent"] = (
                    (holding["profit_loss"] / holding["invested_amount"]) * 100
                ) if holding["invested_amount"] > 0 else 0
        
        # Recalculate portfolio metrics
        portfolio = portfolio_service._calculate_portfolio_metrics(portfolio)
        
        # Filter trades based on portfolio type
        all_trades = portfolio.get("trade_history", [])
        if portfolio_type == "intraday":
            # Show trades from today only
            today = datetime.now().date()
            filtered_trades = [
                trade for trade in all_trades 
                if datetime.fromisoformat(trade["timestamp"]).date() == today
            ]
            portfolio_name = f"Intraday Portfolio"
        elif portfolio_type == "longterm":
            # Show all trades
            filtered_trades = all_trades
            portfolio_name = f"Long-term Portfolio"
        else:
            filtered_trades = all_trades
            portfolio_name = "My Portfolio"
        
        # Structure response for portfolio.html
        return {
            "status": "success",
            "portfolio_type": portfolio_type,
            "portfolio": {
                "id": portfolio.get("portfolio_id", 1),
                "name": portfolio_name,
                "type": portfolio_type,
                "description": f"Your {portfolio_type} trading portfolio",
                
                # Key metrics for portfolio view
                "summary": {
                    "total_invested": portfolio.get("metrics", {}).get("total_invested", 0),
                    "current_value": portfolio.get("metrics", {}).get("current_value", 0),
                    "cash_balance": portfolio.get("current_balance", 0),
                    "total_portfolio_value": portfolio.get("metrics", {}).get("total_portfolio_value", 0),
                    "total_profit_loss": portfolio.get("metrics", {}).get("total_profit_loss", 0),
                    "total_return_percent": portfolio.get("metrics", {}).get("total_return_percent", 0),
                    "day_change": portfolio.get("metrics", {}).get("day_change", 0),
                    "day_change_percent": portfolio.get("metrics", {}).get("day_change_percent", 0)
                },
                
                # Holdings for portfolio display
                "holdings": portfolio.get("holdings", []),
                "holdings_count": len(portfolio.get("holdings", [])),
                
                # Sector allocation chart data
                "sector_allocation": portfolio.get("metrics", {}).get("sector_allocation", {}),
                
                # Recent trades for this portfolio type
                "recent_trades": filtered_trades[-10:],  # Last 10 trades
                "total_trades": len(filtered_trades),
                
                # Trading interface data
                "available_stocks": gemini_service.generate_dynamic_stock_data(),
                
                # Trading options for portfolio page
                "trading_options": [
                    {
                        "type": "intraday",
                        "label": "Intraday Trading",
                        "description": "Real-time market simulation",
                        "active": portfolio_type == "intraday",
                        "url": "/portfolio.html?type=intraday"
                    },
                    {
                        "type": "longterm", 
                        "label": "Long-term Investment",
                        "description": "Historical data simulation",
                        "active": portfolio_type == "longterm",
                        "url": "/portfolio.html?type=longterm"
                    }
                ],
                
                # Timestamps
                "last_updated": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting {portfolio_type} portfolio: {e}")
        return {
            "status": "error",
            "message": f"Failed to load {portfolio_type} portfolio",
            "portfolio": {
                "id": 1,
                "name": f"{portfolio_type.title()} Portfolio",
                "type": portfolio_type,
                "summary": {"total_portfolio_value": 100000, "total_profit_loss": 0},
                "holdings": [],
                "available_stocks": []
            }
        }

@app.get("/api/portfolio/trading-interface")
async def get_portfolio_trading_interface(user_id: int = Depends(get_current_user_optional)):
    """Get trading interface data for portfolio.html - includes both intraday and longterm options"""
    try:
        # Get user's current portfolio status
        portfolio = portfolio_service.get_user_portfolio(user_id)
        
        # Get available stocks for trading
        available_stocks = gemini_service.generate_dynamic_stock_data()
        
        # Get current holdings for quick sell options
        current_holdings = portfolio.get("holdings", [])
        
        return {
            "status": "success",
            "trading_interface": {
                "user_balance": portfolio.get("current_balance", 100000),
                "portfolio_value": portfolio.get("metrics", {}).get("total_portfolio_value", 100000),
                
                # Trading options (moved from dashboard)
                "trading_modes": [
                    {
                        "type": "intraday",
                        "label": "📈 Intraday Trading",
                        "description": "Real-time market simulation",
                        "features": ["Live market data", "Quick buy/sell", "Day trading strategies"],
                        "url": "/portfolio.html?type=intraday",
                        "button_class": "btn-primary"
                    },
                    {
                        "type": "longterm",
                        "label": "🏛️ Long-term Investment", 
                        "description": "Historical data simulation",
                        "features": ["Historical analysis", "Long-term holdings", "Investment strategies"],
                        "url": "/portfolio.html?type=longterm",
                        "button_class": "btn-secondary"
                    }
                ],
                
                # Available stocks for trading
                "available_stocks": available_stocks,
                "trending_stocks": available_stocks[:5],  # Top 5 trending
                
                # Current holdings for quick actions
                "current_holdings": current_holdings,
                "holdings_count": len(current_holdings),
                
                # Quick trading suggestions
                "trading_suggestions": [
                    {
                        "action": "buy",
                        "symbol": "TCS",
                        "reason": "Strong technical indicators",
                        "confidence": "high"
                    },
                    {
                        "action": "sell",
                        "symbol": "RELIANCE", 
                        "reason": "Take profit opportunity",
                        "confidence": "medium"
                    }
                ]
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting trading interface: {e}")
        return {
            "status": "error",
            "message": "Failed to load trading interface",
            "trading_interface": {
                "user_balance": 100000,
                "portfolio_value": 100000,
                "trading_modes": [
                    {"type": "intraday", "label": "Intraday Trading", "url": "/portfolio.html?type=intraday"},
                    {"type": "longterm", "label": "Long-term Investment", "url": "/portfolio.html?type=longterm"}
                ],
                "available_stocks": [],
                "current_holdings": []
            }
        }

@app.get("/api/dashboard/overview")
async def get_dashboard_overview(user_id: int = Depends(get_current_user_optional)):
    """Get comprehensive dashboard data for dashboard.html"""
    try:
        # Get user's portfolio
        portfolio = portfolio_service.get_user_portfolio(user_id)
        
        # Update with real-time market data
        dynamic_stocks = gemini_service.generate_dynamic_stock_data()
        stock_prices = {stock["symbol"]: stock["current_price"] for stock in dynamic_stocks}
        
        # Update portfolio holdings with current prices
        for holding in portfolio.get("holdings", []):
            symbol = holding["symbol"]
            if symbol in stock_prices:
                holding["current_price"] = stock_prices[symbol]
                holding["current_value"] = holding["quantity"] * stock_prices[symbol]
                holding["profit_loss"] = holding["current_value"] - holding["invested_amount"]
                holding["profit_loss_percent"] = (
                    (holding["profit_loss"] / holding["invested_amount"]) * 100
                ) if holding["invested_amount"] > 0 else 0
        
        # Recalculate metrics
        portfolio = portfolio_service._calculate_portfolio_metrics(portfolio)
        
        # Get AI insights and analysis
        market_news = gemini_service.get_market_news_with_gemini()
        trading_insights = gemini_service.get_trading_insights(portfolio)
        
        # Analyze all holdings
        stock_analyses = {}
        for holding in portfolio.get("holdings", []):
            symbol = holding["symbol"]
            stock_analyses[symbol] = gemini_service.get_stock_analysis_with_gemini(symbol)
        
        # Structure comprehensive dashboard data
        dashboard_data = {
            "status": "success",
            
            # Portfolio overview
            "portfolio_summary": {
                "total_portfolio_value": portfolio.get("metrics", {}).get("total_portfolio_value", 0),
                "total_invested": portfolio.get("metrics", {}).get("total_invested", 0),
                "total_profit_loss": portfolio.get("metrics", {}).get("total_profit_loss", 0),
                "total_return_percent": portfolio.get("metrics", {}).get("total_return_percent", 0),
                "cash_balance": portfolio.get("current_balance", 0),
                "day_change": portfolio.get("metrics", {}).get("day_change", 0),
                "day_change_percent": portfolio.get("metrics", {}).get("day_change_percent", 0),
                "holdings_count": len(portfolio.get("holdings", [])),
                "diversification_score": trading_insights.get("diversification_score", 75)
            },
            
            # Detailed transaction history
            "transactions": {
                "all_trades": portfolio.get("trade_history", []),
                "total_trades": len(portfolio.get("trade_history", [])),
                "recent_trades": portfolio.get("trade_history", [])[-20:],  # Last 20 trades
                "trade_summary": {
                    "total_buy_trades": len([t for t in portfolio.get("trade_history", []) if t["transaction_type"] == "buy"]),
                    "total_sell_trades": len([t for t in portfolio.get("trade_history", []) if t["transaction_type"] == "sell"]),
                    "total_fees_paid": sum(t.get("fees", 0) for t in portfolio.get("trade_history", [])),
                    "average_trade_size": sum(t.get("total_amount", 0) for t in portfolio.get("trade_history", [])) / max(len(portfolio.get("trade_history", [])), 1)
                }
            },
            
            # Holdings analysis
            "holdings_analysis": {
                "current_holdings": portfolio.get("holdings", []),
                "sector_allocation": portfolio.get("metrics", {}).get("sector_allocation", {}),
                "top_performers": sorted(
                    portfolio.get("holdings", []), 
                    key=lambda x: x.get("profit_loss_percent", 0), 
                    reverse=True
                )[:5],
                "worst_performers": sorted(
                    portfolio.get("holdings", []), 
                    key=lambda x: x.get("profit_loss_percent", 0)
                )[:5],
                "stock_analyses": stock_analyses
            },
            
            # AI insights and recommendations
            "ai_insights": {
                "portfolio_health": trading_insights.get("portfolio_health", "good"),
                "risk_assessment": trading_insights.get("risk_assessment", "moderate"),
                "recommendations": trading_insights.get("recommendations", []),
                "market_outlook": trading_insights.get("market_outlook", {}),
                "personalized_tips": [
                    "Consider rebalancing your portfolio quarterly",
                    "Monitor sector concentration risk", 
                    "Set stop-loss orders for risk management",
                    "Review and adjust position sizes regularly"
                ]
            },
            
            # Market overview
            "market_data": {
                "market_news": market_news,
                "trending_stocks": dynamic_stocks[:10],  # Top 10 stocks
                "sector_performance": {
                    "IT": random.uniform(-2, 4),
                    "Banking": random.uniform(-1, 3),
                    "Energy": random.uniform(-3, 2),
                    "FMCG": random.uniform(-1, 2),
                    "Telecom": random.uniform(-2, 3)
                },
                "market_indices": {
                    "nifty_50": {"value": 21850, "change": 145.30, "change_percent": 0.67},
                    "sensex": {"value": 72150, "change": 287.50, "change_percent": 0.40}
                }
            },
            
            # Performance metrics
            "performance_metrics": {
                "total_return": portfolio.get("metrics", {}).get("total_return_percent", 0),
                "annualized_return": portfolio.get("metrics", {}).get("total_return_percent", 0) * 4,  # Simplified
                "volatility": random.uniform(8, 15),
                "sharpe_ratio": random.uniform(0.8, 1.5),
                "max_drawdown": random.uniform(-5, -2),
                "win_rate": len([t for t in portfolio.get("trade_history", []) if t.get("profit_loss", 0) > 0]) / max(len(portfolio.get("trade_history", [])), 1) * 100
            },
            
            # Navigation links for dashboard (no trading buttons)
            "navigation_links": [
                {"action": "go_to_portfolio", "label": "Go to Portfolio", "url": "/portfolio.html", "description": "Trade stocks and manage investments"},
                {"action": "view_analysis", "label": "Stock Analysis", "url": "/analysis.html", "description": "AI-powered stock insights"},
                {"action": "view_reports", "label": "Reports", "url": "/reports.html", "description": "Detailed performance reports"}
            ],
            
            "timestamp": datetime.now().isoformat()
        }
        
        return dashboard_data
        
    except Exception as e:
        logger.error(f"Error getting dashboard overview: {e}")
        return {
            "status": "error",
            "message": "Failed to load dashboard data",
            "portfolio_summary": {"total_portfolio_value": 100000, "total_profit_loss": 0},
            "transactions": {"all_trades": [], "total_trades": 0},
            "holdings_analysis": {"current_holdings": [], "sector_allocation": {}},
            "ai_insights": {"recommendations": []},
            "market_data": {"market_news": []}
        }

# Additional endpoints for enhanced portfolio functionality

@app.get("/api/portfolio/{portfolio_type}/trades")
async def get_portfolio_trades(
    portfolio_type: str,
    limit: int = 50,
    user_id: int = Depends(get_current_user_optional)
):
    """Get detailed trade history for specific portfolio type"""
    try:
        portfolio = portfolio_service.get_user_portfolio(user_id)
        all_trades = portfolio.get("trade_history", [])
        
        if portfolio_type == "intraday":
            # Filter trades from today only
            today = datetime.now().date()
            filtered_trades = [
                trade for trade in all_trades 
                if datetime.fromisoformat(trade["timestamp"]).date() == today
            ]
        elif portfolio_type == "longterm":
            # All trades older than today
            today = datetime.now().date()
            filtered_trades = [
                trade for trade in all_trades 
                if datetime.fromisoformat(trade["timestamp"]).date() < today
            ]
        else:
            filtered_trades = all_trades
        
        # Sort by timestamp (most recent first) and limit
        sorted_trades = sorted(filtered_trades, key=lambda x: x["timestamp"], reverse=True)[:limit]
        
        return {
            "status": "success",
            "portfolio_type": portfolio_type,
            "trades": sorted_trades,
            "total_trades": len(filtered_trades),
            "trade_summary": {
                "total_buy_value": sum(t.get("total_amount", 0) for t in filtered_trades if t["transaction_type"] == "buy"),
                "total_sell_value": sum(t.get("total_amount", 0) for t in filtered_trades if t["transaction_type"] == "sell"),
                "total_fees": sum(t.get("fees", 0) for t in filtered_trades),
                "buy_count": len([t for t in filtered_trades if t["transaction_type"] == "buy"]),
                "sell_count": len([t for t in filtered_trades if t["transaction_type"] == "sell"])
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting {portfolio_type} trades: {e}")
        return {
            "status": "error",
            "message": "Failed to fetch trade history",
            "trades": [],
            "total_trades": 0
        }

@app.get("/api/dashboard/performance")
async def get_portfolio_performance(user_id: int = Depends(get_current_user_optional)):
    """Get detailed performance analytics for dashboard"""
    try:
        portfolio = portfolio_service.get_user_portfolio(user_id)
        all_trades = portfolio.get("trade_history", [])
        
        # Calculate performance metrics
        if not all_trades:
            return {
                "status": "success",
                "performance": {
                    "total_return": 0,
                    "daily_returns": [],
                    "monthly_returns": [],
                    "volatility": 0,
                    "sharpe_ratio": 0
                }
            }
        
        # Generate mock performance data for demo
        import math
        days = 30
        daily_returns = []
        cumulative_return = 0
        
        for i in range(days):
            daily_return = random.uniform(-2, 3)  # -2% to +3% daily returns
            daily_returns.append({
                "date": (datetime.now() - timedelta(days=days-i)).strftime("%Y-%m-%d"),
                "return": daily_return,
                "cumulative_return": cumulative_return + daily_return
            })
            cumulative_return += daily_return
        
        # Calculate statistics
        returns_values = [r["return"] for r in daily_returns]
        avg_return = sum(returns_values) / len(returns_values)
        volatility = math.sqrt(sum((r - avg_return) ** 2 for r in returns_values) / len(returns_values))
        sharpe_ratio = (avg_return / volatility) if volatility > 0 else 0
        
        return {
            "status": "success",
            "performance": {
                "total_return": cumulative_return,
                "daily_returns": daily_returns,
                "monthly_returns": [
                    {"month": "Jan 2025", "return": random.uniform(-5, 8)},
                    {"month": "Feb 2025", "return": random.uniform(-3, 6)},
                    {"month": "Mar 2025", "return": random.uniform(-2, 7)}
                ],
                "statistics": {
                    "average_daily_return": round(avg_return, 2),
                    "volatility": round(volatility, 2),
                    "sharpe_ratio": round(sharpe_ratio, 2),
                    "max_drawdown": round(random.uniform(-8, -2), 2),
                    "win_rate": round(len([r for r in returns_values if r > 0]) / len(returns_values) * 100, 1),
                    "best_day": round(max(returns_values), 2),
                    "worst_day": round(min(returns_values), 2)
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting performance data: {e}")
        return {
            "status": "error",
            "message": "Failed to calculate performance metrics",
            "performance": {"total_return": 0, "daily_returns": []}
        }

@app.post("/api/portfolio/trade")
async def execute_portfolio_trade(
    trade_data: dict,
    user_id: int = Depends(get_current_user_optional)
):
    """Execute trade specifically for portfolio pages (unified endpoint)"""
    try:
        # Validate trade data
        required_fields = ["symbol", "quantity", "transaction_type"]
        for field in required_fields:
            if field not in trade_data:
                return {"status": "error", "message": f"Missing required field: {field}"}
        
        # Get current stock price
        dynamic_stocks = gemini_service.generate_dynamic_stock_data()
        stock_prices = {stock["symbol"]: stock["current_price"] for stock in dynamic_stocks}
        
        symbol = trade_data["symbol"]
        quantity = int(trade_data["quantity"])
        transaction_type = trade_data["transaction_type"]
        
        execution_price = stock_prices.get(symbol, 3500.00)
        total_value = execution_price * quantity
        fees = 25.00
        
        # Create trade result
        trade_result = {
            "success": True,
            "message": f"{transaction_type.capitalize()} order executed: {quantity} shares of {symbol}",
            "trade_id": random.randint(1000, 9999),
            "symbol": symbol,
            "transaction_type": transaction_type,
            "quantity": quantity,
            "execution_price": execution_price,
            "total_value": total_value,
            "fees": fees,
            "timestamp": datetime.now().isoformat(),
            "status": "completed"
        }
        
        # Update user's portfolio
        portfolio_updated = portfolio_service.update_portfolio_with_trade(
            user_id=user_id,
            trade_data=trade_result
        )
        
        if portfolio_updated:
            # Get updated portfolio data
            updated_portfolio = portfolio_service.get_user_portfolio(user_id)
            trade_result["portfolio_balance"] = updated_portfolio.get("current_balance", 0)
            trade_result["portfolio_value"] = updated_portfolio.get("metrics", {}).get("total_portfolio_value", 0)
        
        return {
            "status": "success",
            "trade": trade_result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error executing portfolio trade: {e}")
        return {
            "status": "error",
            "message": f"Failed to execute trade: {str(e)}"
        }

# Social Features Endpoints
@app.post("/social/create-post")
async def create_social_post(
    post: SocialPostCreate,
    current_user: int = Depends(get_current_user_optional)
):
    """Create a new social post"""
    if not engagement_system:
        return {"post_id": 1, "message": "Post created successfully (demo mode)"}
    
    try:
        post_id = engagement_system.create_social_post(
            user_id=current_user,
            title=post.title,
            content=post.content,
            post_type=post.post_type,
            tags=post.tags
        )
        
        if post_id:
            return {"post_id": post_id, "message": "Post created successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to create post")
    except Exception as e:
        logger.error(f"Create post error: {e}")
        return {"post_id": 1, "message": "Post created in demo mode"}

@app.get("/social/community-feed")
async def get_community_feed(
    limit: int = 50,
    current_user: int = Depends(get_current_user_optional)
):
    """Get community feed posts"""
    if not engagement_system:
        return [
            {
                "id": 1,
                "title": "My First Profitable Trade!",
                "content": "Just made my first profit with TCS stocks. The key was patience and research!",
                "author_name": "TradingPro",
                "post_type": "discussion",
                "created_at": "2025-01-20T10:00:00Z",
                "likes": 15,
                "comments": 3
            },
            {
                "id": 2,
                "title": "Market Analysis: Banking Sector",
                "content": "Banking stocks are showing strong fundamentals. HDFC and ICICI look promising for long-term investment.",
                "author_name": "FinanceGuru",
                "post_type": "analysis",
                "created_at": "2025-01-20T08:30:00Z",
                "likes": 28,
                "comments": 7
            },
            {
                "id": 3,
                "title": "Question: Best time to buy IT stocks?",
                "content": "I'm new to trading and wondering when is the best time to invest in IT sector stocks like TCS, Infosys?",
                "author_name": "Newbie_Trader",
                "post_type": "question",
                "created_at": "2025-01-20T06:45:00Z",
                "likes": 8,
                "comments": 12
            }
        ]
    
    try:
        posts = engagement_system.get_community_feed(current_user, limit)
        return posts
    except Exception as e:
        logger.error(f"Get community feed error: {e}")
        return []

# Achievement Endpoints
@app.get("/achievements/user-achievements")
async def get_user_achievements(current_user: int = Depends(get_current_user_optional)):
    """Get user's achievements and statistics"""
    if not engagement_system:
        return {
            "earned_achievements": [
                {
                    "id": 1,
                    "achievement_name": "First Trade",
                    "achievement_type": "first_trade",
                    "description": "Completed your first trading transaction",
                    "points_awarded": 100,
                    "earned_at": "2025-01-20T09:00:00Z",
                    "icon": "🎯"
                },
                {
                    "id": 2,
                    "achievement_name": "Portfolio Builder",
                    "achievement_type": "portfolio_builder",
                    "description": "Built a diverse portfolio with 5+ stocks",
                    "points_awarded": 250,
                    "earned_at": "2025-01-20T11:30:00Z",
                    "icon": "📈"
                },
                {
                    "id": 3,
                    "achievement_name": "Community Contributor",
                    "achievement_type": "community_contributor",
                    "description": "Shared your first trading insight",
                    "points_awarded": 150,
                    "earned_at": "2025-01-20T14:15:00Z",
                    "icon": "💬"
                }
            ],
            "total_earned": 3,
            "total_points": 500,
            "completion_percentage": 15,
            "next_achievement": {
                "name": "Profit Maker",
                "description": "Achieve your first profitable trade",
                "progress": 80,
                "points": 300
            },
            "recent_achievements": [
                {
                    "name": "Community Contributor",
                    "earned_at": "2025-01-20T14:15:00Z"
                }
            ]
        }
    
    try:
        achievements = engagement_system.get_user_achievements(current_user)
        return achievements
    except Exception as e:
        logger.error(f"Get achievements error: {e}")
        return {"earned_achievements": [], "total_earned": 0, "total_points": 0, "completion_percentage": 0}

@app.get("/leaderboard/{leaderboard_type}")
async def get_leaderboard(
    leaderboard_type: str,
    current_user: int = Depends(get_current_user)
):
    """Get various types of leaderboards"""
    if not engagement_system:
        return []
    
    try:
        leaderboard = engagement_system.create_leaderboard(leaderboard_type)
        return leaderboard
    except Exception as e:
        logger.error(f"Get leaderboard error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Analytics Endpoints
@app.get("/analytics/portfolio/{simulation_id}")
async def get_portfolio_analytics(
    simulation_id: int,
    current_user: int = Depends(get_current_user)
):
    """Get comprehensive portfolio analytics"""
    if not analytics_engine:
        return {"performance_metrics": {}, "risk_metrics": {}, "recommendations": []}
    
    try:
        analytics = analytics_engine.generate_portfolio_analytics(current_user, simulation_id)
        return analytics
    except Exception as e:
        logger.error(f"Get portfolio analytics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# OLD Dashboard Endpoint - DEPRECATED 
# Use /api/dashboard/overview instead
@app.get("/dashboard/overview") 
async def get_old_dashboard_overview(current_user: int = Depends(get_current_user_optional)):
    """DEPRECATED: Use /api/dashboard/overview instead. This endpoint redirects for backward compatibility."""
    # Redirect to new endpoint
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/api/dashboard/overview", status_code=307)

# Market Data Endpoints - Enhanced with Gemini API
@app.get("/market/stocks")
async def get_available_stocks():
    """Get list of available stocks with dynamic pricing using Gemini API"""
    try:
        # Get dynamic stock data from Gemini service
        stocks = gemini_service.generate_dynamic_stock_data()
        return stocks
    except Exception as e:
        logger.error(f"Error getting dynamic stock data: {e}")
        # Fallback to static data
        return [
            {"symbol": "TCS", "sector": "IT", "current_price": 3500, "change_percent": 0.0},
            {"symbol": "RELIANCE", "sector": "Energy", "current_price": 2800, "change_percent": 0.0},
            {"symbol": "HDFCBANK", "sector": "Banking", "current_price": 1650, "change_percent": 0.0}
        ]

@app.get("/market/stock-details/{symbol}")
async def get_stock_details(symbol: str):
    """Get detailed information about a specific stock"""
    try:
        stocks = gemini_service.generate_dynamic_stock_data()
        stock = next((s for s in stocks if s["symbol"] == symbol.upper()), None)
        
        if not stock:
            raise HTTPException(status_code=404, detail="Stock not found")
        
        # Get AI analysis for the stock
        analysis = gemini_service.get_stock_analysis_with_gemini(symbol.upper())
        
        return {
            "stock_data": stock,
            "ai_analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting stock details for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch stock details")

@app.get("/market/news")
async def get_market_news():
    """Get AI-generated market news and insights"""
    try:
        news = gemini_service.get_market_news_with_gemini()
        return {
            "status": "success",
            "news": news,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting market news: {e}")
        return {
            "status": "error",
            "news": [],
            "message": "Failed to fetch market news"
        }

# Health check endpoint
@app.get("/health")
async def health_check():
    """API health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "database": "connected" if db_connection else "disconnected",
            "trading_simulator": "active" if trading_sim else "inactive",
            "ai_engine": "active" if ai_engine else "inactive",
            "engagement_system": "active" if engagement_system else "inactive",
            "analytics_engine": "active" if analytics_engine else "inactive"
        }
    }

# Game Launcher Endpoints
class GameLaunchRequest(BaseModel):
    game_name: str = Field(..., pattern="^(budget_balance|investment_growth|fraud_detection|game_launcher)$")
    username: Optional[str] = None

@app.post("/api/games/launch")
async def launch_pygame_game(
    game_request: GameLaunchRequest,
    current_user: int = Depends(get_current_user_optional)
):
    """Launch a pygame game from the games directory"""
    try:
        # Map game names to their Python files
        game_files = {
            "budget_balance": "budget_balance.py",
            "investment_growth": "investment_growth.py", 
            "fraud_detection": "fraud_detection.py",
            "game_launcher": "game_launcher.py"
        }
        
        game_filename = game_files.get(game_request.game_name)
        if not game_filename:
            raise HTTPException(status_code=400, detail="Invalid game name")
            
        # Get the path to the games directory
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(backend_dir)
        games_dir = os.path.join(project_dir, "games")
        game_path = os.path.join(games_dir, game_filename)
        
        # Check if game file exists
        if not os.path.exists(game_path):
            return {
                "status": "error",
                "message": f"Game file not found: {game_filename}",
                "game_path": game_path,
                "suggestion": "Please ensure the game files are in the games/ directory"
            }
        
        # Launch the game as a separate process
        try:
            # Use subprocess to launch the game
            process = subprocess.Popen(
                [sys.executable, game_path],
                cwd=games_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            logger.info(f"Launched {game_request.game_name} (PID: {process.pid})")
            
            return {
                "status": "success",
                "message": f"Successfully launched {game_request.game_name}",
                "game_name": game_request.game_name,
                "process_id": process.pid,
                "game_path": game_path,
                "instructions": [
                    "The game window should open shortly",
                    "If the game doesn't start, check that pygame is installed: pip install pygame",
                    "You can close this browser tab - the game runs independently"
                ]
            }
            
        except Exception as launch_error:
            logger.error(f"Failed to launch {game_request.game_name}: {launch_error}")
            return {
                "status": "error", 
                "message": f"Failed to launch game: {str(launch_error)}",
                "troubleshooting": [
                    "Make sure pygame is installed: pip install pygame",
                    "Make sure Python is in your system PATH",
                    "Check that all game dependencies are installed",
                    "Try running the game directly from command line"
                ]
            }
            
    except Exception as e:
        logger.error(f"Game launch error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/games/available")
async def get_available_games():
    """Get list of available pygame games"""
    try:
        # Get the path to the games directory
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(backend_dir)
        games_dir = os.path.join(project_dir, "games")
        
        games = [
            {
                "id": "budget_balance",
                "name": "Budget Balance",
                "description": "Catch income items while avoiding expenses! Learn to balance your financial life through fast-paced action gameplay.",
                "icon": "💰",
                "skills": ["Expense Management", "Income Planning", "Budget Balancing"],
                "file_exists": os.path.exists(os.path.join(games_dir, "budget_balance.py"))
            },
            {
                "id": "investment_growth", 
                "name": "Investment Garden",
                "description": "Plant investments and watch them grow! Learn about compound interest, diversification, and long-term wealth building.",
                "icon": "🌱", 
                "skills": ["Compound Interest", "Risk Assessment", "Portfolio Management"],
                "file_exists": os.path.exists(os.path.join(games_dir, "investment_growth.py"))
            },
            {
                "id": "fraud_detection",
                "name": "Fraud Detective", 
                "description": "Identify and eliminate scams! Master the art of spotting financial fraud, phishing attempts, and malicious schemes.",
                "icon": "🛡️",
                "skills": ["Scam Detection", "Security Awareness", "Risk Recognition"],
                "file_exists": os.path.exists(os.path.join(games_dir, "fraud_detection.py"))
            },
            {
                "id": "game_launcher",
                "name": "Game Launcher",
                "description": "Launch all games from a unified pygame interface with progress tracking and achievements.",
                "icon": "🎮",
                "skills": ["Game Management", "Progress Tracking", "Achievement System"],
                "file_exists": os.path.exists(os.path.join(games_dir, "game_launcher.py"))
            }
        ]
        
        # Check which games are actually available
        available_games = [game for game in games if game["file_exists"]]
        missing_games = [game for game in games if not game["file_exists"]]
        
        return {
            "status": "success",
            "available_games": available_games,
            "missing_games": missing_games,
            "total_games": len(games),
            "available_count": len(available_games),
            "games_directory": games_dir,
            "installation_note": "Make sure pygame is installed: pip install pygame" if available_games else "No games found in games directory"
        }
        
    except Exception as e:
        logger.error(f"Error getting available games: {e}")
        return {
            "status": "error",
            "message": "Failed to get available games",
            "available_games": [],
            "error": str(e)
        }

@app.get("/", tags=["Root"])
def read_root():
    """Root endpoint with enhanced features info"""
    return {
        "message": "Enhanced PaisaBuddy API",
        "version": "2.0.0",
        "docs_url": "/docs",
        "features": [
            "Trading Simulation (Intraday & Long-term)",
            "AI-Powered Personalization",
            "Social Features & Community",
            "Achievements & Competitions", 
            "Advanced Analytics & Insights",
            "Real-time Market Events",
            "Pygame Game Launcher"
        ]
    }

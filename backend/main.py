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
    simulation_id: int
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
    current_user: int = Depends(get_current_user)
):
    """Create a new trading simulation"""
    if not trading_sim:
        raise HTTPException(status_code=503, detail="Trading simulator not available")
    
    try:
        simulation_id = trading_sim.create_simulation(
            user_id=current_user,
            simulation_type=simulation.simulation_type,
            simulation_name=simulation.simulation_name,
            start_year=simulation.start_year,
            settings=simulation.settings
        )
        
        if simulation_id:
            return {"simulation_id": simulation_id, "message": "Simulation created successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to create simulation")
    except Exception as e:
        logger.error(f"Create simulation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/trading/execute-trade")
async def execute_trade(
    trade: TradeRequest,
    current_user: int = Depends(get_current_user)
):
    """Execute a buy or sell trade"""
    if not trading_sim:
        raise HTTPException(status_code=503, detail="Trading simulator not available")
    
    try:
        result = trading_sim.execute_trade(
            simulation_id=trade.simulation_id,
            transaction_type=trade.transaction_type,
            symbol=trade.symbol,
            quantity=trade.quantity,
            notes=trade.notes
        )
        
        if result['success'] and engagement_system:
            # Check for achievements after trade
            engagement_system.check_and_award_achievements(current_user)
        
        return result
    except Exception as e:
        logger.error(f"Execute trade error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/trading/simulation/{simulation_id}")
async def get_simulation_status(
    simulation_id: int,
    current_user: int = Depends(get_current_user)
):
    """Get simulation status and portfolio"""
    if not trading_sim:
        raise HTTPException(status_code=503, detail="Trading simulator not available")
    
    try:
        status = trading_sim.get_simulation_status(simulation_id)
        if not status:
            raise HTTPException(status_code=404, detail="Simulation not found")
        return status
    except Exception as e:
        logger.error(f"Get simulation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/trading/user-simulations")
async def get_user_simulations(current_user: int = Depends(get_current_user)):
    """Get all simulations for current user"""
    if not db_connection:
        raise HTTPException(status_code=503, detail="Database not available")
    
    cursor = db_connection.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT * FROM trading_simulations 
            WHERE user_id = %s 
            ORDER BY created_at DESC
        """, (current_user,))
        
        simulations = cursor.fetchall()
        return simulations
    except Exception as e:
        logger.error(f"Get user simulations error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()

# AI & Personalization Endpoints
@app.get("/ai/behavioral-analysis")
async def get_behavioral_analysis(current_user: int = Depends(get_current_user)):
    """Get AI behavioral analysis for user"""
    if not ai_engine:
        return {"personality_insights": {"risk_tolerance": "moderate", "trading_style": "beginner"}, "recommendations": []}
    
    try:
        analysis = ai_engine.analyze_user_behavior(current_user)
        return analysis
    except Exception as e:
        logger.error(f"Behavioral analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ai/stock-suggestions")
async def get_stock_suggestions(
    simulation_id: Optional[int] = None,
    current_user: int = Depends(get_current_user)
):
    """Get personalized stock suggestions"""
    if not ai_engine:
        return [{"symbol": "TCS", "sector": "IT", "current_price": 3500, "reason": "Stable large cap stock", "risk_level": "low", "confidence": 0.8}]
    
    try:
        suggestions = ai_engine.get_personalized_stock_suggestions(current_user, simulation_id)
        return suggestions
    except Exception as e:
        logger.error(f"Stock suggestions error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Social Features Endpoints
@app.post("/social/create-post")
async def create_social_post(
    post: SocialPostCreate,
    current_user: int = Depends(get_current_user)
):
    """Create a new social post"""
    if not engagement_system:
        raise HTTPException(status_code=503, detail="Social features not available")
    
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
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/social/community-feed")
async def get_community_feed(
    limit: int = 50,
    current_user: int = Depends(get_current_user)
):
    """Get community feed posts"""
    if not engagement_system:
        return []
    
    try:
        posts = engagement_system.get_community_feed(current_user, limit)
        return posts
    except Exception as e:
        logger.error(f"Get community feed error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Achievement Endpoints
@app.get("/achievements/user-achievements")
async def get_user_achievements(current_user: int = Depends(get_current_user)):
    """Get user's achievements and statistics"""
    if not engagement_system:
        return {"earned_achievements": [], "total_earned": 0, "total_points": 0, "completion_percentage": 0}
    
    try:
        achievements = engagement_system.get_user_achievements(current_user)
        return achievements
    except Exception as e:
        logger.error(f"Get achievements error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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

# Dashboard Endpoint
@app.get("/dashboard/overview")
async def get_dashboard_overview(current_user: int = Depends(get_current_user)):
    """Get comprehensive dashboard overview"""
    try:
        dashboard = {"user_stats": {}, "achievements": {}, "performance": {}, "ai_insights": {}}
        
        if engagement_system:
            achievements = engagement_system.get_user_achievements(current_user)
            stats_summary = engagement_system.get_user_stats_summary(current_user)
            dashboard["achievements"] = {
                "total_earned": achievements.get("total_earned", 0),
                "total_points": achievements.get("total_points", 0),
                "recent_achievements": achievements.get("recent_achievements", [])
            }
            dashboard["user_stats"] = stats_summary
        
        if analytics_engine:
            analytics_summary = analytics_engine.get_user_analytics_summary(current_user)
            dashboard["performance"] = analytics_summary.get("overall_metrics", {})
        
        if ai_engine:
            behavioral_analysis = ai_engine.analyze_user_behavior(current_user, days_back=30)
            dashboard["ai_insights"] = {
                "personality": behavioral_analysis.get("personality_insights", {}),
                "recommendations": behavioral_analysis.get("recommendations", [])[:3]
            }
        
        return dashboard
    except Exception as e:
        logger.error(f"Get dashboard error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Market Data Endpoints
@app.get("/market/stocks")
async def get_available_stocks():
    """Get list of available stocks for trading"""
    if not db_connection:
        # Return some default stocks if database not available
        return [
            {"symbol": "TCS", "sector": "IT", "current_price": 3500},
            {"symbol": "RELIANCE", "sector": "Energy", "current_price": 2800},
            {"symbol": "HDFCBANK", "sector": "Banking", "current_price": 1650}
        ]
    
    cursor = db_connection.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT DISTINCT symbol, sector, close_price as current_price
            FROM historical_market_data 
            WHERE year = 2024
            ORDER BY symbol
        """)
        
        stocks = cursor.fetchall()
        return stocks if stocks else [
            {"symbol": "TCS", "sector": "IT", "current_price": 3500},
            {"symbol": "RELIANCE", "sector": "Energy", "current_price": 2800}
        ]
    except Exception as e:
        logger.error(f"Get stocks error: {e}")
        return [{"symbol": "TCS", "sector": "IT", "current_price": 3500}]
    finally:
        cursor.close()

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
            "Real-time Market Events"
        ]
    }

#!/usr/bin/env python3
"""
Enhanced FastAPI Backend for Paisabuddy
Comprehensive API with trading simulation, AI, social features, and analytics
"""

from fastapi import FastAPI, HTTPException, Depends, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
import mysql.connector
from datetime import datetime, timedelta, date
import logging
import json
import hashlib
import sys
import os

# Add parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our custom modules
from enhanced_database import EnhancedPaisabuddyDB
from trading_simulator import create_trading_simulator
from ai_personalization import create_ai_engine
from engagement_system import create_engagement_system
from analytics_engine import create_analytics_engine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Enhanced Paisabuddy API",
    description="Comprehensive financial learning platform with AI-powered trading simulation",
    version="2.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Database connection
db = EnhancedPaisabuddyDB()
db_connection = None

# Initialize our engines
trading_sim = None
ai_engine = None
engagement_system = None
analytics_engine = None

@app.on_event("startup")
async def startup_event():
    """Initialize database connection and engines"""
    global db_connection, trading_sim, ai_engine, engagement_system, analytics_engine
    
    if db.connect():
        db_connection = db.connection
        
        # Initialize all engines
        trading_sim = create_trading_simulator(db_connection)
        ai_engine = create_ai_engine(db_connection)
        engagement_system = create_engagement_system(db_connection)
        analytics_engine = create_analytics_engine(db_connection)
        
        logger.info("Enhanced Paisabuddy API started successfully!")
    else:
        logger.error("Failed to connect to database!")

# Pydantic models for request/response
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class TradingSimulationCreate(BaseModel):
    simulation_type: str = Field(..., regex="^(intraday|longterm)$")
    simulation_name: str
    start_year: Optional[int] = None
    settings: Optional[Dict] = None

class TradeRequest(BaseModel):
    simulation_id: int
    transaction_type: str = Field(..., regex="^(buy|sell)$")
    symbol: str
    quantity: int
    notes: Optional[str] = None

class SocialPostCreate(BaseModel):
    title: str
    content: str
    post_type: str = Field(default="question", regex="^(question|strategy|success_story|tip|news)$")
    tags: Optional[List[str]] = []

class CompetitionCreate(BaseModel):
    name: str
    description: str
    start_date: date
    end_date: date
    competition_type: str = Field(default="monthly", regex="^(monthly|weekly|event_based|challenge)$")
    prize_pool: Optional[Dict] = None
    rules: Optional[Dict] = None

# Authentication helper functions
def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current user from token (simplified for demo)"""
    # In production, implement proper JWT token validation
    # For now, we'll use a simple token = user_id approach
    try:
        user_id = int(token)
        return user_id
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Authentication endpoints
@app.post("/auth/register")
async def register_user(user: UserCreate):
    """Register a new user"""
    cursor = db_connection.cursor()
    
    try:
        # Check if user exists
        cursor.execute("SELECT id FROM users WHERE email = %s OR username = %s", 
                      (user.email, user.username))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="User already exists")
        
        # Create new user
        hashed_password = hash_password(user.password)
        cursor.execute("""
            INSERT INTO users (username, email, password) VALUES (%s, %s, %s)
        """, (user.username, user.email, hashed_password))
        
        user_id = cursor.lastrowid
        db_connection.commit()
        
        return {"message": "User registered successfully", "user_id": user_id}
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")
    finally:
        cursor.close()

@app.post("/auth/login")
async def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    """User login"""
    cursor = db_connection.cursor()
    
    try:
        hashed_password = hash_password(form_data.password)
        cursor.execute("""
            SELECT id, username FROM users 
            WHERE username = %s AND password = %s
        """, (form_data.username, hashed_password))
        
        user = cursor.fetchone()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
        
        # Return user_id as token (in production, use proper JWT)
        return {"access_token": str(user[0]), "token_type": "bearer"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")
    finally:
        cursor.close()

# Trading Simulation Endpoints
@app.post("/trading/create-simulation")
async def create_simulation(
    simulation: TradingSimulationCreate,
    current_user: int = Depends(get_current_user)
):
    """Create a new trading simulation"""
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
    try:
        result = trading_sim.execute_trade(
            simulation_id=trade.simulation_id,
            transaction_type=trade.transaction_type,
            symbol=trade.symbol,
            quantity=trade.quantity,
            notes=trade.notes
        )
        
        if result['success']:
            # Check for achievements after trade
            await check_achievements(current_user)
            
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

@app.post("/trading/pause-simulation/{simulation_id}")
async def pause_simulation(
    simulation_id: int,
    current_user: int = Depends(get_current_user)
):
    """Pause a trading simulation"""
    try:
        trading_sim.pause_simulation(simulation_id)
        return {"message": "Simulation paused"}
        
    except Exception as e:
        logger.error(f"Pause simulation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/trading/resume-simulation/{simulation_id}")
async def resume_simulation(
    simulation_id: int,
    current_user: int = Depends(get_current_user)
):
    """Resume a paused simulation"""
    try:
        trading_sim.resume_simulation(simulation_id)
        return {"message": "Simulation resumed"}
        
    except Exception as e:
        logger.error(f"Resume simulation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# AI & Personalization Endpoints
@app.get("/ai/behavioral-analysis")
async def get_behavioral_analysis(current_user: int = Depends(get_current_user)):
    """Get AI behavioral analysis for user"""
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
    try:
        posts = engagement_system.get_community_feed(current_user, limit)
        return posts
        
    except Exception as e:
        logger.error(f"Get community feed error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Achievement & Engagement Endpoints
@app.get("/achievements/user-achievements")
async def get_user_achievements(current_user: int = Depends(get_current_user)):
    """Get user's achievements and statistics"""
    try:
        achievements = engagement_system.get_user_achievements(current_user)
        return achievements
        
    except Exception as e:
        logger.error(f"Get achievements error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/achievements/check")
async def check_achievements(current_user: int = Depends(get_current_user)):
    """Check and award new achievements"""
    try:
        new_achievements = engagement_system.check_and_award_achievements(current_user)
        return {"new_achievements": new_achievements}
        
    except Exception as e:
        logger.error(f"Check achievements error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Leaderboard Endpoints
@app.get("/leaderboard/{leaderboard_type}")
async def get_leaderboard(
    leaderboard_type: str,
    current_user: int = Depends(get_current_user)
):
    """Get various types of leaderboards"""
    try:
        leaderboard = engagement_system.create_leaderboard(leaderboard_type)
        return leaderboard
        
    except Exception as e:
        logger.error(f"Get leaderboard error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Competition Endpoints
@app.post("/competitions/create")
async def create_competition(
    competition: CompetitionCreate,
    current_user: int = Depends(get_current_user)  # Only admin should create competitions in production
):
    """Create a new trading competition"""
    try:
        competition_id = engagement_system.create_trading_competition(
            name=competition.name,
            description=competition.description,
            start_date=competition.start_date,
            end_date=competition.end_date,
            competition_type=competition.competition_type,
            prize_pool=competition.prize_pool,
            rules=competition.rules
        )
        
        if competition_id:
            return {"competition_id": competition_id, "message": "Competition created successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to create competition")
            
    except Exception as e:
        logger.error(f"Create competition error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/competitions/active")
async def get_active_competitions():
    """Get list of active competitions"""
    try:
        competitions = engagement_system.get_active_competitions()
        return competitions
        
    except Exception as e:
        logger.error(f"Get competitions error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/competitions/{competition_id}/join")
async def join_competition(
    competition_id: int,
    current_user: int = Depends(get_current_user)
):
    """Join a trading competition"""
    try:
        success = engagement_system.join_competition(current_user, competition_id)
        if success:
            return {"message": "Successfully joined competition"}
        else:
            raise HTTPException(status_code=400, detail="Failed to join competition")
            
    except Exception as e:
        logger.error(f"Join competition error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/competitions/{competition_id}/leaderboard")
async def get_competition_leaderboard(competition_id: int):
    """Get leaderboard for specific competition"""
    try:
        leaderboard = engagement_system.get_competition_leaderboard(competition_id)
        return leaderboard
        
    except Exception as e:
        logger.error(f"Get competition leaderboard error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Analytics Endpoints
@app.get("/analytics/portfolio/{simulation_id}")
async def get_portfolio_analytics(
    simulation_id: int,
    current_user: int = Depends(get_current_user)
):
    """Get comprehensive portfolio analytics"""
    try:
        analytics = analytics_engine.generate_portfolio_analytics(current_user, simulation_id)
        return analytics
        
    except Exception as e:
        logger.error(f"Get portfolio analytics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/decision-analysis/{simulation_id}")
async def get_decision_analysis(
    simulation_id: int,
    current_user: int = Depends(get_current_user)
):
    """Get trading decision analysis"""
    try:
        analysis = analytics_engine.generate_decision_analysis(current_user, simulation_id)
        return analysis
        
    except Exception as e:
        logger.error(f"Get decision analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/user-summary")
async def get_user_analytics_summary(current_user: int = Depends(get_current_user)):
    """Get comprehensive analytics summary for user dashboard"""
    try:
        summary = analytics_engine.get_user_analytics_summary(current_user)
        return summary
        
    except Exception as e:
        logger.error(f"Get analytics summary error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Dashboard Endpoints
@app.get("/dashboard/overview")
async def get_dashboard_overview(current_user: int = Depends(get_current_user)):
    """Get comprehensive dashboard overview"""
    try:
        # Get data from all systems
        achievements = engagement_system.get_user_achievements(current_user)
        stats_summary = engagement_system.get_user_stats_summary(current_user)
        analytics_summary = analytics_engine.get_user_analytics_summary(current_user)
        behavioral_analysis = ai_engine.analyze_user_behavior(current_user, days_back=30)
        
        dashboard = {
            "user_stats": stats_summary,
            "achievements": {
                "total_earned": achievements.get("total_earned", 0),
                "total_points": achievements.get("total_points", 0),
                "recent_achievements": achievements.get("recent_achievements", [])
            },
            "performance": analytics_summary.get("overall_metrics", {}),
            "ai_insights": {
                "personality": behavioral_analysis.get("personality_insights", {}),
                "recommendations": behavioral_analysis.get("recommendations", [])[:3]
            }
        }
        
        return dashboard
        
    except Exception as e:
        logger.error(f"Get dashboard error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Market Data Endpoints
@app.get("/market/stocks")
async def get_available_stocks():
    """Get list of available stocks for trading"""
    cursor = db_connection.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT DISTINCT symbol, sector, close_price as current_price
            FROM historical_market_data 
            WHERE year = 2024
            ORDER BY symbol
        """)
        
        stocks = cursor.fetchall()
        return stocks
        
    except Exception as e:
        logger.error(f"Get stocks error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()

@app.get("/market/stock-info/{symbol}")
async def get_stock_info(symbol: str):
    """Get detailed information about a specific stock"""
    cursor = db_connection.cursor(dictionary=True)
    
    try:
        # Get latest price and historical data
        cursor.execute("""
            SELECT * FROM historical_market_data 
            WHERE symbol = %s 
            ORDER BY year DESC 
            LIMIT 10
        """, (symbol,))
        
        stock_data = cursor.fetchall()
        if not stock_data:
            raise HTTPException(status_code=404, detail="Stock not found")
        
        return {
            "symbol": symbol,
            "current_price": stock_data[0]["close_price"],
            "sector": stock_data[0]["sector"],
            "historical_data": stock_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get stock info error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
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

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Enhanced Paisabuddy API",
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
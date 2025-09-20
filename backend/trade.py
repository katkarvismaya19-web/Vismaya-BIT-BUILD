# backend/trade.py
from fastapi import APIRouter, Depends, HTTPException, status
import database
import mysql.connector
import requests
import random
from datetime import datetime, timedelta
from typing import Dict, List
from pydantic import BaseModel
from auth import get_current_user, User

router = APIRouter()

# Pydantic models for request/response
class TradeRequest(BaseModel):
    symbol: str
    quantity: int
    price: float = None  # Optional, will use current price if not provided

class StockInfo(BaseModel):
    symbol: str
    name: str
    current_price: float
    change_percent: float
    sector: str

# Stock market data simulation
STOCK_DATA = {
    "RELIANCE": {"name": "Reliance Industries", "base_price": 2500, "sector": "Energy & Petrochemicals"},
    "TCS": {"name": "Tata Consultancy Services", "base_price": 3200, "sector": "Information Technology"},
    "HDFCBANK": {"name": "HDFC Bank", "base_price": 1600, "sector": "Banking"},
    "INFY": {"name": "Infosys", "base_price": 1400, "sector": "Information Technology"},
    "ICICIBANK": {"name": "ICICI Bank", "base_price": 950, "sector": "Banking"},
    "SBIN": {"name": "State Bank of India", "base_price": 520, "sector": "Banking"},
    "AXISBANK": {"name": "Axis Bank", "base_price": 1100, "sector": "Banking"},
    "BAJFINANCE": {"name": "Bajaj Finance", "base_price": 6800, "sector": "Financial Services"},
    "TATAMOTORS": {"name": "Tata Motors", "base_price": 650, "sector": "Automotive"},
    "WIPRO": {"name": "Wipro", "base_price": 400, "sector": "Information Technology"},
    "MARUTI": {"name": "Maruti Suzuki", "base_price": 9500, "sector": "Automotive"},
    "HINDUNILVR": {"name": "Hindustan Unilever", "base_price": 2400, "sector": "FMCG"}
}

def get_current_stock_price(symbol: str) -> float:
    """Simulate real-time stock prices with random fluctuations"""
    if symbol not in STOCK_DATA:
        raise HTTPException(status_code=404, detail=f"Stock {symbol} not found")
    
    base_price = STOCK_DATA[symbol]["base_price"]
    # Simulate price movement between -5% to +5%
    fluctuation = random.uniform(-0.05, 0.05)
    current_price = base_price * (1 + fluctuation)
    return round(current_price, 2)

def get_price_change_percent(symbol: str, current_price: float) -> float:
    """Calculate price change percentage from base price"""
    base_price = STOCK_DATA[symbol]["base_price"]
    change_percent = ((current_price - base_price) / base_price) * 100
    return round(change_percent, 2)

def get_all_stocks() -> List[StockInfo]:
    """Get all available stocks with current prices"""
    stocks = []
    for symbol, data in STOCK_DATA.items():
        current_price = get_current_stock_price(symbol)
        change_percent = get_price_change_percent(symbol, current_price)
        stocks.append(StockInfo(
            symbol=symbol,
            name=data["name"],
            current_price=current_price,
            change_percent=change_percent,
            sector=data["sector"]
        ))
    return stocks

def get_user_from_db(user_id: int):
    conn = database.get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT balance FROM Users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    if not user:
        # Create user with default balance
        cursor.execute("INSERT INTO Users (id, balance) VALUES (%s, %s)", (user_id, 100000))
        conn.commit()
        balance = 100000
    else:
        balance = user['balance']
    # Get portfolio with current market values
    cursor.execute("SELECT symbol, quantity FROM Portfolio WHERE user_id = %s AND quantity > 0", (user_id,))
    portfolio_data = cursor.fetchall()
    portfolio = {}
    total_portfolio_value = 0
    
    for row in portfolio_data:
        symbol = row['symbol']
        quantity = row['quantity']
        current_price = get_current_stock_price(symbol)
        market_value = quantity * current_price
        total_portfolio_value += market_value
        
        portfolio[symbol] = {
            'quantity': quantity,
            'current_price': current_price,
            'market_value': market_value
        }
    
    cursor.close()
    conn.close()
    return {
        'balance': float(balance), 
        'portfolio': portfolio, 
        'total_portfolio_value': total_portfolio_value,
        'total_value': float(balance) + total_portfolio_value
    }

# --- API Endpoints ---
@router.post("/buy")
def buy_stock(trade_request: TradeRequest, current_user: User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user_id = current_user.id
    symbol = trade_request.symbol
    quantity = trade_request.quantity
    
    # Get current stock price
    current_price = get_current_stock_price(symbol)
    price = trade_request.price or current_price
    cost = price * quantity
    
    conn = database.get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT balance FROM Users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            # Create new user with default balance
            cursor.execute("INSERT INTO Users (id, balance) VALUES (%s, %s)", (user_id, 100000))
            conn.commit()
            balance = 100000
        else:
            balance = user[0]
            
        if balance < cost:
            raise HTTPException(status_code=400, detail="Insufficient balance")
        
        # Deduct balance
        cursor.execute("UPDATE Users SET balance = balance - %s WHERE id = %s", (cost, user_id))
        
        # Update/Add portfolio
        cursor.execute("SELECT quantity FROM Portfolio WHERE user_id = %s AND symbol = %s", (user_id, symbol))
        row = cursor.fetchone()
        
        if row:
            cursor.execute("UPDATE Portfolio SET quantity = quantity + %s WHERE user_id = %s AND symbol = %s", (quantity, user_id, symbol))
        else:
            cursor.execute("INSERT INTO Portfolio (user_id, symbol, quantity) VALUES (%s, %s, %s)", (user_id, symbol, quantity))
        
        # Add to trade history
        cursor.execute(
            "INSERT INTO TradeHistory (user_id, symbol, trade_type, quantity, price, trade_date) VALUES (%s, %s, %s, %s, %s, %s)",
            (user_id, symbol, 'BUY', quantity, price, datetime.now())
        )
        
        conn.commit()
        
        return {
            "message": f"Successfully bought {quantity} shares of {symbol} at ₹{price} each",
            "transaction": {
                "type": "BUY",
                "symbol": symbol,
                "quantity": quantity,
                "price": price,
                "total_cost": cost,
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.post("/sell")
def sell_stock(trade_request: TradeRequest, current_user: User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user_id = current_user.id
    symbol = trade_request.symbol
    quantity = trade_request.quantity
    
    # Get current stock price
    current_price = get_current_stock_price(symbol)
    price = trade_request.price or current_price
    sale_value = price * quantity
    
    conn = database.get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT quantity FROM Portfolio WHERE user_id = %s AND symbol = %s", (user_id, symbol))
        row = cursor.fetchone()
        
        if not row or row[0] < quantity:
            raise HTTPException(status_code=400, detail="Not enough shares to sell")
        
        # Update portfolio
        new_quantity = row[0] - quantity
        if new_quantity == 0:
            cursor.execute("DELETE FROM Portfolio WHERE user_id = %s AND symbol = %s", (user_id, symbol))
        else:
            cursor.execute("UPDATE Portfolio SET quantity = %s WHERE user_id = %s AND symbol = %s", (new_quantity, user_id, symbol))
        
        # Add balance
        cursor.execute("UPDATE Users SET balance = balance + %s WHERE id = %s", (sale_value, user_id))
        
        # Add to trade history
        cursor.execute(
            "INSERT INTO TradeHistory (user_id, symbol, trade_type, quantity, price, trade_date) VALUES (%s, %s, %s, %s, %s, %s)",
            (user_id, symbol, 'SELL', quantity, price, datetime.now())
        )
        
        conn.commit()
        
        return {
            "message": f"Successfully sold {quantity} shares of {symbol} at ₹{price} each",
            "transaction": {
                "type": "SELL",
                "symbol": symbol,
                "quantity": quantity,
                "price": price,
                "total_value": sale_value,
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.get("/portfolio")
def get_portfolio(current_user: User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user_id = current_user.id
    user_data = get_user_from_db(user_id)
    return {
        "balance": user_data["balance"],
        "portfolio": user_data["portfolio"],
        "total_portfolio_value": user_data["total_portfolio_value"],
        "total_value": user_data["total_value"],
        "profit_loss": user_data["total_value"] - 100000  # Assuming 100k starting balance
    }

# --- Stock Data Endpoints ---
@router.get("/stocks")
def get_stocks():
    """Get all available stocks with current prices"""
    return get_all_stocks()

@router.get("/stocks/{symbol}")
def get_stock_price(symbol: str):
    """Get current price for a specific stock"""
    if symbol not in STOCK_DATA:
        raise HTTPException(status_code=404, detail=f"Stock {symbol} not found")
    
    current_price = get_current_stock_price(symbol)
    change_percent = get_price_change_percent(symbol, current_price)
    
    return StockInfo(
        symbol=symbol,
        name=STOCK_DATA[symbol]["name"],
        current_price=current_price,
        change_percent=change_percent,
        sector=STOCK_DATA[symbol]["sector"]
    )

@router.get("/trade-history")
def get_trade_history(current_user: User = Depends(get_current_user), limit: int = 50):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user_id = current_user.id
    """Get user's trade history"""
    conn = database.get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute(
            """SELECT symbol, trade_type, quantity, price, trade_date 
               FROM TradeHistory 
               WHERE user_id = %s 
               ORDER BY trade_date DESC 
               LIMIT %s""",
            (user_id, limit)
        )
        
        trades = cursor.fetchall()
        
        # Convert datetime objects to strings for JSON serialization
        for trade in trades:
            if 'trade_date' in trade and trade['trade_date']:
                trade['trade_date'] = trade['trade_date'].isoformat()
        
        return {"trades": trades}
        
    finally:
        cursor.close()
        conn.close()

@router.get("/market-summary")
def get_market_summary():
    """Get overall market summary"""
    stocks = get_all_stocks()
    positive_stocks = [s for s in stocks if s.change_percent > 0]
    negative_stocks = [s for s in stocks if s.change_percent < 0]
    
    return {
        "total_stocks": len(stocks),
        "gainers": len(positive_stocks),
        "losers": len(negative_stocks),
        "top_gainer": max(stocks, key=lambda x: x.change_percent),
        "top_loser": min(stocks, key=lambda x: x.change_percent)
    }

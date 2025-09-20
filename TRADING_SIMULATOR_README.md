# Virtual Trading Simulator - Setup Guide

## Overview
This is a complete virtual trading simulator integrated into your PaisaBuddy platform. Users can trade stocks with virtual money, track their portfolio performance, and learn about investing in a risk-free environment.

## Features
- **Real-time Stock Trading**: Buy and sell stocks with simulated price fluctuations
- **Portfolio Management**: Track your investments and portfolio value
- **Trade History**: View all your past transactions
- **Session-based Authentication**: Secure user sessions
- **Responsive Design**: Works on desktop and mobile devices
- **Auto-refresh**: Real-time price updates every 30 seconds

## Setup Instructions

### 1. Database Setup

First, run the database update script to create the required tables:

```sql
-- Run this in your MySQL database
source database_updates.sql;
```

Or manually execute the SQL commands in `database_updates.sql` to create:
- Updated Users table with balance column
- Portfolio table for tracking user holdings
- TradeHistory table for transaction records
- Stocks table with sample stock data
- UserSessions table for authentication

### 2. Backend Setup

The backend is built with FastAPI and includes several new modules:

#### Key Files:
- `backend/trade.py` - Trading API endpoints
- `backend/auth.py` - Authentication system
- `backend/main.py` - Main FastAPI application
- `backend/database.py` - Database connection

#### Install Dependencies:
```bash
pip install fastapi uvicorn mysql-connector-python python-multipart
```

#### Start the Backend Server:
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

### 3. Frontend Integration

The trading simulator is integrated into `frontend/portfolio.html`:

#### Key Features:
- Dynamic stock loading from backend
- Real-time portfolio updates
- Interactive trading modal
- Trade history display
- Session-based authentication

#### To Access:
1. Open `frontend/portfolio.html` in a web browser
2. Click "Demo Login" to create a test user
3. Start trading with virtual money!

### 4. API Endpoints

#### Authentication Endpoints (`/api/auth/`)
- `POST /api/auth/login` - User login
- `GET /api/auth/demo-login/{username}` - Quick demo login
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/logout` - User logout

#### Trading Endpoints (`/api/trade/`)
- `GET /api/trade/stocks` - Get all available stocks with current prices
- `GET /api/trade/stocks/{symbol}` - Get specific stock info
- `POST /api/trade/buy` - Buy stocks
- `POST /api/trade/sell` - Sell stocks
- `GET /api/trade/portfolio` - Get user's portfolio
- `GET /api/trade/trade-history` - Get user's trade history
- `GET /api/trade/market-summary` - Get market overview

### 5. Database Schema

#### Users Table (Updated)
```sql
ALTER TABLE Users ADD COLUMN balance DECIMAL(15,2) DEFAULT 100000.00;
```

#### New Tables Created:
- **Portfolio**: User stock holdings
- **TradeHistory**: All buy/sell transactions  
- **Stocks**: Available stocks with price data
- **UserSessions**: User authentication sessions

### 6. Sample Stock Data

The system includes these Indian stocks:
- Reliance Industries (RELIANCE)
- Tata Consultancy Services (TCS) 
- HDFC Bank (HDFCBANK)
- Infosys (INFY)
- ICICI Bank (ICICIBANK)
- State Bank of India (SBIN)
- Axis Bank (AXISBANK)
- Bajaj Finance (BAJFINANCE)
- Tata Motors (TATAMOTORS)
- Wipro (WIPRO)
- Maruti Suzuki (MARUTI)
- Hindustan Unilever (HINDUNILVR)

## Usage Instructions

### For Users:
1. **Login**: Click "Demo Login" or create an account
2. **Browse Stocks**: View available stocks with real-time prices
3. **Place Orders**: Click Buy/Sell buttons to trade
4. **Track Portfolio**: Monitor your investments and P&L
5. **View History**: See all your past transactions

### For Developers:
1. **Add New Stocks**: Update `STOCK_DATA` in `backend/trade.py`
2. **Modify UI**: Edit `frontend/portfolio.html` 
3. **Add Features**: Extend API endpoints in respective modules
4. **Database Changes**: Update schema as needed

## Security Features

- Session-based authentication with secure tokens
- CORS protection configured for development
- SQL injection protection with parameterized queries
- Input validation on all endpoints

## Testing

1. **Start Backend**: `uvicorn main:app --reload`
2. **Open Frontend**: Load `portfolio.html` in browser
3. **Demo Login**: Use "demo" or any username
4. **Test Trading**: Try buying and selling stocks
5. **Check Database**: Verify transactions are recorded

## Troubleshooting

### Common Issues:

1. **CORS Errors**: Ensure backend CORS settings allow your frontend origin
2. **Database Connection**: Check MySQL credentials in `database.py`
3. **Port Conflicts**: Backend runs on 8000, ensure it's available
4. **Authentication**: Clear cookies if login issues persist

### Error Messages:
- "Authentication required" - User needs to log in
- "Insufficient balance" - User doesn't have enough virtual money
- "Not enough shares to sell" - User trying to sell more than owned

## Production Deployment

For production deployment:
1. Update CORS settings to specific domains
2. Use environment variables for database credentials
3. Enable HTTPS and secure cookie settings
4. Add rate limiting to prevent abuse
5. Implement proper logging and monitoring

## Contact

For questions or issues with the trading simulator, please refer to the main PaisaBuddy documentation or contact the development team.

---

**Happy Trading! 📈💰**
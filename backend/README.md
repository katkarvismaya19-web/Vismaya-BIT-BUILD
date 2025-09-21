# Enhanced PaisaBuddy Backend with Gemini AI Integration

This is the enhanced backend for PaisaBuddy, a comprehensive financial learning platform that combines trading simulation with AI-powered insights and dynamic market data.

## New Features Added

### 🤖 Gemini AI Integration
- **Real-time Stock Analysis**: AI-powered analysis of individual stocks using Google's Gemini API
- **Dynamic Market Data**: Continuously updated stock prices with realistic fluctuations
- **Market News Generation**: AI-generated market news and sector insights
- **Personalized Trading Insights**: Portfolio-specific recommendations and risk analysis
- **Stock Recommendations**: AI-driven stock suggestions based on market analysis

### 📊 Unified Portfolio Management
- **Dynamic Portfolios**: Real-time portfolio updates synchronized with trading activity
- **Portfolio Templates**: Pre-built portfolio strategies (Conservative, Aggressive, Balanced)
- **Advanced Analytics**: Comprehensive portfolio metrics and performance tracking
- **Sector Allocation**: Automatic calculation of sector-wise investment distribution
- **Trade History**: Complete tracking of all trading activities

### 🚀 Enhanced API Endpoints
- **Market Data**: `/market/stocks`, `/market/stock-details/{symbol}`, `/market/news`
- **AI Analysis**: `/api/ai/analysis/{symbol}`, `/api/ai/insights`
- **Portfolio**: `/api/portfolio`, `/api/portfolio/templates`, `/api/portfolio/analysis`
- **Trading**: Enhanced `/trading/execute-trade` with portfolio synchronization

## Setup Instructions

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Environment Configuration
Copy the example environment file and configure your settings:
```bash
cp .env.example .env
```

Edit `.env` file and set your configuration:
```env
# Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Database Configuration
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=paisabuddy_enhanced
```

### 3. Get Gemini API Key
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file as `GEMINI_API_KEY`

### 4. Start the Server
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- Alternative Docs: `http://localhost:8000/redoc`

## API Overview

### Market Data Endpoints

#### GET `/market/stocks`
Get list of available stocks with dynamic pricing
```json
{
  "status": "success",
  "stocks": [
    {
      "symbol": "TCS",
      "name": "Tata Consultancy Services",
      "sector": "IT",
      "current_price": 3542.75,
      "change_percent": 2.3,
      "volume": 2500000,
      "market_cap": 12850000000
    }
  ]
}
```

#### GET `/market/stock-details/{symbol}`
Get detailed stock information with AI analysis
```json
{
  "stock_data": {
    "symbol": "TCS",
    "current_price": 3542.75,
    "change_percent": 2.3
  },
  "ai_analysis": {
    "sentiment": "positive",
    "recommendation": "BUY",
    "target_price": 3800,
    "confidence": 0.82,
    "risk_level": "low"
  }
}
```

#### GET `/market/news`
Get AI-generated market news
```json
{
  "status": "success",
  "news": [
    {
      "headline": "IT Sector Shows Strong Q3 Results",
      "description": "Major IT companies report better earnings",
      "sector": "IT",
      "impact": "positive",
      "relevance": "high"
    }
  ]
}
```

### AI Analysis Endpoints

#### GET `/api/ai/analysis/{stock_symbol}`
Get AI analysis for a specific stock
```json
{
  "status": "success",
  "analysis": {
    "symbol": "TCS",
    "sentiment": "positive",
    "technical_indicators": {
      "trend": "bullish",
      "rsi": 62,
      "support": 3400,
      "resistance": 3650
    },
    "recommendation": "BUY",
    "confidence": 0.82,
    "key_factors": [
      "Strong Q3 earnings growth",
      "Digital transformation deals",
      "Client addition"
    ]
  }
}
```

#### GET `/api/ai/insights`
Get personalized AI insights and market overview
```json
{
  "status": "success",
  "insights": {
    "market_news": [...],
    "trading_insights": {
      "portfolio_health": "good",
      "risk_assessment": "moderate",
      "recommendations": [...]
    },
    "market_outlook": {
      "sentiment": "cautiously optimistic"
    }
  }
}
```

### Portfolio Endpoints

#### GET `/api/portfolio`
Get user's portfolio with real-time data
```json
{
  "status": "success",
  "portfolio": {
    "portfolio_id": 1,
    "name": "My Portfolio",
    "holdings": [
      {
        "symbol": "TCS",
        "quantity": 5,
        "current_price": 3500,
        "profit_loss": 250,
        "profit_loss_percent": 1.45
      }
    ],
    "metrics": {
      "total_invested": 50000,
      "current_value": 51250,
      "total_return_percent": 2.5,
      "sector_allocation": {
        "IT": 45.0,
        "Banking": 35.0,
        "Energy": 20.0
      }
    }
  }
}
```

#### GET `/api/portfolio/templates`
Get available portfolio templates
```json
{
  "status": "success",
  "templates": [
    {
      "id": 1,
      "name": "Conservative Growth",
      "risk_level": "low",
      "allocation": {
        "Banking": 40,
        "IT": 25,
        "FMCG": 20,
        "Healthcare": 15
      }
    }
  ]
}
```

#### POST `/api/portfolio/create`
Create portfolio from template
```json
{
  "template_id": 1,
  "initial_balance": 100000
}
```

#### GET `/api/portfolio/analysis`
Get comprehensive portfolio analysis
```json
{
  "status": "success",
  "portfolio_analysis": {
    "portfolio_metrics": {...},
    "ai_insights": {...},
    "stock_analyses": {...},
    "recommendations": [...],
    "risk_assessment": "moderate",
    "diversification_score": 75
  }
}
```

### Trading Endpoints

#### POST `/trading/execute-trade`
Execute buy/sell trade and update portfolio
```json
{
  "simulation_id": 1,
  "transaction_type": "buy",
  "symbol": "TCS",
  "quantity": 5,
  "notes": "Investment based on AI analysis"
}
```

Response:
```json
{
  "success": true,
  "trade_id": 1234,
  "execution_price": 3500.00,
  "total_value": 17500.00,
  "portfolio_balance": 82500.00,
  "status": "completed"
}
```

## Key Features

### 🎯 AI-Powered Analysis
- Stock sentiment analysis using Gemini API
- Technical indicators and recommendations
- Market news generation and analysis
- Risk assessment and confidence scoring

### 📈 Dynamic Market Data
- Real-time price updates with realistic fluctuations
- Volume and market cap calculations
- Sector-wise performance tracking
- Historical price simulation

### 💼 Advanced Portfolio Management
- Real-time portfolio synchronization with trades
- Multiple portfolio support per user
- Template-based portfolio creation
- Comprehensive performance metrics
- Sector allocation and diversification analysis

### 🔄 Unified Trading Experience
- Seamless integration between trading and portfolio
- Real-time balance updates
- Complete trade history tracking
- Achievement system integration

## Architecture

### Services
- **GeminiMarketService**: Handles Gemini API integration for AI analysis and market data
- **PortfolioService**: Manages dynamic portfolios and trading synchronization
- **Enhanced Trading Engine**: Improved trading with portfolio integration

### Data Flow
1. **Market Data**: Gemini service generates dynamic stock prices
2. **AI Analysis**: Real-time analysis using Gemini API
3. **Trading**: Executes trades and updates portfolios
4. **Portfolio**: Syncs with market data for real-time valuation

## Error Handling

The API includes comprehensive error handling with graceful fallbacks:
- Gemini API failures fall back to mock data
- Database connection issues use in-memory storage
- Network timeouts return cached responses
- Invalid requests return meaningful error messages

## Performance Optimization

- **Caching**: Stock analysis and market data caching
- **Batch Processing**: Multiple stock analysis in parallel
- **Lazy Loading**: Dynamic data loading only when requested
- **Connection Pooling**: Efficient API connection management

## Security

- **API Key Management**: Secure Gemini API key handling
- **Input Validation**: Comprehensive request validation
- **Error Sanitization**: Safe error message handling
- **CORS Configuration**: Proper cross-origin request handling

## Development

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/
```

### Code Quality
```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

## Production Deployment

### Docker Setup
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables
Ensure all required environment variables are set:
- `GEMINI_API_KEY`: Your Gemini API key
- `DB_HOST`, `DB_USER`, `DB_PASSWORD`: Database configuration
- `SECRET_KEY`: Application security key

### Health Monitoring
The API includes a health check endpoint at `/health` that monitors:
- Database connection status
- Gemini API connectivity
- Service availability
- System resource usage

## Troubleshooting

### Common Issues

1. **Gemini API Errors**
   - Check API key validity
   - Verify quota limits
   - Check network connectivity

2. **Portfolio Sync Issues**
   - Verify trade data structure
   - Check portfolio service initialization
   - Review error logs for details

3. **Database Connection**
   - Verify database credentials
   - Check database server status
   - Review connection string format

### Logs
Enable debug logging by setting `LOG_LEVEL=DEBUG` in your `.env` file.

## Support

For technical support or feature requests, please refer to the project documentation or create an issue in the project repository.
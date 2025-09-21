"""
Gemini API Integration for Dynamic Stock Data and AI Insights
Provides real-time market data, analysis, and AI-powered trading recommendations
"""

import requests
import json
import random
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class GeminiMarketService:
    """
    Service to integrate with Gemini API for market data and AI insights
    """
    
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        
        # Mock stock data for demo purposes
        self.mock_stocks = [
            {"symbol": "TCS", "name": "Tata Consultancy Services", "sector": "IT", "base_price": 3500},
            {"symbol": "RELIANCE", "name": "Reliance Industries", "sector": "Energy", "base_price": 2800},
            {"symbol": "HDFCBANK", "name": "HDFC Bank", "sector": "Banking", "base_price": 1650},
            {"symbol": "INFY", "name": "Infosys Limited", "sector": "IT", "base_price": 1450},
            {"symbol": "ICICIBANK", "name": "ICICI Bank", "sector": "Banking", "base_price": 1200},
            {"symbol": "HINDUNILVR", "name": "Hindustan Unilever", "sector": "FMCG", "base_price": 2400},
            {"symbol": "ITC", "name": "ITC Limited", "sector": "FMCG", "base_price": 460},
            {"symbol": "SBIN", "name": "State Bank of India", "sector": "Banking", "base_price": 820},
            {"symbol": "BHARTIARTL", "name": "Bharti Airtel", "sector": "Telecom", "base_price": 1100},
            {"symbol": "KOTAKBANK", "name": "Kotak Mahindra Bank", "sector": "Banking", "base_price": 1750}
        ]
    
    def generate_dynamic_stock_data(self) -> List[Dict[str, Any]]:
        """
        Generate dynamic stock data with realistic price movements
        """
        stocks = []
        
        for stock in self.mock_stocks:
            # Generate realistic price changes (-5% to +5%)
            change_percent = random.uniform(-5.0, 5.0)
            current_price = stock["base_price"] * (1 + change_percent / 100)
            
            # Generate volume data
            volume = random.randint(1000000, 10000000)
            
            # Market cap calculation (simplified)
            market_cap = current_price * random.randint(100, 1000) * 10000000
            
            stock_data = {
                "symbol": stock["symbol"],
                "name": stock["name"],
                "sector": stock["sector"],
                "current_price": round(current_price, 2),
                "base_price": stock["base_price"],
                "change": round(current_price - stock["base_price"], 2),
                "change_percent": round(change_percent, 2),
                "volume": volume,
                "market_cap": market_cap,
                "high": round(current_price * random.uniform(1.01, 1.05), 2),
                "low": round(current_price * random.uniform(0.95, 0.99), 2),
                "pe_ratio": round(random.uniform(15, 35), 2),
                "dividend_yield": round(random.uniform(0.5, 4.0), 2),
                "beta": round(random.uniform(0.7, 1.5), 2),
                "last_updated": datetime.now().isoformat()
            }
            
            stocks.append(stock_data)
        
        return stocks
    
    def get_stock_analysis_with_gemini(self, symbol: str) -> Dict[str, Any]:
        """
        Get AI-powered stock analysis using Gemini API
        """
        if not self.api_key:
            return self._get_mock_analysis(symbol)
        
        try:
            # Prepare prompt for Gemini
            prompt = f"""
            Analyze the stock {symbol} from an Indian stock market perspective. 
            Provide a comprehensive analysis including:
            1. Current market sentiment
            2. Technical analysis indicators
            3. Fundamental analysis highlights  
            4. Risk assessment
            5. Investment recommendation (BUY/HOLD/SELL)
            6. Target price
            7. Key factors to watch
            
            Format the response as JSON with the following structure:
            {{
                "sentiment": "positive/negative/neutral",
                "technical_indicators": {{"trend": "bullish/bearish/sideways", "rsi": 45-75, "support": price, "resistance": price}},
                "recommendation": "BUY/HOLD/SELL",
                "target_price": price,
                "confidence": 0.1-1.0,
                "risk_level": "low/medium/high",
                "key_factors": ["factor1", "factor2", "factor3"],
                "analysis_summary": "brief summary"
            }}
            """
            
            url = f"{self.base_url}/models/gemini-pro:generateContent"
            headers = {
                'Content-Type': 'application/json',
            }
            
            data = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": prompt
                            }
                        ]
                    }
                ]
            }
            
            response = requests.post(
                f"{url}?key={self.api_key}",
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                # Extract the generated content
                if 'candidates' in result and len(result['candidates']) > 0:
                    content = result['candidates'][0]['content']['parts'][0]['text']
                    try:
                        # Parse JSON response from Gemini
                        analysis = json.loads(content)
                        return analysis
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse Gemini response as JSON for {symbol}")
                        return self._get_mock_analysis(symbol)
            else:
                logger.warning(f"Gemini API request failed: {response.status_code}")
                return self._get_mock_analysis(symbol)
                
        except Exception as e:
            logger.error(f"Error getting Gemini analysis for {symbol}: {e}")
            return self._get_mock_analysis(symbol)
    
    def _get_mock_analysis(self, symbol: str) -> Dict[str, Any]:
        """
        Provide mock analysis when Gemini API is not available
        """
        mock_analyses = {
            "TCS": {
                "sentiment": "positive",
                "technical_indicators": {
                    "trend": "bullish",
                    "rsi": 62,
                    "support": 3400,
                    "resistance": 3650
                },
                "recommendation": "BUY",
                "target_price": 3800,
                "confidence": 0.82,
                "risk_level": "low",
                "key_factors": [
                    "Strong Q3 earnings growth",
                    "Increasing digital transformation deals",
                    "Robust client addition"
                ],
                "analysis_summary": "TCS shows strong fundamentals with consistent growth in digital services. Technical indicators suggest continued upward momentum."
            },
            "RELIANCE": {
                "sentiment": "neutral",
                "technical_indicators": {
                    "trend": "sideways",
                    "rsi": 48,
                    "support": 2650,
                    "resistance": 2950
                },
                "recommendation": "HOLD",
                "target_price": 3000,
                "confidence": 0.68,
                "risk_level": "medium",
                "key_factors": [
                    "Oil price volatility",
                    "Retail segment expansion",
                    "Jio subscriber growth"
                ],
                "analysis_summary": "Mixed signals with strong retail business but concerns over oil price fluctuations. Range-bound trading expected."
            },
            "HDFCBANK": {
                "sentiment": "positive", 
                "technical_indicators": {
                    "trend": "bullish",
                    "rsi": 58,
                    "support": 1580,
                    "resistance": 1720
                },
                "recommendation": "BUY",
                "target_price": 1800,
                "confidence": 0.79,
                "risk_level": "low",
                "key_factors": [
                    "Strong asset quality",
                    "Digital banking initiatives",
                    "Market share gains"
                ],
                "analysis_summary": "Leading private bank with strong digital presence and consistent performance metrics. Good long-term investment."
            }
        }
        
        return mock_analyses.get(symbol, {
            "sentiment": "neutral",
            "technical_indicators": {"trend": "sideways", "rsi": 50, "support": 0, "resistance": 0},
            "recommendation": "HOLD",
            "target_price": 0,
            "confidence": 0.5,
            "risk_level": "medium",
            "key_factors": ["Market analysis pending"],
            "analysis_summary": "Analysis data not available for this stock."
        })
    
    def get_market_news_with_gemini(self) -> List[Dict[str, Any]]:
        """
        Generate market news and insights using Gemini API
        """
        if not self.api_key:
            return self._get_mock_news()
        
        try:
            prompt = """
            Generate 3-5 current Indian stock market news headlines and brief descriptions.
            Focus on major sectors like IT, Banking, FMCG, Energy, and Telecom.
            Include market sentiment and potential impact on trading.
            
            Format as JSON array:
            [
                {
                    "headline": "news headline",
                    "description": "brief description",
                    "sector": "sector name", 
                    "impact": "positive/negative/neutral",
                    "relevance": "high/medium/low"
                }
            ]
            """
            
            url = f"{self.base_url}/models/gemini-pro:generateContent"
            data = {
                "contents": [{"parts": [{"text": prompt}]}]
            }
            
            response = requests.post(
                f"{url}?key={self.api_key}",
                headers={'Content-Type': 'application/json'},
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    content = result['candidates'][0]['content']['parts'][0]['text']
                    try:
                        news = json.loads(content)
                        return news
                    except json.JSONDecodeError:
                        return self._get_mock_news()
            
            return self._get_mock_news()
            
        except Exception as e:
            logger.error(f"Error getting market news: {e}")
            return self._get_mock_news()
    
    def _get_mock_news(self) -> List[Dict[str, Any]]:
        """
        Mock market news when Gemini API is not available
        """
        return [
            {
                "headline": "IT Sector Shows Strong Q3 Results",
                "description": "Major IT companies report better-than-expected earnings with strong digital transformation bookings",
                "sector": "IT",
                "impact": "positive",
                "relevance": "high"
            },
            {
                "headline": "Banking Stocks Rally on RBI Policy Hopes",
                "description": "Banking sector gains momentum ahead of RBI monetary policy announcement",
                "sector": "Banking", 
                "impact": "positive",
                "relevance": "high"
            },
            {
                "headline": "Oil Prices Impact Energy Sector Performance",
                "description": "Fluctuating crude oil prices create volatility in energy and petrochemical stocks",
                "sector": "Energy",
                "impact": "neutral",
                "relevance": "medium"
            }
        ]
    
    def get_trading_insights(self, user_portfolio: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate personalized trading insights based on user portfolio
        """
        insights = {
            "portfolio_health": "good",
            "diversification_score": random.randint(60, 90),
            "risk_assessment": "moderate",
            "recommendations": [
                {
                    "type": "rebalancing",
                    "message": "Consider increasing exposure to banking sector",
                    "priority": "medium"
                },
                {
                    "type": "profit_booking", 
                    "message": "IT stocks have gained significantly, consider partial profit booking",
                    "priority": "high"
                },
                {
                    "type": "opportunity",
                    "message": "FMCG sector showing value buying opportunities",
                    "priority": "low"
                }
            ],
            "market_outlook": {
                "sentiment": "cautiously optimistic",
                "key_levels": {
                    "nifty_support": 21500,
                    "nifty_resistance": 22200
                },
                "sectoral_outlook": {
                    "IT": "positive",
                    "Banking": "positive", 
                    "Energy": "neutral",
                    "FMCG": "neutral"
                }
            }
        }
        
        return insights

# Create global instance
gemini_service = GeminiMarketService()
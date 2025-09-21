#!/usr/bin/env python3
"""
Integration Test Script for Enhanced PaisaBuddy Backend
Tests Gemini API integration and portfolio services
"""

import asyncio
import sys
from gemini_service import gemini_service
from portfolio_service import portfolio_service

def test_gemini_service():
    """Test Gemini API service functionality"""
    print("🤖 Testing Gemini API Service...")
    
    try:
        # Test dynamic stock data generation
        stocks = gemini_service.generate_dynamic_stock_data()
        print(f"✅ Generated {len(stocks)} dynamic stocks")
        
        if stocks:
            first_stock = stocks[0]
            print(f"   Sample: {first_stock['symbol']} - ₹{first_stock['current_price']} ({first_stock['change_percent']:+.2f}%)")
        
        # Test stock analysis
        analysis = gemini_service.get_stock_analysis_with_gemini("TCS")
        print(f"✅ Stock analysis for TCS: {analysis.get('recommendation', 'N/A')}")
        
        # Test market news
        news = gemini_service.get_market_news_with_gemini()
        print(f"✅ Generated {len(news)} market news items")
        
        # Test trading insights
        portfolio = {"holdings": []}
        insights = gemini_service.get_trading_insights(portfolio)
        print(f"✅ Trading insights: {insights.get('portfolio_health', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Gemini service test failed: {e}")
        return False

def test_portfolio_service():
    """Test portfolio service functionality"""
    print("\n💼 Testing Portfolio Service...")
    
    try:
        # Test portfolio creation
        portfolio = portfolio_service.get_user_portfolio(1)
        print(f"✅ Created portfolio for user 1: {portfolio['name']}")
        print(f"   Holdings: {len(portfolio['holdings'])} stocks")
        print(f"   Total value: ₹{portfolio['metrics']['total_portfolio_value']:,.2f}")
        
        # Test portfolio templates
        templates = portfolio_service.get_portfolio_templates()
        print(f"✅ Available templates: {len(templates)}")
        for template in templates:
            print(f"   - {template['name']} ({template['risk_level']} risk)")
        
        # Test trade execution
        trade_data = {
            "symbol": "INFY",
            "transaction_type": "buy",
            "quantity": 2,
            "execution_price": 1450,
            "fees": 25
        }
        
        success = portfolio_service.update_portfolio_with_trade(1, trade_data)
        print(f"✅ Trade execution test: {'Success' if success else 'Failed'}")
        
        # Get updated portfolio
        updated_portfolio = portfolio_service.get_user_portfolio(1)
        print(f"   Updated portfolio value: ₹{updated_portfolio['metrics']['total_portfolio_value']:,.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Portfolio service test failed: {e}")
        return False

def test_integration():
    """Test integration between services"""
    print("\n🔗 Testing Service Integration...")
    
    try:
        # Get dynamic stock data
        dynamic_stocks = gemini_service.generate_dynamic_stock_data()
        stock_prices = {stock["symbol"]: stock["current_price"] for stock in dynamic_stocks}
        
        # Get portfolio
        portfolio = portfolio_service.get_user_portfolio(1)
        
        # Update portfolio with current prices
        updated_holdings = 0
        for holding in portfolio.get("holdings", []):
            symbol = holding["symbol"]
            if symbol in stock_prices:
                old_price = holding["current_price"]
                new_price = stock_prices[symbol]
                holding["current_price"] = new_price
                print(f"   Updated {symbol}: ₹{old_price} → ₹{new_price}")
                updated_holdings += 1
        
        print(f"✅ Updated {updated_holdings} holdings with dynamic prices")
        
        # Get AI analysis for holdings
        analyses_count = 0
        for holding in portfolio.get("holdings", [])[:2]:  # Test first 2 holdings
            symbol = holding["symbol"]
            analysis = gemini_service.get_stock_analysis_with_gemini(symbol)
            print(f"   AI analysis for {symbol}: {analysis.get('recommendation', 'N/A')} (confidence: {analysis.get('confidence', 0):.0%})")
            analyses_count += 1
        
        print(f"✅ Generated AI analysis for {analyses_count} stocks")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Enhanced PaisaBuddy Backend Integration Test")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 3
    
    # Run tests
    if test_gemini_service():
        tests_passed += 1
    
    if test_portfolio_service():
        tests_passed += 1
        
    if test_integration():
        tests_passed += 1
    
    # Results
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Backend is ready for use.")
        print("\nNext steps:")
        print("1. Set up your Gemini API key in .env file")
        print("2. Start the server: uvicorn main:app --reload")
        print("3. Access API docs: http://localhost:8000/docs")
        return 0
    else:
        print("⚠️  Some tests failed. Check the error messages above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
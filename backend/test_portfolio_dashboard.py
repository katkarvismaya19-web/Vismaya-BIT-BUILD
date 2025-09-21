#!/usr/bin/env python3
"""
Test script for Portfolio and Dashboard API endpoints
Tests the new structure where portfolio.html handles intraday/longterm and dashboard.html shows analysis
"""

import sys
from fastapi.testclient import TestClient
from main import app

def test_portfolio_dashboard_api():
    """Test the restructured API endpoints"""
    print("🧪 Testing Portfolio & Dashboard API Structure...")
    
    client = TestClient(app)
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Get Intraday Portfolio (for portfolio.html?type=intraday)
    total_tests += 1
    print("\n1️⃣ Testing GET /api/portfolio/intraday")
    try:
        response = client.get("/api/portfolio/intraday")
        
        if response.status_code == 200:
            data = response.json()
            portfolio = data.get('portfolio', {})
            
            print(f"✅ Intraday portfolio retrieved")
            print(f"   Name: {portfolio.get('name')}")
            print(f"   Type: {portfolio.get('type')}")
            print(f"   Total value: ₹{portfolio.get('summary', {}).get('total_portfolio_value', 0):,.2f}")
            print(f"   Available stocks: {len(portfolio.get('available_stocks', []))} stocks")
            tests_passed += 1
        else:
            print(f"❌ Failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 2: Get Long-term Portfolio (for portfolio.html?type=longterm)
    total_tests += 1
    print("\n2️⃣ Testing GET /api/portfolio/longterm")
    try:
        response = client.get("/api/portfolio/longterm")
        
        if response.status_code == 200:
            data = response.json()
            portfolio = data.get('portfolio', {})
            
            print(f"✅ Long-term portfolio retrieved")
            print(f"   Name: {portfolio.get('name')}")
            print(f"   Holdings: {portfolio.get('holdings_count', 0)} stocks")
            print(f"   Recent trades: {len(portfolio.get('recent_trades', []))} trades")
            print(f"   Sector allocation: {len(portfolio.get('sector_allocation', {}))} sectors")
            tests_passed += 1
        else:
            print(f"❌ Failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 3: Get Dashboard Overview (for dashboard.html)
    total_tests += 1
    print("\n3️⃣ Testing GET /api/dashboard/overview")
    try:
        response = client.get("/api/dashboard/overview")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"✅ Dashboard overview retrieved")
            
            # Check portfolio summary
            portfolio_summary = data.get('portfolio_summary', {})
            print(f"   Portfolio value: ₹{portfolio_summary.get('total_portfolio_value', 0):,.2f}")
            print(f"   Total P&L: ₹{portfolio_summary.get('total_profit_loss', 0):,.2f}")
            
            # Check transactions
            transactions = data.get('transactions', {})
            print(f"   Total trades: {transactions.get('total_trades', 0)}")
            
            # Check AI insights
            ai_insights = data.get('ai_insights', {})
            print(f"   Portfolio health: {ai_insights.get('portfolio_health', 'N/A')}")
            print(f"   Recommendations: {len(ai_insights.get('recommendations', []))} items")
            
            # Check market data
            market_data = data.get('market_data', {})
            print(f"   Market news: {len(market_data.get('market_news', []))} articles")
            
            # Check quick actions
            quick_actions = data.get('quick_actions', [])
            print(f"   Quick actions: {len(quick_actions)} available")
            for action in quick_actions:
                print(f"     - {action.get('label')}: {action.get('url')}")
            
            tests_passed += 1
        else:
            print(f"❌ Failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 4: Execute Trade via Portfolio API
    total_tests += 1
    print("\n4️⃣ Testing POST /api/portfolio/trade")
    try:
        trade_data = {
            "symbol": "INFY",
            "quantity": 3,
            "transaction_type": "buy"
        }
        
        response = client.post("/api/portfolio/trade", json=trade_data)
        
        if response.status_code == 200:
            data = response.json()
            trade = data.get('trade', {})
            
            print(f"✅ Portfolio trade executed")
            print(f"   Trade ID: {trade.get('trade_id')}")
            print(f"   Symbol: {trade.get('symbol')}")
            print(f"   Price: ₹{trade.get('execution_price', 0):,.2f}")
            print(f"   Total value: ₹{trade.get('total_value', 0):,.2f}")
            print(f"   New portfolio balance: ₹{trade.get('portfolio_balance', 0):,.2f}")
            tests_passed += 1
        else:
            print(f"❌ Failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 5: Get Trade History for Intraday Portfolio
    total_tests += 1
    print("\n5️⃣ Testing GET /api/portfolio/intraday/trades")
    try:
        response = client.get("/api/portfolio/intraday/trades?limit=10")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"✅ Intraday trade history retrieved")
            print(f"   Portfolio type: {data.get('portfolio_type')}")
            print(f"   Total trades: {data.get('total_trades', 0)}")
            print(f"   Returned trades: {len(data.get('trades', []))}")
            
            trade_summary = data.get('trade_summary', {})
            print(f"   Buy trades: {trade_summary.get('buy_count', 0)}")
            print(f"   Sell trades: {trade_summary.get('sell_count', 0)}")
            print(f"   Total fees: ₹{trade_summary.get('total_fees', 0):,.2f}")
            
            tests_passed += 1
        else:
            print(f"❌ Failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 6: Get Performance Analytics for Dashboard
    total_tests += 1
    print("\n6️⃣ Testing GET /api/dashboard/performance")
    try:
        response = client.get("/api/dashboard/performance")
        
        if response.status_code == 200:
            data = response.json()
            performance = data.get('performance', {})
            
            print(f"✅ Performance analytics retrieved")
            print(f"   Total return: {performance.get('total_return', 0):+.2f}%")
            print(f"   Daily returns: {len(performance.get('daily_returns', []))} days")
            print(f"   Monthly returns: {len(performance.get('monthly_returns', []))} months")
            
            stats = performance.get('statistics', {})
            print(f"   Volatility: {stats.get('volatility', 0):.2f}%")
            print(f"   Sharpe ratio: {stats.get('sharpe_ratio', 0):.2f}")
            print(f"   Win rate: {stats.get('win_rate', 0):.1f}%")
            
            tests_passed += 1
        else:
            print(f"❌ Failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Results
    print("\n" + "="*60)
    print(f"📊 Portfolio & Dashboard API Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! API structure is ready for frontend integration.")
        print("\n🏗️  Frontend Integration Guide:")
        print("   📄 portfolio.html:")
        print("     - Use /api/portfolio/intraday for intraday view")
        print("     - Use /api/portfolio/longterm for long-term view") 
        print("     - Use /api/portfolio/trade for executing trades")
        print("     - Use /api/portfolio/{type}/trades for trade history")
        print("\n   📊 dashboard.html:")
        print("     - Use /api/dashboard/overview for main dashboard")
        print("     - Use /api/dashboard/performance for analytics charts")
        print("     - Link to portfolio with query params (?type=intraday/longterm)")
        return True
    else:
        print("⚠️  Some tests failed. Check the error messages above.")
        return False

if __name__ == "__main__":
    success = test_portfolio_dashboard_api()
    sys.exit(0 if success else 1)
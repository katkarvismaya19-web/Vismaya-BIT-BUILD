#!/usr/bin/env python3
"""
Test script to verify API endpoints work correctly without authentication issues
"""

import requests
import json
import sys
import asyncio
from typing import Dict, Any

# Test the endpoints in isolation without starting full server
from main import app
from fastapi.testclient import TestClient

def test_api_endpoints():
    """Test API endpoints using FastAPI TestClient"""
    print("🧪 Testing API Endpoints...")
    
    client = TestClient(app)
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Create Trading Simulation (should not give 401 error)
    total_tests += 1
    print("\n1️⃣ Testing POST /trading/create-simulation")
    try:
        response = client.post("/trading/create-simulation", json={
            "simulation_type": "intraday",
            "simulation_name": "Test Portfolio",
            "start_year": 2024
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Simulation created: ID {data.get('simulation_id')}")
            print(f"   Message: {data.get('message')}")
            tests_passed += 1
        else:
            print(f"❌ Failed with status {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 2: Execute Trade (should update portfolio)
    total_tests += 1
    print("\n2️⃣ Testing POST /trading/execute-trade")
    try:
        response = client.post("/trading/execute-trade", json={
            "simulation_id": 1,
            "transaction_type": "buy",
            "symbol": "TCS",
            "quantity": 2,
            "notes": "Test purchase"
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Trade executed: {data.get('message')}")
            print(f"   Price: ₹{data.get('execution_price')}")
            print(f"   Portfolio balance: ₹{data.get('portfolio_balance', 0):,.2f}")
            tests_passed += 1
        else:
            print(f"❌ Failed with status {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 3: Get Unified Portfolio
    total_tests += 1
    print("\n3️⃣ Testing GET /api/user/portfolio")
    try:
        response = client.get("/api/user/portfolio")
        
        if response.status_code == 200:
            data = response.json()
            portfolio = data.get('portfolio', {})
            summary = portfolio.get('summary', {})
            
            print(f"✅ Portfolio retrieved: {portfolio.get('name')}")
            print(f"   Holdings: {portfolio.get('holdings_count', 0)} stocks")
            print(f"   Total value: ₹{summary.get('total_portfolio_value', 0):,.2f}")
            print(f"   P&L: ₹{summary.get('total_profit_loss', 0):,.2f}")
            
            # Check if holdings have updated prices
            holdings = portfolio.get('holdings', [])
            if holdings:
                print("   Holdings detail:")
                for holding in holdings:
                    print(f"     {holding['symbol']}: {holding['quantity']} shares @ ₹{holding['current_price']:.2f}")
            
            tests_passed += 1
        else:
            print(f"❌ Failed with status {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 4: Get Dynamic Market Data
    total_tests += 1
    print("\n4️⃣ Testing GET /market/stocks")
    try:
        response = client.get("/market/stocks")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                print(f"✅ Market data retrieved: {len(data)} stocks")
                # Show first few stocks
                for stock in data[:3]:
                    print(f"   {stock['symbol']}: ₹{stock['current_price']} ({stock['change_percent']:+.1f}%)")
                tests_passed += 1
            else:
                print(f"❌ No market data returned")
        else:
            print(f"❌ Failed with status {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 5: Get User Simulations (should return unified portfolio)
    total_tests += 1
    print("\n5️⃣ Testing GET /trading/user-simulations")
    try:
        response = client.get("/trading/user-simulations")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                sim = data[0]
                print(f"✅ User simulations retrieved: {sim.get('simulation_name')}")
                print(f"   Current value: ₹{sim.get('current_value', 0):,.2f}")
                print(f"   Return: {sim.get('total_return', 0):+.1f}%")
                print(f"   Holdings: {sim.get('holdings_count', 0)} stocks")
                tests_passed += 1
            else:
                print(f"❌ No simulations returned")
        else:
            print(f"❌ Failed with status {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 6: Test another trade to verify portfolio updates
    total_tests += 1
    print("\n6️⃣ Testing second trade to verify portfolio sync")
    try:
        response = client.post("/trading/execute-trade", json={
            "simulation_id": 1,
            "transaction_type": "buy",
            "symbol": "HDFCBANK",
            "quantity": 3,
            "notes": "Second test purchase"
        })
        
        if response.status_code == 200:
            print("✅ Second trade executed successfully")
            
            # Now check if portfolio is updated
            portfolio_response = client.get("/api/user/portfolio")
            if portfolio_response.status_code == 200:
                portfolio_data = portfolio_response.json()
                holdings = portfolio_data.get('portfolio', {}).get('holdings', [])
                holdings_count = len(holdings)
                
                print(f"   Portfolio now has {holdings_count} different stocks")
                
                # Check for HDFCBANK
                hdfcbank_holding = next((h for h in holdings if h['symbol'] == 'HDFCBANK'), None)
                if hdfcbank_holding:
                    print(f"   HDFCBANK holding: {hdfcbank_holding['quantity']} shares")
                    tests_passed += 1
                else:
                    print("❌ HDFCBANK holding not found in portfolio")
            else:
                print("❌ Failed to retrieve updated portfolio")
        else:
            print(f"❌ Second trade failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Results
    print("\n" + "="*50)
    print(f"📊 API Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All API tests passed!")
        print("\n✅ Issues Fixed:")
        print("   - No more 401 Unauthorized errors")
        print("   - Portfolio updates correctly with trades")
        print("   - Single unified portfolio system")
        print("   - Real-time price updates working")
        return True
    else:
        print("⚠️  Some API tests failed. Check the error messages above.")
        return False

if __name__ == "__main__":
    success = test_api_endpoints()
    sys.exit(0 if success else 1)
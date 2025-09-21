#!/usr/bin/env python3
"""
Paisabuddy Complete System Startup Script
Installs dependencies, starts API server, and provides system information
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def print_banner():
    """Print the startup banner"""
    print("=" * 80)
    print("🎮 PAISABUDDY FINANCIAL LEARNING PLATFORM 🎮")
    print("=" * 80)
    print("Complete system with database integration, games, and web interface")
    print()

def check_python():
    """Check Python version"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print(f"❌ Python {version.major}.{version.minor} detected. Python 3.7+ required.")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible!")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    
    try:
        # Install from requirements.txt
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "games/requirements.txt"
        ])
        print("✅ All dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def check_database():
    """Check database connection"""
    print("\n🗄️ Checking database connection...")
    
    try:
        sys.path.append('games')
        from database import PaisabuddyDB
        
        db = PaisabuddyDB()
        if db.connect():
            print("✅ Database connection successful!")
            print("📊 Database tables created/verified")
            db.disconnect()
            return True
        else:
            print("❌ Database connection failed")
            return False
    except Exception as e:
        print(f"⚠️ Database check failed: {e}")
        print("💡 Make sure MySQL is running and database 'paisabuddy' exists")
        return False

def start_api_server():
    """Start the API server in background"""
    print("\n🚀 Starting API server...")
    
    try:
        # Start API server as subprocess
        api_process = subprocess.Popen([
            sys.executable, "api/game_api.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Give it time to start
        time.sleep(2)
        
        if api_process.poll() is None:
            print("✅ API server started successfully!")
            print("🌐 API available at: http://localhost:5000")
            return api_process
        else:
            print("❌ API server failed to start")
            return None
    except Exception as e:
        print(f"❌ Failed to start API server: {e}")
        return None

def show_system_info():
    """Show system information and usage instructions"""
    print("\n" + "=" * 80)
    print("📋 SYSTEM INFORMATION")
    print("=" * 80)
    
    print("\n🌐 Web Interface:")
    print("  • Main website: open frontend/index.html in browser")
    print("  • Gamified learning: frontend/gamified-learning.html")
    print("  • Budget tracker: frontend/budget-tracker.html")
    print("  • Fraud challenges: frontend/fraud-challenges.html")
    
    print("\n🎮 Pygame Games:")
    print("  • Main launcher: python games/game_launcher.py")
    print("  • Budget Balance: python games/budget_balance.py")
    print("  • Investment Garden: python games/investment_growth.py")
    print("  • Fraud Detective: python games/fraud_detection.py")
    
    print("\n📊 API Endpoints:")
    print("  • Health check: GET http://localhost:5000/api/health")
    print("  • User stats: GET http://localhost:5000/api/user/demo_user/stats")
    print("  • Leaderboard: GET http://localhost:5000/api/leaderboard")
    print("  • Record quiz: POST http://localhost:5000/api/record-quiz")
    
    print("\n🗄️ Database Integration:")
    print("  • All game progress saved to MySQL database")
    print("  • Web activity tracking enabled")
    print("  • Real-time statistics and achievements")
    print("  • Cross-platform progress synchronization")

def show_quick_start():
    """Show quick start options"""
    print("\n" + "=" * 80)
    print("🚀 QUICK START OPTIONS")
    print("=" * 80)
    
    print("\n1. 🎮 Launch Game Hub:")
    print("   python games/game_launcher.py")
    
    print("\n2. 🌐 Open Web Interface:")
    print("   Open frontend/gamified-learning.html in your browser")
    
    print("\n3. 📊 View API Documentation:")
    print("   Visit http://localhost:5000/api/health")
    
    print("\n4. 🔧 Advanced Setup:")
    print("   • Configure database in games/database.py")
    print("   • Customize API server in api/game_api.py")
    print("   • Modify games for specific requirements")

def main():
    """Main startup process"""
    print_banner()
    
    # Step 1: Check Python
    if not check_python():
        input("\nPress Enter to exit...")
        return
    
    # Step 2: Install dependencies
    if not install_dependencies():
        print("\n⚠️ Some dependencies failed to install. System may not work correctly.")
        if input("Continue anyway? (y/N): ").lower() != 'y':
            return
    
    # Step 3: Check database
    database_available = check_database()
    if not database_available:
        print("\n⚠️ Database not available. Games will run in offline mode.")
        print("💡 To enable database features:")
        print("   1. Install and start MySQL server")
        print("   2. Create 'paisabuddy' database")
        print("   3. Update connection settings in games/database.py")
        
        if input("\nContinue without database? (y/N): ").lower() != 'y':
            return
    
    # Step 4: Start API server (if database available)
    api_process = None
    if database_available:
        api_process = start_api_server()
    
    # Step 5: Show system information
    show_system_info()
    show_quick_start()
    
    # Step 6: Interactive menu
    print("\n" + "=" * 80)
    print("🎯 INTERACTIVE MENU")
    print("=" * 80)
    print("1. Launch Game Hub")
    print("2. Open Web Interface")
    print("3. Test Individual Games")
    print("4. View System Status")
    print("5. Exit")
    
    while True:
        try:
            choice = input("\nSelect option (1-5): ").strip()
            
            if choice == "1":
                print("🎮 Launching Game Hub...")
                subprocess.run([sys.executable, "games/game_launcher.py"])
                
            elif choice == "2":
                print("🌐 Opening Web Interface...")
                web_path = Path("frontend/gamified-learning.html").absolute()
                webbrowser.open(f"file://{web_path}")
                print(f"Opened: {web_path}")
                
            elif choice == "3":
                print("\n🎮 Available Games:")
                print("1. Budget Balance")
                print("2. Investment Garden") 
                print("3. Fraud Detective")
                
                game_choice = input("Select game (1-3): ").strip()
                games = {
                    "1": "games/budget_balance.py",
                    "2": "games/investment_growth.py",
                    "3": "games/fraud_detection.py"
                }
                
                if game_choice in games:
                    subprocess.run([sys.executable, games[game_choice]])
                else:
                    print("Invalid selection")
                    
            elif choice == "4":
                print("\n📊 System Status:")
                print(f"Python: {sys.version}")
                print(f"Database: {'✅ Connected' if database_available else '❌ Not available'}")
                print(f"API Server: {'✅ Running' if api_process and api_process.poll() is None else '❌ Not running'}")
                print(f"Working Directory: {os.getcwd()}")
                
            elif choice == "5":
                break
                
            else:
                print("❌ Invalid option. Please select 1-5.")
                
        except KeyboardInterrupt:
            break
    
    # Cleanup
    print("\n🛑 Shutting down...")
    if api_process and api_process.poll() is None:
        print("Stopping API server...")
        api_process.terminate()
        api_process.wait()
    
    print("✅ Paisabuddy system stopped. Thank you for learning with us! 🎓")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        input("Press Enter to exit...")
#!/usr/bin/env python3
"""
Paisabuddy Integrated Main Application
Starts both backend API and game system together
"""

import os
import sys
import subprocess
import time
import threading
import webbrowser
from pathlib import Path
import signal

# Add backend to path for imports
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def start_backend_server():
    """Start the main backend server"""
    print("🚀 Starting Paisabuddy Backend Server...")
    
    try:
        # Start FastAPI backend server using uvicorn
        backend_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "backend.main:app", 
            "--host", "0.0.0.0", "--port", "8000", "--reload"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Give it time to start
        time.sleep(3)
        
        if backend_process.poll() is None:
            print("✅ Backend server started successfully!")
            print("🌐 Backend API: http://localhost:8000")
            return backend_process
        else:
            stdout, stderr = backend_process.communicate()
            print("❌ Backend server failed to start")
            print(f"Error: {stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return None

def start_game_api():
    """Start the game progress API server"""
    print("🎮 Starting Game Progress API...")
    
    try:
        # Start game API server
        api_process = subprocess.Popen([
            sys.executable, "api/game_api.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Give it time to start
        time.sleep(2)
        
        if api_process.poll() is None:
            print("✅ Game API started successfully!")
            print("📊 Game API: http://localhost:5000")
            return api_process
        else:
            print("⚠️ Game API failed to start (database may not be configured)")
            return None
            
    except Exception as e:
        print(f"⚠️ Game API startup failed: {e}")
        return None

def install_dependencies():
    """Install required dependencies"""
    print("📬 Checking dependencies...")
    
    try:
        # Install backend requirements first
        if Path("backend/requirements.txt").exists():
            print("Installing backend dependencies...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", "backend/requirements.txt"
            ])
            
        # Install game requirements  
        if Path("games/requirements.txt").exists():
            print("Installing game dependencies...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", "games/requirements.txt"
            ])
            
        print("✅ Dependencies installed successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Some dependencies failed to install: {e}")
        return False

def open_browser():
    """Open browser with the main interface"""
    time.sleep(5)  # Wait for servers to fully start
    
    print("🌐 Opening web interface...")
    
    # Try to open the main frontend
    frontend_paths = [
        "frontend/index.html",
        "frontend/gamified-learning.html"
    ]
    
    for path in frontend_paths:
        if Path(path).exists():
            web_path = Path(path).absolute()
            webbrowser.open(f"file://{web_path}")
            print(f"✅ Opened: {web_path}")
            break
    else:
        print("⚠️ Frontend files not found")

def print_status():
    """Print system status and available features"""
    print("\n" + "=" * 80)
    print("🎯 PAISABUDDY PLATFORM - FULLY INTEGRATED")
    print("=" * 80)
    
    print("\n🌐 Web Services:")
    print("  • Main Backend API: http://localhost:8000")
    print("  • Game Progress API: http://localhost:5000") 
    print("  • Frontend Interface: Open in browser automatically")
    
    print("\n🎮 Available Features:")
    print("  • Interactive Financial Games (Pygame)")
    print("  • Web-based Quizzes and Challenges")
    print("  • Real-time Progress Tracking")
    print("  • Budget Tracking Tools")
    print("  • Investment Portfolio Simulator")
    print("  • Fraud Detection Training")
    
    print("\n📊 Integration Features:")
    print("  • Cross-platform progress synchronization")
    print("  • Database-backed user statistics")
    print("  • Achievement and reward system")
    print("  • Real-time leaderboards")
    
    print("\n💡 Quick Access:")
    print("  • Game Hub: python games/game_launcher.py")
    print("  • API Health: http://localhost:5000/api/health")
    print("  • Backend Docs: http://localhost:8000/docs")

def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully"""
    print("\n\n🛑 Shutting down Paisabuddy Platform...")
    sys.exit(0)

def main():
    """Main integrated startup process"""
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    print("=" * 80)
    print("🎮 PAISABUDDY INTEGRATED PLATFORM STARTUP")
    print("=" * 80)
    print("Starting complete financial learning platform...")
    print()
    
    # Step 1: Install dependencies
    install_dependencies()
    
    # Step 2: Start backend server
    backend_process = start_backend_server()
    if not backend_process:
        print("❌ Cannot start without backend server")
        return
    
    # Step 3: Start game API (optional, continues even if fails)
    game_api_process = start_game_api()
    
    # Step 4: Open browser in background thread
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()
    
    # Step 5: Print status
    print_status()
    
    print("\n🚀 Platform is running! Press Ctrl+C to stop all services.")
    print("💡 The web interface should open automatically in your browser.")
    
    try:
        # Keep the main process alive and monitor subprocesses
        while True:
            time.sleep(5)
            
            # Check if backend is still running
            if backend_process and backend_process.poll() is not None:
                print("❌ Backend server stopped unexpectedly")
                break
                
    except KeyboardInterrupt:
        pass
    finally:
        # Cleanup
        print("\n🛑 Stopping all services...")
        
        if backend_process and backend_process.poll() is None:
            print("Stopping backend server...")
            backend_process.terminate()
            backend_process.wait()
            
        if game_api_process and game_api_process.poll() is None:
            print("Stopping game API...")
            game_api_process.terminate()
            game_api_process.wait()
            
        print("✅ All services stopped. Thank you for using Paisabuddy! 🎓")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        input("Press Enter to exit...")
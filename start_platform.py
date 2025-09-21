#!/usr/bin/env python3
"""
Simple Paisabuddy Platform Startup
Starts backend and opens frontend
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def install_backend_deps():
    """Install backend dependencies"""
    print("📦 Installing backend dependencies...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "fastapi", "uvicorn[standard]", 
            "python-multipart", "mysql-connector-python", "python-jose[cryptography]", 
            "passlib[bcrypt]", "bcrypt"
        ])
        print("✅ Backend dependencies installed!")
        return True
    except Exception as e:
        print(f"⚠️ Backend dependency installation failed: {e}")
        return False

def start_backend():
    """Start the FastAPI backend"""
    print("🚀 Starting backend server...")
    
    try:
        # Try to start with uvicorn
        backend_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "backend.main:app", 
            "--host", "0.0.0.0", "--port", "8000", "--reload"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Wait and check if it started
        time.sleep(3)
        
        if backend_process.poll() is None:
            print("✅ Backend server started on http://localhost:8000")
            return backend_process
        else:
            # If failed, try alternative method
            print("⚠️ Uvicorn failed, trying alternative startup...")
            
            # Kill the failed process
            try:
                backend_process.terminate()
            except:
                pass
            
            # Try running directly in backend directory
            os.chdir("backend")
            backend_process = subprocess.Popen([
                sys.executable, "-c", 
                "import uvicorn; uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            os.chdir("..")  # Go back
            time.sleep(3)
            
            if backend_process.poll() is None:
                print("✅ Backend server started on http://localhost:8000")
                return backend_process
            else:
                stdout, stderr = backend_process.communicate()
                print("❌ Backend failed to start")
                print(f"Error: {stderr}")
                return None
                
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return None

def start_game_api():
    """Start game API if database is available"""
    print("🎮 Starting game API...")
    
    try:
        api_process = subprocess.Popen([
            sys.executable, "api/game_api.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        time.sleep(2)
        
        if api_process.poll() is None:
            print("✅ Game API started on http://localhost:5000")
            return api_process
        else:
            print("⚠️ Game API not available (database may not be configured)")
            return None
            
    except Exception as e:
        print(f"⚠️ Game API failed: {e}")
        return None

def open_frontend():
    """Open frontend in browser"""
    print("🌐 Opening frontend...")
    
    # Look for frontend files
    frontend_files = [
        "frontend/index.html",
        "frontend/gamified-learning.html"
    ]
    
    for file_path in frontend_files:
        if Path(file_path).exists():
            full_path = Path(file_path).absolute()
            webbrowser.open(f"file://{full_path}")
            print(f"✅ Opened: {full_path}")
            return True
    
    print("⚠️ Frontend files not found")
    return False

def main():
    """Main startup process"""
    print("=" * 60)
    print("🎮 PAISABUDDY PLATFORM STARTUP")
    print("=" * 60)
    
    # Step 1: Install dependencies
    install_backend_deps()
    
    # Step 2: Start backend
    backend_process = start_backend()
    if not backend_process:
        print("❌ Cannot continue without backend server")
        print("\n💡 Troubleshooting:")
        print("  1. Make sure you have backend/main.py")
        print("  2. Try running: pip install fastapi uvicorn")
        print("  3. Check if port 8000 is already in use")
        input("Press Enter to exit...")
        return
    
    # Step 3: Start game API (optional)
    game_process = start_game_api()
    
    # Step 4: Open frontend
    time.sleep(2)
    open_frontend()
    
    # Status
    print("\n" + "=" * 60)
    print("🎯 PLATFORM STATUS")
    print("=" * 60)
    print("✅ Backend API: http://localhost:8000")
    if game_process:
        print("✅ Game API: http://localhost:5000")
    else:
        print("⚠️ Game API: Not available")
    print("✅ Frontend: Opened in browser")
    
    print("\n🚀 Platform is running!")
    print("💡 Backend API docs: http://localhost:8000/docs")
    print("🛑 Press Ctrl+C to stop all services")
    
    try:
        while True:
            time.sleep(5)
            if backend_process.poll() is not None:
                print("❌ Backend stopped unexpectedly")
                break
    except KeyboardInterrupt:
        print("\n🛑 Stopping services...")
        
        if backend_process:
            backend_process.terminate()
            print("Backend stopped")
            
        if game_process:
            game_process.terminate() 
            print("Game API stopped")
            
        print("✅ All services stopped")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Cancelled by user")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        input("Press Enter to exit...")
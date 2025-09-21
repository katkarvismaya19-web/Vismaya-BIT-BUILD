#!/usr/bin/env python3
"""
Paisabuddy Game Setup Script
This script ensures all required dependencies are installed for pygame games
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def check_installation():
    """Check if required packages are installed"""
    packages = {
        'pygame': 'pygame',
        'numpy': 'numpy', 
        'requests': 'requests'
    }
    
    missing_packages = []
    
    for package_name, pip_name in packages.items():
        try:
            __import__(package_name)
            print(f"✅ {package_name} is installed")
        except ImportError:
            print(f"❌ {package_name} is missing")
            missing_packages.append(pip_name)
    
    return missing_packages

def main():
    """Main setup function"""
    print("🎮 Paisabuddy Game Setup")
    print("=" * 40)
    
    # Check current installations
    print("Checking installed packages...")
    missing = check_installation()
    
    if not missing:
        print("\n🎉 All dependencies are already installed!")
        print("\n🚀 You can now launch games from the web interface!")
        print("   1. Start the backend server: cd backend && python main.py")
        print("   2. Open gamified-learning.html in your browser")
        print("   3. Click any 'Play' button to launch pygame games")
        return
    
    print(f"\n📦 Installing missing packages: {', '.join(missing)}")
    
    # Install missing packages
    all_installed = True
    for package in missing:
        print(f"\nInstalling {package}...")
        if install_package(package):
            print(f"✅ Successfully installed {package}")
        else:
            print(f"❌ Failed to install {package}")
            all_installed = False
    
    if all_installed:
        print("\n🎉 All dependencies installed successfully!")
        print("\n🚀 Setup complete! You can now:")
        print("   1. Start the backend server: cd backend && python main.py")
        print("   2. Open gamified-learning.html in your browser") 
        print("   3. Click any 'Play' button to launch pygame games")
        
        # Test game availability
        print("\n🎮 Testing game availability...")
        games_dir = os.path.join(os.path.dirname(__file__), "games")
        game_files = ["budget_balance.py", "investment_growth.py", "fraud_detection.py", "game_launcher.py"]
        
        found_games = []
        for game_file in game_files:
            game_path = os.path.join(games_dir, game_file)
            if os.path.exists(game_path):
                found_games.append(game_file)
                print(f"   ✅ {game_file}")
            else:
                print(f"   ❌ {game_file} (missing)")
        
        if found_games:
            print(f"\n🎮 Found {len(found_games)}/{len(game_files)} games ready to play!")
        else:
            print("\n⚠️  No game files found in games/ directory")
            
    else:
        print("\n❌ Some packages failed to install. Please install manually:")
        for package in missing:
            print(f"   pip install {package}")

if __name__ == "__main__":
    main()
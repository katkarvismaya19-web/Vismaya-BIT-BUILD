#!/usr/bin/env python3
"""
Paisabuddy Financial Games - Installation and Setup Script
This script helps users install the required dependencies and test the games.
"""

import sys
import subprocess
import os
import platform
from pathlib import Path

def print_banner():
    """Print welcome banner"""
    print("=" * 60)
    print("🎮 PAISABUDDY FINANCIAL GAMES INSTALLER 🎮")
    print("=" * 60)
    print("Welcome to the Paisabuddy Financial Learning Games!")
    print("This script will help you install and set up everything you need.\n")

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print(f"❌ Python {version.major}.{version.minor} detected. Python 3.7+ is required.")
        print("Please update Python at: https://python.org/downloads/")
        return False
    else:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible!")
        return True

def install_package(package):
    """Install a Python package using pip"""
    try:
        print(f"📦 Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}")
        return False

def check_and_install_dependencies():
    """Check and install required dependencies"""
    print("\n📋 Checking dependencies...")
    
    required_packages = {
        'pygame': '2.5.2',
        'numpy': '1.24.3',
    }
    
    optional_packages = {
        'matplotlib': '3.7.1'
    }
    
    all_installed = True
    
    # Check required packages
    for package, version in required_packages.items():
        try:
            __import__(package)
            print(f"✅ {package} is already installed")
        except ImportError:
            print(f"❌ {package} is not installed")
            if install_package(f"{package}>={version}"):
                continue
            else:
                all_installed = False
    
    # Check optional packages
    for package, version in optional_packages.items():
        try:
            __import__(package)
            print(f"✅ {package} (optional) is already installed")
        except ImportError:
            print(f"⚠️ {package} (optional) is not installed")
            install_package(f"{package}>={version}")
    
    return all_installed

def test_games():
    """Test if games can be imported and run"""
    print("\n🧪 Testing games...")
    
    games = [
        ('budget_balance.py', 'Budget Balance Game'),
        ('investment_growth.py', 'Investment Garden Game'), 
        ('fraud_detection.py', 'Fraud Detective Game'),
        ('game_launcher.py', 'Game Launcher Hub')
    ]
    
    working_games = []
    
    for game_file, game_name in games:
        if os.path.exists(game_file):
            try:
                # Try to import the game (basic syntax check)
                with open(game_file, 'r') as f:
                    compile(f.read(), game_file, 'exec')
                print(f"✅ {game_name} - Ready to play!")
                working_games.append((game_file, game_name))
            except Exception as e:
                print(f"❌ {game_name} - Error: {e}")
        else:
            print(f"❌ {game_name} - File not found: {game_file}")
    
    return working_games

def create_shortcuts():
    """Create desktop shortcuts for easy access"""
    print("\n🔗 Creating shortcuts...")
    
    try:
        current_dir = os.path.abspath('.')
        
        if platform.system() == "Windows":
            create_windows_shortcuts(current_dir)
        elif platform.system() == "Linux":
            create_linux_shortcuts(current_dir)
        elif platform.system() == "Darwin":  # macOS
            create_macos_shortcuts(current_dir)
        else:
            print("⚠️ Automatic shortcut creation not supported for your OS")
            
    except Exception as e:
        print(f"⚠️ Could not create shortcuts: {e}")

def create_windows_shortcuts(current_dir):
    """Create Windows shortcuts"""
    try:
        import winshell
        from win32com.client import Dispatch
        
        desktop = winshell.desktop()
        
        # Create shortcut for game launcher
        shortcut = Dispatch('WScript.Shell').CreateShortCut(
            os.path.join(desktop, "Paisabuddy Games.lnk")
        )
        shortcut.Targetpath = sys.executable
        shortcut.Arguments = os.path.join(current_dir, "game_launcher.py")
        shortcut.WorkingDirectory = current_dir
        shortcut.IconLocation = sys.executable
        shortcut.save()
        
        print("✅ Windows shortcuts created on desktop!")
        
    except ImportError:
        print("⚠️ Could not create Windows shortcuts (missing winshell/pywin32)")
    except Exception as e:
        print(f"⚠️ Error creating Windows shortcuts: {e}")

def create_linux_shortcuts(current_dir):
    """Create Linux desktop shortcuts"""
    try:
        desktop_dir = Path.home() / "Desktop"
        if not desktop_dir.exists():
            desktop_dir = Path.home()
            
        shortcut_content = f"""[Desktop Entry]
Name=Paisabuddy Games
Comment=Financial Learning Games
Exec=python3 "{os.path.join(current_dir, 'game_launcher.py')}"
Icon=applications-games
Terminal=false
Type=Application
Categories=Game;Education;
"""
        
        shortcut_path = desktop_dir / "paisabuddy-games.desktop"
        with open(shortcut_path, 'w') as f:
            f.write(shortcut_content)
        
        # Make executable
        os.chmod(shortcut_path, 0o755)
        
        print("✅ Linux shortcuts created!")
        
    except Exception as e:
        print(f"⚠️ Error creating Linux shortcuts: {e}")

def create_macos_shortcuts(current_dir):
    """Create macOS shortcuts"""
    try:
        # Create simple shell script
        script_content = f"""#!/bin/bash
cd "{current_dir}"
python3 game_launcher.py
"""
        
        script_path = Path.home() / "Desktop" / "Paisabuddy Games.command"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        os.chmod(script_path, 0o755)
        
        print("✅ macOS shortcuts created!")
        
    except Exception as e:
        print(f"⚠️ Error creating macOS shortcuts: {e}")

def print_instructions(working_games):
    """Print final instructions"""
    print("\n" + "=" * 60)
    print("🎉 INSTALLATION COMPLETE!")
    print("=" * 60)
    
    if working_games:
        print("\n🎮 Available Games:")
        for game_file, game_name in working_games:
            print(f"   • {game_name}")
            print(f"     Run: python {game_file}")
        
        print(f"\n🚀 Quick Start:")
        print(f"   python game_launcher.py")
        print(f"   (Opens the main game hub with all games)")
        
        print(f"\n💡 Game Features:")
        print(f"   • Budget Balance: Learn expense management through action gameplay")
        print(f"   • Investment Garden: Understand compound interest by growing investments")
        print(f"   • Fraud Detective: Master scam detection and security awareness")
        
        print(f"\n📊 Progress Tracking:")
        print(f"   • Your scores and achievements are automatically saved")
        print(f"   • Use the Game Launcher Hub for comprehensive statistics")
        
    else:
        print("\n❌ No games are ready to play. Please check the error messages above.")
        
    print(f"\n🆘 Need Help?")
    print(f"   • Make sure Python 3.7+ is installed")
    print(f"   • Try: pip install --upgrade pygame numpy")
    print(f"   • Contact support if issues persist")
    
    print("\n🎓 Happy Learning with Paisabuddy Financial Games! 🎓")

def main():
    """Main installation process"""
    print_banner()
    
    # Step 1: Check Python version
    if not check_python_version():
        input("\nPress Enter to exit...")
        return
    
    # Step 2: Install dependencies
    if not check_and_install_dependencies():
        print("\n⚠️ Some required packages failed to install.")
        print("You may need to install them manually or check your internet connection.")
    
    # Step 3: Test games
    working_games = test_games()
    
    # Step 4: Create shortcuts (optional)
    create_shortcuts()
    
    # Step 5: Print instructions
    print_instructions(working_games)
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Installation cancelled by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please report this issue if it persists.")
        input("Press Enter to exit...")
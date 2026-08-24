#!/usr/bin/env python3
"""
Fix common game issues and create required directories/files
"""

import os
import json

def create_game_directories():
    """Create required directories for games"""
    directories = [
        'games',
        'assets',
        'assets/images',
        'assets/sounds'
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Created directory: {directory}")
        else:
            print(f"✓ Directory exists: {directory}")

def create_progress_files():
    """Create initial progress files for games"""
    progress_files = {
        'games/progress.json': {
            "games_played": 0,
            "high_score": 0,
            "achievements": [],
            "total_time_played": 0
        },
        'games/investment_progress.json': {
            "games_played": 0,
            "high_score": 0,
            "best_portfolio_value": 0,
            "total_investments": 0,
            "achievements": []
        },
        'games/fraud_progress.json': {
            "games_played": 0,
            "high_score": 0,
            "scams_detected": 0,
            "accuracy_rate": 0,
            "achievements": []
        }
    }
    
    for file_path, initial_data in progress_files.items():
        if not os.path.exists(file_path):
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Create file with initial data
            with open(file_path, 'w') as f:
                json.dump(initial_data, f, indent=2)
            print(f"✅ Created progress file: {file_path}")
        else:
            print(f"✓ Progress file exists: {file_path}")

def fix_game_paths():
    """Fix hardcoded paths in game files"""
    game_files = [
        'investment_growth.py',
        'fraud_detection.py'
    ]
    
    for game_file in game_files:
        if os.path.exists(game_file):
            try:
                with open(game_file, 'r') as f:
                    content = f.read()
                
                # Fix progress file paths
                original_content = content
                content = content.replace("'games/investment_progress.json'", "'investment_progress.json'")
                content = content.replace("'games/fraud_progress.json'", "'fraud_progress.json'")
                content = content.replace("'games/progress.json'", "'progress.json'")
                
                if content != original_content:
                    with open(game_file, 'w') as f:
                        f.write(content)
                    print(f"✅ Fixed paths in: {game_file}")
                else:
                    print(f"✓ No path fixes needed in: {game_file}")
                    
            except Exception as e:
                print(f"❌ Error fixing {game_file}: {e}")
        else:
            print(f"⚠️ Game file not found: {game_file}")

def create_default_config():
    """Create default game configuration"""
    config = {
        "game_settings": {
            "music_volume": 0.7,
            "sound_effects": True,
            "fullscreen": False,
            "difficulty": "medium",
            "auto_save": True
        },
        "player_preferences": {
            "player_name": "Player",
            "tutorial_completed": False,
            "tips_enabled": True
        }
    }
    
    config_file = 'game_config.json'
    if not os.path.exists(config_file):
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"✅ Created config file: {config_file}")
    else:
        print(f"✓ Config file exists: {config_file}")

def main():
    """Main function to run all fixes"""
    print("🔧 Fixing Paisabuddy Games...")
    print("-" * 50)
    
    try:
        create_game_directories()
        print()
        
        create_progress_files()
        print()
        
        fix_game_paths()
        print()
        
        create_default_config()
        print()
        
        print("✅ All game fixes completed successfully!")
        print("\n🎮 You can now run the games without path errors.")
        print("📁 Progress will be saved in the current directory.")
        
    except Exception as e:
        print(f"❌ Error during fixes: {e}")

if __name__ == "__main__":
    main()
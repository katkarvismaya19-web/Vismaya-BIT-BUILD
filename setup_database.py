#!/usr/bin/env python3
"""
Quick Database Setup for Paisabuddy
"""

import os
import sys

def update_database_config():
    """Update database configuration with common settings"""
    
    print("🛠️ Setting up database configuration...")
    
    # Common MySQL password configurations
    common_passwords = ["", "root", "password", "admin"]
    
    config_template = '''        self.config = {
            'host': 'localhost',
            'database': 'paisabuddy',
            'user': 'root',
            'password': '{password}',
            'port': 3306,
            'charset': 'utf8mb4',
            'autocommit': True
        }'''
    
    # Try to read database.py
    db_file = "games/database.py"
    
    if not os.path.exists(db_file):
        print(f"❌ Database file not found: {db_file}")
        return False
    
    print("\n🔧 Common MySQL configurations to try:")
    print("1. Empty password (default for many installations)")
    print("2. Password: 'root' (XAMPP/WAMP default)")  
    print("3. Password: 'password' (common default)")
    print("4. Password: 'admin' (common default)")
    print("5. Custom password")
    
    choice = input("\nSelect option (1-5): ").strip()
    
    if choice == "1":
        password = ""
    elif choice == "2":
        password = "root"
    elif choice == "3":
        password = "password"
    elif choice == "4":
        password = "admin"
    elif choice == "5":
        password = input("Enter your MySQL password: ").strip()
    else:
        print("❌ Invalid choice")
        return False
    
    try:
        # Read the file
        with open(db_file, 'r') as f:
            content = f.read()
        
        # Find and replace the config section
        import re
        pattern = r"self\.config = \{[^}]+\}"
        new_config = config_template.format(password=password).strip()
        
        updated_content = re.sub(pattern, new_config, content, flags=re.MULTILINE | re.DOTALL)
        
        # Write back
        with open(db_file, 'w') as f:
            f.write(updated_content)
            
        print(f"✅ Database configuration updated with password: '{password}'")
        print("💡 You can now run: python main_integrated.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to update configuration: {e}")
        return False

def main():
    print("=" * 60)
    print("🗄️ PAISABUDDY DATABASE SETUP")
    print("=" * 60)
    
    print("This will configure the database connection for your MySQL setup.")
    print("Make sure you have:")
    print("  1. MySQL server running")
    print("  2. 'paisabuddy' database created")
    print("  3. Know your MySQL root password")
    print()
    
    if input("Continue? (y/N): ").lower() != 'y':
        return
    
    if update_database_config():
        print("\n🎉 Setup completed!")
        print("\n🚀 Next steps:")
        print("  1. Run: python main_integrated.py")
        print("  2. Your platform will start with backend + games integrated!")
    else:
        print("\n❌ Setup failed. Please check your MySQL configuration.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Setup cancelled")
    finally:
        input("Press Enter to exit...")
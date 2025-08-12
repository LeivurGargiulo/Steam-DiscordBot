#!/usr/bin/env python3
"""
Quick Start Script for Optimized Steam Discord Bot

This script helps users quickly set up and run the bot with minimal configuration.
It provides an interactive setup process and validates the environment.
"""

import os
import sys
import subprocess
from pathlib import Path
import shutil

def print_banner():
    """Print the bot banner"""
    print("=" * 80)
    print("🎮 Optimized Steam Discord Bot - Quick Start")
    print("=" * 80)
    print()

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    print("\n📦 Checking dependencies...")
    
    required_packages = [
        'discord.py',
        'aiohttp',
        'python-dotenv',
        'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} (missing)")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        install = input("Would you like to install missing packages? (y/n): ").lower()
        
        if install == 'y':
            print("Installing packages...")
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
                print("✅ Packages installed successfully")
                return True
            except subprocess.CalledProcessError:
                print("❌ Failed to install packages")
                return False
        else:
            print("Please install the missing packages manually:")
            print(f"pip install {' '.join(missing_packages)}")
            return False
    
    return True

def setup_environment():
    """Set up the environment file"""
    print("\n🔧 Setting up environment...")
    
    env_file = Path('.env')
    example_file = Path('.env.example')
    
    if env_file.exists():
        overwrite = input(".env file already exists. Overwrite? (y/n): ").lower()
        if overwrite != 'y':
            print("Using existing .env file")
            return True
    
    if not example_file.exists():
        print("❌ .env.example file not found")
        return False
    
    # Copy example file
    shutil.copy(example_file, env_file)
    print("✅ Created .env file from template")
    
    return True

def get_user_input():
    """Get required configuration from user"""
    print("\n🔑 Configuration Setup")
    print("You'll need to provide your Discord bot token and Steam API key.")
    print()
    
    # Discord Token
    print("Discord Bot Token:")
    print("1. Go to https://discord.com/developers/applications")
    print("2. Create a new application or select existing")
    print("3. Go to 'Bot' section")
    print("4. Create a bot and copy the token")
    print()
    
    discord_token = input("Enter your Discord bot token: ").strip()
    if not discord_token:
        print("❌ Discord token is required")
        return False
    
    # Steam API Key
    print("\nSteam API Key:")
    print("1. Go to https://steamcommunity.com/dev/apikey")
    print("2. Register for a free API key")
    print("3. Copy the key")
    print()
    
    steam_token = input("Enter your Steam API key: ").strip()
    if not steam_token:
        print("❌ Steam API key is required")
        return False
    
    # Update .env file
    try:
        with open('.env', 'r') as f:
            content = f.read()
        
        content = content.replace('your_discord_bot_token_here', discord_token)
        content = content.replace('your_steam_api_key_here', steam_token)
        
        with open('.env', 'w') as f:
            f.write(content)
        
        print("✅ Configuration saved to .env file")
        return True
        
    except Exception as e:
        print(f"❌ Error saving configuration: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    
    directories = ['logs', 'data', 'cache']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created {directory}/ directory")
    
    return True

def validate_setup():
    """Validate the setup"""
    print("\n🔍 Validating setup...")
    
    # Check .env file
    if not Path('.env').exists():
        print("❌ .env file not found")
        return False
    
    # Check for required tokens
    with open('.env', 'r') as f:
        content = f.read()
    
    if 'your_discord_bot_token_here' in content:
        print("❌ Discord token not configured")
        return False
    
    if 'your_steam_api_key_here' in content:
        print("❌ Steam API key not configured")
        return False
    
    print("✅ Setup validation passed")
    return True

def run_bot():
    """Run the bot"""
    print("\n🚀 Starting the bot...")
    print("Press Ctrl+C to stop the bot")
    print()
    
    try:
        # Import and run the bot
        from run_optimized_bot import main
        import asyncio
        
        asyncio.run(main())
        
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except ImportError as e:
        print(f"❌ Error importing bot modules: {e}")
        print("Please ensure all optimized_*.py files are present")
    except Exception as e:
        print(f"❌ Error running bot: {e}")

def main():
    """Main quick start function"""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Setup environment
    if not setup_environment():
        sys.exit(1)
    
    # Get user input
    if not get_user_input():
        sys.exit(1)
    
    # Create directories
    if not create_directories():
        sys.exit(1)
    
    # Validate setup
    if not validate_setup():
        sys.exit(1)
    
    # Success message
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Invite your bot to your Discord server")
    print("2. Use !help to see available commands")
    print("3. Try !profile <steamid> to test the bot")
    print()
    
    # Ask if user wants to run the bot
    run_now = input("Would you like to start the bot now? (y/n): ").lower()
    
    if run_now == 'y':
        run_bot()
    else:
        print("\nTo start the bot later, run:")
        print("python run_optimized_bot.py")
        print("\nOr use this quick start script again:")
        print("python quick_start.py")

if __name__ == "__main__":
    main()
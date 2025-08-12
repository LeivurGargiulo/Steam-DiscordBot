#!/usr/bin/env python3
"""
Test script for Steam Discord Bot

This script tests the basic setup and functionality of the Discord bot
without actually connecting to Discord.
"""

import os
import sys
import asyncio
from unittest.mock import Mock, patch

# Load test environment variables
from dotenv import load_dotenv
load_dotenv('.env.test')

def test_imports():
    """Test that all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        import discord
        print(f"✅ discord.py imported successfully (version: {discord.__version__})")
    except ImportError as e:
        print(f"❌ Failed to import discord.py: {e}")
        return False
    
    try:
        from discord_bot import SteamDiscordBot
        print("✅ SteamDiscordBot imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import SteamDiscordBot: {e}")
        return False
    
    try:
        from steam_api import SteamAPI
        print("✅ SteamAPI imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import SteamAPI: {e}")
        return False
    
    try:
        from config import Config
        print("✅ Config imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Config: {e}")
        return False
    
    try:
        from utils import validate_steam_id, validate_app_id
        print("✅ Utils imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import utils: {e}")
        return False
    
    return True

def test_config():
    """Test configuration setup"""
    print("\n🔍 Testing configuration...")
    
    from config import Config
    
    # Test environment variables
    if not os.getenv('DISCORD_TOKEN'):
        print("⚠️  DISCORD_TOKEN not set in environment")
    else:
        print("✅ DISCORD_TOKEN found in environment")
    
    if not os.getenv('STEAM_API_KEY'):
        print("⚠️  STEAM_API_KEY not set in environment")
    else:
        print("✅ STEAM_API_KEY found in environment")
    
    # Test config validation
    try:
        Config.validate_config()
        print("✅ Configuration validation passed")
    except ValueError as e:
        print(f"❌ Configuration validation failed: {e}")
        return False
    
    return True

def test_steam_api():
    """Test Steam API functionality"""
    print("\n🔍 Testing Steam API...")
    
    from steam_api import SteamAPI
    
    try:
        api = SteamAPI()
        print("✅ SteamAPI instance created successfully")
        
        # Test basic validation functions
        from utils import validate_steam_id, validate_app_id
        
        # Test Steam ID validation
        valid_steam_id = "76561198000000000"
        invalid_steam_id = "12345"
        
        if validate_steam_id(valid_steam_id):
            print("✅ Steam ID validation working")
        else:
            print("❌ Steam ID validation failed")
            return False
        
        if not validate_steam_id(invalid_steam_id):
            print("✅ Invalid Steam ID correctly rejected")
        else:
            print("❌ Invalid Steam ID incorrectly accepted")
            return False
        
        # Test App ID validation
        valid_app_id = "730"
        invalid_app_id = "abc"
        
        if validate_app_id(valid_app_id):
            print("✅ App ID validation working")
        else:
            print("❌ App ID validation failed")
            return False
        
        if not validate_app_id(invalid_app_id):
            print("✅ Invalid App ID correctly rejected")
        else:
            print("❌ Invalid App ID incorrectly accepted")
            return False
        
    except Exception as e:
        print(f"❌ Steam API test failed: {e}")
        return False
    
    return True

def test_bot_creation():
    """Test bot instance creation"""
    print("\n🔍 Testing bot creation...")
    
    try:
        from discord_bot import SteamDiscordBot
        
        # Mock the bot to avoid actual Discord connection and async issues
        with patch('discord.ext.commands.Bot.__init__'), \
             patch('discord_bot.tasks.loop'), \
             patch('discord_bot.SteamDiscordBot.cleanup_task'):
            bot = SteamDiscordBot()
            print("✅ Bot instance created successfully")
            
            # Test bot attributes
            if hasattr(bot, 'steam_api'):
                print("✅ Steam API attached to bot")
            else:
                print("❌ Steam API not attached to bot")
                return False
            
            if hasattr(bot, 'start_time'):
                print("✅ Bot start time initialized")
            else:
                print("❌ Bot start time not initialized")
                return False
            
    except Exception as e:
        print(f"❌ Bot creation test failed: {e}")
        return False
    
    return True

def test_utility_functions():
    """Test utility functions"""
    print("\n🔍 Testing utility functions...")
    
    try:
        from utils import format_playtime, validate_steam_id, validate_app_id
        
        # Test playtime formatting
        test_cases = [
            (30, "30m"),
            (90, "1h 30m"),
            (1440, "1d"),
            (1500, "1d 1h")
        ]
        
        for minutes, expected in test_cases:
            result = format_playtime(minutes)
            if result == expected:
                print(f"✅ Playtime formatting: {minutes} minutes -> {result}")
            else:
                print(f"❌ Playtime formatting failed: {minutes} minutes -> {result} (expected {expected})")
                return False
        
        # Test Steam ID validation
        steam_id_tests = [
            ("76561198000000000", True),
            ("12345678901234567", True),
            ("12345", False),
            ("abc", False),
            ("", False)
        ]
        
        for steam_id, expected in steam_id_tests:
            result = validate_steam_id(steam_id)
            if result == expected:
                print(f"✅ Steam ID validation: {steam_id} -> {result}")
            else:
                print(f"❌ Steam ID validation failed: {steam_id} -> {result} (expected {expected})")
                return False
        
        # Test App ID validation
        app_id_tests = [
            ("730", True),
            ("123456", True),
            ("abc", False),
            ("", False)
        ]
        
        for app_id, expected in app_id_tests:
            result = validate_app_id(app_id)
            if result == expected:
                print(f"✅ App ID validation: {app_id} -> {result}")
            else:
                print(f"❌ App ID validation failed: {app_id} -> {result} (expected {expected})")
                return False
        
    except Exception as e:
        print(f"❌ Utility functions test failed: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🧪 Steam Discord Bot Test Suite")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Configuration Test", test_config),
        ("Steam API Test", test_steam_api),
        ("Bot Creation Test", test_bot_creation),
        ("Utility Functions Test", test_utility_functions)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your Discord bot setup is ready.")
        print("\nNext steps:")
        print("1. Set up your .env file with DISCORD_TOKEN and STEAM_API_KEY")
        print("2. Run: python discord_main.py")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
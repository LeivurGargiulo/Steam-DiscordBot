#!/usr/bin/env python3
"""
Test script for Steam Telegram Bot

This script tests the basic functionality of the bot components
without requiring a Telegram bot token.
"""

import sys
import os
from steam_api import SteamAPI
from utils import *
from config import Config

def test_steam_api():
    """Test Steam API functionality"""
    print("🧪 Testing Steam API...")
    
    # Check if API key is configured
    if not Config.STEAM_API_KEY:
        print("❌ Steam API key not configured. Please set STEAM_API_KEY in .env file")
        return False
    
    steam_api = SteamAPI()
    
    # Test with a known Steam ID (Valve's official account)
    test_steam_id = "76561197960287930"  # Valve's Steam ID
    
    print(f"Testing with Steam ID: {test_steam_id}")
    
    # Test profile fetch
    print("  📋 Testing profile fetch...")
    try:
        profile = steam_api.get_user_profile(test_steam_id)
        if profile:
            print(f"  ✅ Profile: {profile.get('personaname', 'Unknown')}")
        else:
            print("  ❌ Could not fetch profile")
    except Exception as e:
        print(f"  ❌ Profile fetch error: {e}")
    
    # Test game details (CS2)
    print("  🎮 Testing game details...")
    try:
        game = steam_api.get_game_details("730")  # CS2
        if game:
            print(f"  ✅ Game: {game.get('name', 'Unknown')}")
        else:
            print("  ❌ Could not fetch game details")
    except Exception as e:
        print(f"  ❌ Game details error: {e}")
    
    # Test player count
    print("  👥 Testing player count...")
    try:
        count = steam_api.get_player_count("730")  # CS2
        if count is not None:
            print(f"  ✅ Player count: {count:,}")
        else:
            print("  ❌ Could not fetch player count")
    except Exception as e:
        print(f"  ❌ Player count error: {e}")
    
    # Test featured games
    print("  🔥 Testing featured games...")
    try:
        featured = steam_api.get_featured_games()
        if featured and featured.get('featured_win'):
            games = featured['featured_win'].get('items', [])
            print(f"  ✅ Featured games: {len(games)} games found")
        else:
            print("  ❌ Could not fetch featured games")
    except Exception as e:
        print(f"  ❌ Featured games error: {e}")
    
    return True

def test_utils():
    """Test utility functions"""
    print("\n🧪 Testing utility functions...")
    
    # Test Steam ID validation
    print("  🔍 Testing Steam ID validation...")
    valid_id = "76561197960287930"
    invalid_id = "12345"
    
    if validate_steam_id(valid_id):
        print("  ✅ Valid Steam ID validation works")
    else:
        print("  ❌ Valid Steam ID validation failed")
    
    if not validate_steam_id(invalid_id):
        print("  ✅ Invalid Steam ID validation works")
    else:
        print("  ❌ Invalid Steam ID validation failed")
    
    # Test App ID validation
    print("  🎮 Testing App ID validation...")
    valid_app_id = "730"
    invalid_app_id = "abc"
    
    if validate_app_id(valid_app_id):
        print("  ✅ Valid App ID validation works")
    else:
        print("  ❌ Valid App ID validation failed")
    
    if not validate_app_id(invalid_app_id):
        print("  ✅ Invalid App ID validation works")
    else:
        print("  ❌ Invalid App ID validation failed")
    
    # Test playtime formatting
    print("  ⏱️ Testing playtime formatting...")
    test_cases = [
        (30, "30m"),
        (90, "1h 30m"),
        (1440, "1d"),
        (1500, "1d 1h")
    ]
    
    for minutes, expected in test_cases:
        result = format_playtime(minutes)
        if result == expected:
            print(f"  ✅ {minutes} minutes -> {result}")
        else:
            print(f"  ❌ {minutes} minutes -> {result} (expected {expected})")

def test_config():
    """Test configuration"""
    print("\n🧪 Testing configuration...")
    
    # Test environment loading
    if Config.TELEGRAM_TOKEN:
        print("  ✅ Telegram token configured")
    else:
        print("  ⚠️ Telegram token not configured (required for bot)")
    
    if Config.STEAM_API_KEY:
        print("  ✅ Steam API key configured")
    else:
        print("  ❌ Steam API key not configured (required for testing)")
    
    print(f"  📊 Cache duration: {Config.CACHE_DURATION} seconds")
    print(f"  ⏱️ Rate limit delay: {Config.RATE_LIMIT_DELAY} seconds")

def main():
    """Main test function"""
    print("🎮 Steam Telegram Bot - Test Suite")
    print("=" * 50)
    
    # Test configuration
    test_config()
    
    # Test utility functions
    test_utils()
    
    # Test Steam API (only if API key is configured)
    if Config.STEAM_API_KEY:
        test_steam_api()
    else:
        print("\n⚠️ Skipping Steam API tests - no API key configured")
        print("   To test API functionality, set STEAM_API_KEY in .env file")
    
    print("\n" + "=" * 50)
    print("✅ Test suite completed!")
    
    if not Config.STEAM_API_KEY:
        print("\n📝 Next steps:")
        print("1. Get a Steam API key from https://steamcommunity.com/dev/apikey")
        print("2. Add it to your .env file")
        print("3. Run this test again to verify API functionality")

if __name__ == "__main__":
    main()
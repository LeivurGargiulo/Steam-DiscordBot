import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for the Steam Telegram Bot"""
    
    # Telegram Bot Token
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
    
    # Steam API Key
    STEAM_API_KEY = os.getenv('STEAM_API_KEY')
    
    # Steam API Base URLs
    STEAM_API_BASE = "https://api.steampowered.com"
    STEAM_STORE_BASE = "https://store.steampowered.com"
    STEAM_COMMUNITY_BASE = "https://steamcommunity.com"
    
    # Cache settings
    CACHE_DURATION = 300  # 5 minutes in seconds
    
    # Rate limiting
    RATE_LIMIT_DELAY = 1  # seconds between API calls
    
    @classmethod
    def validate_config(cls):
        """Validate that required environment variables are set"""
        if not cls.TELEGRAM_TOKEN:
            raise ValueError("TELEGRAM_TOKEN environment variable is required")
        if not cls.STEAM_API_KEY:
            raise ValueError("STEAM_API_KEY environment variable is required")
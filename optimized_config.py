"""
Optimized Configuration Management

This module provides secure and robust configuration management with:
- Environment variable validation
- Secure token handling
- Performance tuning options
- Comprehensive error handling
- Type hints for better code safety
"""

import os
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass
from dotenv import load_dotenv
import secrets

# Load environment variables from .env file
load_dotenv()

@dataclass
class DatabaseConfig:
    """Database configuration settings"""
    host: str = "localhost"
    port: int = 5432
    name: str = "steam_bot"
    user: str = "steam_bot"
    password: Optional[str] = None
    pool_size: int = 10
    max_overflow: int = 20

@dataclass
class CacheConfig:
    """Cache configuration settings"""
    max_size: int = 1000
    default_ttl: int = 300  # 5 minutes
    profile_ttl: int = 300  # 5 minutes
    game_ttl: int = 3600    # 1 hour
    player_count_ttl: int = 120  # 2 minutes
    cleanup_interval: int = 300  # 5 minutes

@dataclass
class RateLimitConfig:
    """Rate limiting configuration"""
    max_requests: int = 15
    window_seconds: int = 60
    burst_limit: int = 5
    cooldown_seconds: int = 30

@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    log_commands: bool = True
    log_api_calls: bool = True
    log_errors: bool = True

class OptimizedConfig:
    """Enhanced configuration class with comprehensive validation and security"""
    
    def __init__(self):
        # Bot Tokens (required)
        self.discord_token: Optional[str] = self._get_required_env('DISCORD_TOKEN')
        self.steam_api_key: Optional[str] = self._get_required_env('STEAM_API_KEY')
        
        # Optional tokens
        self.telegram_token: Optional[str] = self._get_optional_env('TELEGRAM_TOKEN')
        
        # Steam API URLs
        self.steam_api_base: str = "https://api.steampowered.com"
        self.steam_store_base: str = "https://store.steampowered.com"
        self.steam_community_base: str = "https://steamcommunity.com"
        
        # Performance settings
        self.max_concurrent_requests: int = int(self._get_optional_env('MAX_CONCURRENT_REQUESTS', '10'))
        self.request_timeout: int = int(self._get_optional_env('REQUEST_TIMEOUT', '30'))
        self.retry_attempts: int = int(self._get_optional_env('RETRY_ATTEMPTS', '3'))
        self.retry_delay: float = float(self._get_optional_env('RETRY_DELAY', '1.0'))
        
        # Security settings
        self.allowed_guilds: list = self._parse_allowed_guilds()
        self.admin_user_ids: list = self._parse_admin_users()
        self.enable_debug_mode: bool = self._get_optional_env('DEBUG_MODE', 'false').lower() == 'true'
        
        # Feature flags
        self.enable_caching: bool = self._get_optional_env('ENABLE_CACHING', 'true').lower() == 'true'
        self.enable_rate_limiting: bool = self._get_optional_env('ENABLE_RATE_LIMITING', 'true').lower() == 'true'
        self.enable_analytics: bool = self._get_optional_env('ENABLE_ANALYTICS', 'true').lower() == 'true'
        
        # Initialize sub-configurations
        self.cache = CacheConfig()
        self.rate_limit = RateLimitConfig()
        self.logging = LoggingConfig()
        self.database = DatabaseConfig()
        
        # Override with environment variables if present
        self._load_env_overrides()
        
        # Generate session secret for internal use
        self.session_secret: str = self._get_optional_env('SESSION_SECRET') or secrets.token_urlsafe(32)
    
    def _get_required_env(self, key: str) -> str:
        """Get required environment variable with validation"""
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Required environment variable '{key}' is not set")
        return value.strip()
    
    def _get_optional_env(self, key: str, default: str = None) -> Optional[str]:
        """Get optional environment variable"""
        value = os.getenv(key, default)
        return value.strip() if value else None
    
    def _parse_allowed_guilds(self) -> list:
        """Parse allowed guild IDs from environment variable"""
        guilds_str = self._get_optional_env('ALLOWED_GUILDS', '')
        if not guilds_str:
            return []  # Allow all guilds if not specified
        
        try:
            return [int(guild_id.strip()) for guild_id in guilds_str.split(',') if guild_id.strip()]
        except ValueError:
            logging.warning(f"Invalid guild ID format in ALLOWED_GUILDS: {guilds_str}")
            return []
    
    def _parse_admin_users(self) -> list:
        """Parse admin user IDs from environment variable"""
        users_str = self._get_optional_env('ADMIN_USER_IDS', '')
        if not users_str:
            return []
        
        try:
            return [int(user_id.strip()) for user_id in users_str.split(',') if user_id.strip()]
        except ValueError:
            logging.warning(f"Invalid user ID format in ADMIN_USER_IDS: {users_str}")
            return []
    
    def _load_env_overrides(self):
        """Load configuration overrides from environment variables"""
        # Cache overrides
        if cache_size := self._get_optional_env('CACHE_MAX_SIZE'):
            self.cache.max_size = int(cache_size)
        
        if cache_ttl := self._get_optional_env('CACHE_DEFAULT_TTL'):
            self.cache.default_ttl = int(cache_ttl)
        
        # Rate limit overrides
        if rate_limit_max := self._get_optional_env('RATE_LIMIT_MAX_REQUESTS'):
            self.rate_limit.max_requests = int(rate_limit_max)
        
        if rate_limit_window := self._get_optional_env('RATE_LIMIT_WINDOW'):
            self.rate_limit.window_seconds = int(rate_limit_window)
        
        # Logging overrides
        if log_level := self._get_optional_env('LOG_LEVEL'):
            self.logging.level = log_level.upper()
    
    def validate_config(self) -> bool:
        """Comprehensive configuration validation"""
        errors = []
        
        # Validate required tokens
        if not self.discord_token:
            errors.append("DISCORD_TOKEN is required")
        
        if not self.steam_api_key:
            errors.append("STEAM_API_KEY is required")
        
        # Validate Steam API key format (basic check)
        if self.steam_api_key and len(self.steam_api_key) < 10:
            errors.append("STEAM_API_KEY appears to be invalid (too short)")
        
        # Validate performance settings
        if self.max_concurrent_requests < 1:
            errors.append("MAX_CONCURRENT_REQUESTS must be at least 1")
        
        if self.request_timeout < 5:
            errors.append("REQUEST_TIMEOUT must be at least 5 seconds")
        
        if self.retry_attempts < 0:
            errors.append("RETRY_ATTEMPTS must be non-negative")
        
        # Validate cache settings
        if self.cache.max_size < 10:
            errors.append("Cache max_size must be at least 10")
        
        if self.cache.default_ttl < 60:
            errors.append("Cache default_ttl must be at least 60 seconds")
        
        # Validate rate limit settings
        if self.rate_limit.max_requests < 1:
            errors.append("Rate limit max_requests must be at least 1")
        
        if self.rate_limit.window_seconds < 10:
            errors.append("Rate limit window_seconds must be at least 10")
        
        # Report errors
        if errors:
            for error in errors:
                logging.error(f"Configuration error: {error}")
            return False
        
        return True
    
    def is_guild_allowed(self, guild_id: int) -> bool:
        """Check if a guild is allowed to use the bot"""
        if not self.allowed_guilds:
            return True  # Allow all if not restricted
        return guild_id in self.allowed_guilds
    
    def is_admin_user(self, user_id: int) -> bool:
        """Check if a user has admin privileges"""
        return user_id in self.admin_user_ids
    
    def get_steam_api_params(self) -> Dict[str, Any]:
        """Get Steam API configuration parameters"""
        return {
            'api_key': self.steam_api_key,
            'base_url': self.steam_api_base,
            'store_url': self.steam_store_base,
            'community_url': self.steam_community_base,
            'timeout': self.request_timeout,
            'retry_attempts': self.retry_attempts,
            'retry_delay': self.retry_delay
        }
    
    def get_cache_config(self) -> Dict[str, Any]:
        """Get cache configuration parameters"""
        return {
            'max_size': self.cache.max_size,
            'default_ttl': self.cache.default_ttl,
            'profile_ttl': self.cache.profile_ttl,
            'game_ttl': self.cache.game_ttl,
            'player_count_ttl': self.cache.player_count_ttl,
            'cleanup_interval': self.cache.cleanup_interval
        }
    
    def get_rate_limit_config(self) -> Dict[str, Any]:
        """Get rate limiting configuration parameters"""
        return {
            'max_requests': self.rate_limit.max_requests,
            'window_seconds': self.rate_limit.window_seconds,
            'burst_limit': self.rate_limit.burst_limit,
            'cooldown_seconds': self.rate_limit.cooldown_seconds
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary (excluding sensitive data)"""
        return {
            'steam_api_base': self.steam_api_base,
            'steam_store_base': self.steam_store_base,
            'steam_community_base': self.steam_community_base,
            'max_concurrent_requests': self.max_concurrent_requests,
            'request_timeout': self.request_timeout,
            'retry_attempts': self.retry_attempts,
            'retry_delay': self.retry_delay,
            'allowed_guilds': self.allowed_guilds,
            'enable_debug_mode': self.enable_debug_mode,
            'enable_caching': self.enable_caching,
            'enable_rate_limiting': self.enable_rate_limiting,
            'enable_analytics': self.enable_analytics,
            'cache': asdict(self.cache),
            'rate_limit': asdict(self.rate_limit),
            'logging': asdict(self.logging),
            'database': asdict(self.database)
        }
    
    def __str__(self) -> str:
        """String representation of configuration (excluding sensitive data)"""
        config_dict = self.to_dict()
        return f"OptimizedConfig({config_dict})"

# Global configuration instance
Config = OptimizedConfig()

# Validate configuration on import
if not Config.validate_config():
    raise ValueError("Configuration validation failed. Check the logs for details.")
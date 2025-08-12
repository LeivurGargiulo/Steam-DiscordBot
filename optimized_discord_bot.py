"""
Optimized Discord Bot for Steam API Integration

This module provides a production-ready Discord bot with:
- Efficient asynchronous event handling
- Comprehensive error handling and logging
- Rate limit management
- Intelligent caching system
- Modular code structure
- Performance optimizations
- Secure configuration management
"""

import discord
from discord.ext import commands, tasks
import asyncio
import logging
import time
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from functools import wraps
import aiohttp
import aioredis
from collections import defaultdict, deque
import hashlib

# Local imports
from steam_api import SteamAPI
from utils import *
from config import Config
from logging_config import setup_logging, log_command, log_api_call, log_error

# Setup logging
logger = setup_logging()

@dataclass
class CacheEntry:
    """Represents a cached item with metadata"""
    data: Any
    timestamp: float
    ttl: int
    access_count: int = 0
    last_accessed: float = 0.0

class RateLimiter:
    """Advanced rate limiter with sliding window and per-user tracking"""
    
    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(deque)
        self._lock = asyncio.Lock()
    
    async def is_allowed(self, user_id: int) -> bool:
        """Check if user is allowed to make a request"""
        async with self._lock:
            now = time.time()
            user_requests = self.requests[user_id]
            
            # Remove old requests outside the window
            while user_requests and now - user_requests[0] > self.window_seconds:
                user_requests.popleft()
            
            # Check if user has exceeded the limit
            if len(user_requests) >= self.max_requests:
                return False
            
            # Add current request
            user_requests.append(now)
            return True
    
    async def get_remaining_requests(self, user_id: int) -> int:
        """Get remaining requests for a user"""
        async with self._lock:
            now = time.time()
            user_requests = self.requests[user_id]
            
            # Remove old requests
            while user_requests and now - user_requests[0] > self.window_seconds:
                user_requests.popleft()
            
            return max(0, self.max_requests - len(user_requests))

class CacheManager:
    """Intelligent caching system with TTL and LRU eviction"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: Dict[str, CacheEntry] = {}
        self.access_order = deque()
        self._lock = asyncio.Lock()
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate a cache key from arguments"""
        key_data = f"{prefix}:{':'.join(map(str, args))}"
        if kwargs:
            key_data += f":{json.dumps(kwargs, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def get(self, prefix: str, *args, **kwargs) -> Optional[Any]:
        """Get item from cache"""
        key = self._generate_key(prefix, *args, **kwargs)
        
        async with self._lock:
            if key in self.cache:
                entry = self.cache[key]
                now = time.time()
                
                # Check if entry has expired
                if now - entry.timestamp > entry.ttl:
                    del self.cache[key]
                    self.access_order.remove(key)
                    return None
                
                # Update access metadata
                entry.access_count += 1
                entry.last_accessed = now
                
                # Move to end of access order (most recently used)
                self.access_order.remove(key)
                self.access_order.append(key)
                
                return entry.data
        
        return None
    
    async def set(self, prefix: str, data: Any, ttl: int = None, *args, **kwargs) -> None:
        """Set item in cache"""
        key = self._generate_key(prefix, *args, **kwargs)
        ttl = ttl or self.default_ttl
        
        async with self._lock:
            # Evict if cache is full
            if len(self.cache) >= self.max_size:
                self._evict_lru()
            
            # Add new entry
            self.cache[key] = CacheEntry(
                data=data,
                timestamp=time.time(),
                ttl=ttl,
                access_count=1,
                last_accessed=time.time()
            )
            self.access_order.append(key)
    
    def _evict_lru(self):
        """Evict least recently used item"""
        if self.access_order:
            lru_key = self.access_order.popleft()
            if lru_key in self.cache:
                del self.cache[lru_key]
    
    async def clear_expired(self):
        """Clear expired cache entries"""
        now = time.time()
        expired_keys = []
        
        async with self._lock:
            for key, entry in self.cache.items():
                if now - entry.timestamp > entry.ttl:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.cache[key]
                if key in self.access_order:
                    self.access_order.remove(key)

class OptimizedSteamAPI(SteamAPI):
    """Enhanced Steam API with caching and better error handling"""
    
    def __init__(self, cache_manager: CacheManager):
        super().__init__()
        self.cache = cache_manager
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session
    
    async def _make_async_request(self, url: str, params: Dict = None) -> Optional[Dict]:
        """Make async HTTP request with better error handling"""
        try:
            session = await self._get_session()
            async with session.get(url, params=params) as response:
                if response.status == 429:  # Rate limited
                    retry_after = int(response.headers.get('Retry-After', 60))
                    logger.warning(f"Rate limited by Steam API. Retrying after {retry_after} seconds")
                    await asyncio.sleep(retry_after)
                    return await self._make_async_request(url, params)
                
                response.raise_for_status()
                return await response.json()
                
        except aiohttp.ClientError as e:
            logger.error(f"HTTP request failed: {e}")
            return None
        except asyncio.TimeoutError:
            logger.error("Request timed out")
            return None
    
    async def get_user_profile_async(self, steam_id: str) -> Optional[Dict]:
        """Get user profile with caching"""
        # Check cache first
        cached = await self.cache.get("profile", steam_id)
        if cached:
            return cached
        
        # Make API request
        url = f"{self.base_url}/ISteamUser/GetPlayerSummaries/v2/"
        params = {
            'key': self.api_key,
            'steamids': steam_id
        }
        
        data = await self._make_async_request(url, params)
        if data and data.get('response', {}).get('players'):
            profile = data['response']['players'][0]
            # Cache for 5 minutes
            await self.cache.set("profile", profile, ttl=300, steam_id=steam_id)
            return profile
        
        return None
    
    async def get_game_details_async(self, app_id: str) -> Optional[Dict]:
        """Get game details with caching"""
        cached = await self.cache.get("game", app_id)
        if cached:
            return cached
        
        url = f"{self.store_url}/api/appdetails"
        params = {'appids': app_id}
        
        data = await self._make_async_request(url, params)
        if data and data.get(app_id, {}).get('success'):
            game_data = data[app_id]['data']
            # Cache for 1 hour (game data doesn't change often)
            await self.cache.set("game", game_data, ttl=3600, app_id=app_id)
            return game_data
        
        return None
    
    async def get_player_count_async(self, app_id: str) -> Optional[int]:
        """Get player count with short cache (frequently changing)"""
        cached = await self.cache.get("playercount", app_id)
        if cached:
            return cached
        
        url = f"{self.base_url}/ISteamUserStats/GetNumberOfCurrentPlayers/v1/"
        params = {'appid': app_id}
        
        data = await self._make_async_request(url, params)
        if data and data.get('response', {}).get('player_count') is not None:
            count = data['response']['player_count']
            # Cache for 2 minutes (player count changes frequently)
            await self.cache.set("playercount", count, ttl=120, app_id=app_id)
            return count
        
        return None

class OptimizedDiscordBot(commands.Bot):
    """Production-ready Discord bot with advanced features"""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None,
            max_messages=10000  # Increase message cache for better performance
        )
        
        # Initialize components
        self.cache_manager = CacheManager()
        self.rate_limiter = RateLimiter(max_requests=15, window_seconds=60)
        self.steam_api = OptimizedSteamAPI(self.cache_manager)
        
        # Bot statistics
        self.start_time = datetime.now()
        self.command_stats = defaultdict(int)
        self.error_stats = defaultdict(int)
        self.api_call_stats = defaultdict(int)
        
        # Performance tracking
        self.response_times = deque(maxlen=1000)
        
        # Start background tasks
        self.cleanup_task.start()
        self.stats_task.start()
        self.health_check_task.start()
    
    async def setup_hook(self):
        """Initialize bot components"""
        logger.info("Setting up optimized Discord bot...")
        
        # Load command cogs
        await self.add_cog(OptimizedSteamCommands(self))
        await self.add_cog(AdminCommands(self))
        await self.add_cog(PerformanceCommands(self))
        
        logger.info("Bot setup complete!")
    
    async def on_ready(self):
        """Handle bot ready event"""
        logger.info(f'Logged in as {self.user} (ID: {self.user.id})')
        logger.info(f'Connected to {len(self.guilds)} guilds')
        
        # Set bot status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="Steam profiles | !help"
            )
        )
        
        # Log startup statistics
        logger.info(f"Bot startup completed in {(datetime.now() - self.start_time).total_seconds():.2f}s")
    
    async def on_command_error(self, ctx, error):
        """Enhanced global error handler"""
        self.error_stats[type(error).__name__] += 1
        
        if isinstance(error, commands.CommandNotFound):
            return  # Ignore command not found
        
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Missing required argument: `{error.param.name}`\n"
                          f"Usage: `{ctx.prefix}{ctx.command.name} {ctx.command.signature}`")
        
        elif isinstance(error, commands.BadArgument):
            await ctx.send("❌ Invalid argument provided. Please check your input.")
        
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏰ Command is on cooldown. Try again in {error.retry_after:.1f} seconds.")
        
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have permission to use this command.")
        
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("❌ I don't have the required permissions to execute this command.")
        
        else:
            # Log detailed error
            log_error(error, f"Command error in {ctx.command.name if ctx.command else 'unknown'}")
            logger.error(f"Unexpected error: {error}", exc_info=True)
            
            # Send user-friendly error message
            await ctx.send("❌ An unexpected error occurred. Please try again later.")
    
    async def on_command(self, ctx):
        """Track command usage"""
        self.command_stats[ctx.command.name] += 1
    
    @tasks.loop(minutes=5)
    async def cleanup_task(self):
        """Periodic cleanup tasks"""
        try:
            # Clear expired cache entries
            await self.cache_manager.clear_expired()
            
            # Close old aiohttp sessions if needed
            if self.steam_api.session and self.steam_api.session.closed:
                self.steam_api.session = None
            
            logger.debug("Cleanup task completed")
            
        except Exception as e:
            logger.error(f"Error in cleanup task: {e}")
    
    @tasks.loop(minutes=10)
    async def stats_task(self):
        """Log periodic statistics"""
        try:
            uptime = datetime.now() - self.start_time
            total_commands = sum(self.command_stats.values())
            total_errors = sum(self.error_stats.values())
            
            logger.info(f"Bot Statistics - Uptime: {uptime}, "
                       f"Commands: {total_commands}, Errors: {total_errors}")
            
        except Exception as e:
            logger.error(f"Error in stats task: {e}")
    
    @tasks.loop(minutes=2)
    async def health_check_task(self):
        """Health check for bot components"""
        try:
            # Check cache health
            cache_size = len(self.cache_manager.cache)
            if cache_size > self.cache_manager.max_size * 0.9:
                logger.warning(f"Cache usage high: {cache_size}/{self.cache_manager.max_size}")
            
            # Check response times
            if self.response_times:
                avg_response_time = sum(self.response_times) / len(self.response_times)
                if avg_response_time > 5.0:  # 5 seconds
                    logger.warning(f"High average response time: {avg_response_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Error in health check: {e}")
    
    @cleanup_task.before_loop
    @stats_task.before_loop
    @health_check_task.before_loop
    async def before_background_tasks(self):
        """Wait until bot is ready before starting background tasks"""
        await self.wait_until_ready()

def rate_limit_check():
    """Decorator for rate limiting commands"""
    def decorator(func):
        @wraps(func)
        async def wrapper(self, ctx, *args, **kwargs):
            # Check rate limit
            if not await self.bot.rate_limiter.is_allowed(ctx.author.id):
                remaining = await self.bot.rate_limiter.get_remaining_requests(ctx.author.id)
                await ctx.send(f"⏰ Rate limit exceeded. Please wait before making more requests.")
                return
            
            # Execute command with timing
            start_time = time.time()
            try:
                result = await func(self, ctx, *args, **kwargs)
                return result
            finally:
                response_time = time.time() - start_time
                self.bot.response_times.append(response_time)
        
        return wrapper
    return decorator

class OptimizedSteamCommands(commands.Cog):
    """Optimized Steam commands with caching and rate limiting"""
    
    def __init__(self, bot: OptimizedDiscordBot):
        self.bot = bot
    
    @commands.command(name='start')
    async def start_command(self, ctx):
        """Welcome message with command overview"""
        welcome_embed = discord.Embed(
            title="🎮 Welcome to Optimized Steam Bot!",
            description="A high-performance Discord bot for Steam queries with intelligent caching and rate limiting.",
            color=discord.Color.blue()
        )
        
        welcome_embed.add_field(
            name="Profile & Games",
            value="• `!profile <steamid>` - Get user profile info\n"
                  "• `!library <steamid>` - List owned games\n"
                  "• `!recent <steamid>` - Recently played games\n"
                  "• `!achievements <steamid> <appid>` - Game achievements\n"
                  "• `!level <steamid>` - Steam level\n"
                  "• `!badges <steamid>` - User badges",
            inline=False
        )
        
        welcome_embed.add_field(
            name="Game Information",
            value="• `!game <appid>` - Game details\n"
                  "• `!playercount <appid>` - Current players\n"
                  "• `!news <appid>` - Game news\n"
                  "• `!topgames` - Trending games\n"
                  "• `!randomgame` - Random game suggestion",
            inline=False
        )
        
        welcome_embed.add_field(
            name="Performance Features",
            value="• Intelligent caching for faster responses\n"
                  "• Rate limiting to prevent API abuse\n"
                  "• Async processing for better performance\n"
                  "• Comprehensive error handling",
            inline=False
        )
        
        welcome_embed.set_footer(text="Use !help for more information | !stats for bot statistics")
        
        await ctx.send(embed=welcome_embed)
    
    @commands.command(name='help')
    async def help_command(self, ctx):
        """Show help information"""
        await self.start_command(ctx)
    
    @commands.command(name='profile')
    @rate_limit_check()
    async def profile_command(self, ctx, steam_id: str):
        """Get Steam user profile information with caching"""
        log_command(ctx, "!profile")
        
        if not validate_steam_id(steam_id):
            await ctx.send("❌ Invalid Steam ID format. Steam IDs are 17-digit numbers.")
            return
        
        # Send loading message
        loading_msg = await ctx.send("🔍 Fetching profile...")
        
        try:
            profile = await self.bot.steam_api.get_user_profile_async(steam_id)
            if not profile:
                await loading_msg.edit(content="❌ Profile not found or private.")
                return
            
            log_api_call("get_user_profile", {"steam_id": steam_id}, success=True)
            
            message = format_user_profile(profile)
            
            # Create embed
            embed = discord.Embed(
                title=f"🎮 Steam Profile: {profile.get('personaname', 'Unknown')}",
                description=message,
                color=discord.Color.green(),
                url=profile.get('profileurl', '')
            )
            
            if profile.get('avatarfull'):
                embed.set_thumbnail(url=profile.get('avatarfull'))
            
            # Add cache indicator
            embed.add_field(
                name="Performance",
                value="✅ Cached response" if await self.bot.cache_manager.get("profile", steam_id) else "🔄 Fresh data",
                inline=False
            )
            
            await loading_msg.edit(content="", embed=embed)
            
        except Exception as e:
            log_api_call("get_user_profile", {"steam_id": steam_id}, success=False, error=str(e))
            log_error(e, f"Profile command failed for Steam ID: {steam_id}")
            await loading_msg.edit(content="❌ Error fetching profile. Please try again later.")
    
    @commands.command(name='game')
    @rate_limit_check()
    async def game_command(self, ctx, app_id: str):
        """Get game details with caching"""
        if not validate_app_id(app_id):
            await ctx.send("❌ Invalid App ID format. App IDs are numeric.")
            return
        
        loading_msg = await ctx.send("🔍 Fetching game details...")
        
        try:
            game = await self.bot.steam_api.get_game_details_async(app_id)
            if not game:
                await loading_msg.edit(content="❌ Game not found.")
                return
            
            message = format_game_details(game)
            
            # Create embed
            embed = discord.Embed(
                title=f"🎮 {game.get('name', 'Unknown Game')}",
                description=message,
                color=discord.Color.blue(),
                url=f"https://store.steampowered.com/app/{app_id}"
            )
            
            if game.get('header_image'):
                embed.set_thumbnail(url=game.get('header_image'))
            
            # Add cache indicator
            embed.add_field(
                name="Performance",
                value="✅ Cached response" if await self.bot.cache_manager.get("game", app_id) else "🔄 Fresh data",
                inline=False
            )
            
            await loading_msg.edit(content="", embed=embed)
            
        except Exception as e:
            logger.error(f"Error fetching game: {e}")
            await loading_msg.edit(content="❌ Error fetching game details. Please try again later.")
    
    @commands.command(name='playercount')
    @rate_limit_check()
    async def playercount_command(self, ctx, app_id: str):
        """Get current player count with short-term caching"""
        if not validate_app_id(app_id):
            await ctx.send("❌ Invalid App ID format. App IDs are numeric.")
            return
        
        loading_msg = await ctx.send("🔍 Fetching player count...")
        
        try:
            count = await self.bot.steam_api.get_player_count_async(app_id)
            if count is None:
                await loading_msg.edit(content="❌ Could not fetch player count.")
                return
            
            embed = discord.Embed(
                title="👥 Current Players",
                description=f"**{count:,}** players currently online",
                color=discord.Color.green()
            )
            
            # Add cache indicator
            embed.add_field(
                name="Performance",
                value="✅ Cached response" if await self.bot.cache_manager.get("playercount", app_id) else "🔄 Fresh data",
                inline=False
            )
            
            await loading_msg.edit(content="", embed=embed)
            
        except Exception as e:
            logger.error(f"Error fetching player count: {e}")
            await loading_msg.edit(content="❌ Error fetching player count. Please try again later.")

class AdminCommands(commands.Cog):
    """Administrative commands for bot management"""
    
    def __init__(self, bot: OptimizedDiscordBot):
        self.bot = bot
    
    @commands.command(name='stats')
    @commands.has_permissions(manage_messages=True)
    async def stats_command(self, ctx):
        """Show bot statistics"""
        uptime = datetime.now() - self.bot.start_time
        total_commands = sum(self.bot.command_stats.values())
        total_errors = sum(self.bot.error_stats.values())
        
        embed = discord.Embed(
            title="📊 Bot Statistics",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="General",
            value=f"**Uptime:** {uptime.days}d {uptime.seconds//3600}h {(uptime.seconds//60)%60}m\n"
                  f"**Total Commands:** {total_commands}\n"
                  f"**Total Errors:** {total_errors}",
            inline=False
        )
        
        embed.add_field(
            name="Cache",
            value=f"**Cache Size:** {len(self.bot.cache_manager.cache)}/{self.bot.cache_manager.max_size}\n"
                  f"**Cache Usage:** {len(self.bot.cache_manager.cache)/self.bot.cache_manager.max_size*100:.1f}%",
            inline=True
        )
        
        if self.bot.response_times:
            avg_response = sum(self.bot.response_times) / len(self.bot.response_times)
            embed.add_field(
                name="Performance",
                value=f"**Avg Response Time:** {avg_response:.2f}s\n"
                      f"**Recent Responses:** {len(self.bot.response_times)}",
                inline=True
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='cache')
    @commands.has_permissions(administrator=True)
    async def cache_command(self, ctx, action: str = "info"):
        """Manage cache"""
        if action.lower() == "clear":
            self.bot.cache_manager.cache.clear()
            self.bot.cache_manager.access_order.clear()
            await ctx.send("✅ Cache cleared!")
        elif action.lower() == "info":
            cache_size = len(self.bot.cache_manager.cache)
            await ctx.send(f"📦 Cache Info: {cache_size}/{self.bot.cache_manager.max_size} entries")
        else:
            await ctx.send("❌ Invalid action. Use 'clear' or 'info'")

class PerformanceCommands(commands.Cog):
    """Commands for monitoring bot performance"""
    
    def __init__(self, bot: OptimizedDiscordBot):
        self.bot = bot
    
    @commands.command(name='ping')
    async def ping_command(self, ctx):
        """Check bot latency"""
        start_time = time.time()
        msg = await ctx.send("🏓 Pinging...")
        end_time = time.time()
        
        latency = (end_time - start_time) * 1000
        api_latency = self.latency * 1000
        
        embed = discord.Embed(
            title="🏓 Pong!",
            color=discord.Color.green()
        )
        
        embed.add_field(name="Bot Latency", value=f"{latency:.2f}ms", inline=True)
        embed.add_field(name="API Latency", value=f"{api_latency:.2f}ms", inline=True)
        
        await msg.edit(content="", embed=embed)

async def main():
    """Main function to run the optimized Discord bot"""
    # Validate configuration
    try:
        Config.validate_config()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return
    
    # Create and run bot
    bot = OptimizedDiscordBot()
    
    try:
        await bot.start(Config.DISCORD_TOKEN)
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested")
    except Exception as e:
        logger.error(f"Bot startup failed: {e}")
    finally:
        # Cleanup
        if bot.steam_api.session:
            await bot.steam_api.session.close()
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
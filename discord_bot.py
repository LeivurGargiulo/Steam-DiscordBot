import discord
from discord.ext import commands, tasks
import asyncio
import logging
import time
from datetime import datetime, timedelta
from steam_api import SteamAPI
from utils import *
from config import Config
from logging_config import setup_logging, log_command, log_api_call, log_error

# Setup logging
logger = setup_logging()

class SteamDiscordBot(commands.Bot):
    """Main Discord bot class with Steam API integration"""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None  # We'll create our own help command
        )
        
        self.steam_api = SteamAPI()
        self.start_time = datetime.now()
        self.error_count = 0
        self.command_count = 0
        
        # Background task for periodic cleanup
        self.cleanup_task.start()
    
    async def setup_hook(self):
        """Called when the bot is starting up"""
        logger.info("Setting up Discord bot...")
        
        # Load all command cogs
        await self.add_cog(SteamCommands(self))
        await self.add_cog(AdminCommands(self))
        
        logger.info("Discord bot setup complete!")
    
    async def on_ready(self):
        """Called when the bot is ready"""
        logger.info(f'Logged in as {self.user} (ID: {self.user.id})')
        logger.info(f'Connected to {len(self.guilds)} guilds')
        
        # Set bot status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="Steam profiles | !help"
            )
        )
    
    async def on_command_error(self, ctx, error):
        """Global error handler for commands"""
        self.error_count += 1
        
        if isinstance(error, commands.CommandNotFound):
            return  # Ignore command not found errors
        
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Missing required argument: `{error.param.name}`")
        
        elif isinstance(error, commands.BadArgument):
            await ctx.send("❌ Invalid argument provided. Please check your input.")
        
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏰ Command is on cooldown. Try again in {error.retry_after:.1f} seconds.")
        
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have permission to use this command.")
        
        else:
            # Log the error
            log_error(error, f"Command error in {ctx.command.name if ctx.command else 'unknown'}")
            
            # Send user-friendly error message
            await ctx.send("❌ An unexpected error occurred. Please try again later.")
            
            # Log detailed error for debugging
            logger.error(f"Command error: {error}", exc_info=True)
    
    async def on_command(self, ctx):
        """Called when a command is executed successfully"""
        self.command_count += 1
    
    @tasks.loop(hours=1)
    async def cleanup_task(self):
        """Background task for periodic cleanup"""
        try:
            # Clean up any temporary data, cache, etc.
            logger.debug("Running periodic cleanup task")
            
            # You can add more cleanup logic here
            # For example, clearing old cache entries, etc.
            
        except Exception as e:
            logger.error(f"Error in cleanup task: {e}")
    
    @cleanup_task.before_loop
    async def before_cleanup_task(self):
        """Wait until the bot is ready before starting the cleanup task"""
        await self.wait_until_ready()

class SteamCommands(commands.Cog):
    """Cog containing all Steam-related commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='start')
    async def start_command(self, ctx):
        """Welcome message and command overview"""
        welcome_embed = discord.Embed(
            title="🎮 Welcome to Steam Bot!",
            description="I can help you with various Steam-related queries.",
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
            name="Social Features",
            value="• `!friends <steamid>` - Friends list\n"
                  "• `!compare <steamid1> <steamid2>` - Compare users",
            inline=False
        )
        
        welcome_embed.add_field(
            name="Examples",
            value="• `!profile 76561198000000000`\n"
                  "• `!game 730` (CS2)\n"
                  "• `!playercount 730`",
            inline=False
        )
        
        welcome_embed.set_footer(text="Need help? Use !help for more information!")
        
        await ctx.send(embed=welcome_embed)
    
    @commands.command(name='help')
    async def help_command(self, ctx):
        """Show help information"""
        await self.start_command(ctx)
    
    @commands.command(name='profile')
    @commands.cooldown(1, 5, commands.BucketType.user)  # 1 use per 5 seconds per user
    async def profile_command(self, ctx, steam_id: str):
        """Get Steam user profile information"""
        log_command(ctx, "!profile")
        
        if not validate_steam_id(steam_id):
            await ctx.send("❌ Invalid Steam ID format. Steam IDs are 17-digit numbers.")
            return
        
        # Send loading message
        loading_msg = await ctx.send("🔍 Fetching profile...")
        
        try:
            profile = self.bot.steam_api.get_user_profile(steam_id)
            log_api_call("get_user_profile", {"steam_id": steam_id}, success=True)
            
            message = format_user_profile(profile)
            
            # Create embed for better formatting
            embed = discord.Embed(
                title=f"🎮 Steam Profile: {profile.get('personaname', 'Unknown')}",
                description=message,
                color=discord.Color.green(),
                url=profile.get('profileurl', '')
            )
            
            if profile.get('avatarfull'):
                embed.set_thumbnail(url=profile.get('avatarfull'))
            
            await loading_msg.edit(content="", embed=embed)
            
        except Exception as e:
            log_api_call("get_user_profile", {"steam_id": steam_id}, success=False, error=str(e))
            log_error(e, f"Profile command failed for Steam ID: {steam_id}")
            await loading_msg.edit(content="❌ Error fetching profile. Please try again later.")
    
    @commands.command(name='game')
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def game_command(self, ctx, app_id: str):
        """Get game details"""
        if not validate_app_id(app_id):
            await ctx.send("❌ Invalid App ID format. App IDs are numeric.")
            return
        
        loading_msg = await ctx.send("🔍 Fetching game details...")
        
        try:
            game = self.bot.steam_api.get_game_details(app_id)
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
            
            await loading_msg.edit(content="", embed=embed)
            
        except Exception as e:
            logger.error(f"Error fetching game: {e}")
            await loading_msg.edit(content="❌ Error fetching game details. Please try again later.")
    
    @commands.command(name='library')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def library_command(self, ctx, steam_id: str):
        """Get user's owned games"""
        if not validate_steam_id(steam_id):
            await ctx.send("❌ Invalid Steam ID format. Steam IDs are 17-digit numbers.")
            return
        
        loading_msg = await ctx.send("🔍 Fetching library...")
        
        try:
            games = self.bot.steam_api.get_owned_games(steam_id)
            message = format_owned_games(games)
            
            # Split long messages if needed
            if len(message) > 2000:
                chunks = [message[i:i+1900] for i in range(0, len(message), 1900)]
                await loading_msg.delete()
                for i, chunk in enumerate(chunks):
                    await ctx.send(f"📚 Library (Part {i+1}/{len(chunks)}):\n{chunk}")
            else:
                await loading_msg.edit(content=message)
                
        except Exception as e:
            logger.error(f"Error fetching library: {e}")
            await loading_msg.edit(content="❌ Error fetching library. Please try again later.")
    
    @commands.command(name='recent')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def recent_command(self, ctx, steam_id: str):
        """Get recently played games"""
        if not validate_steam_id(steam_id):
            await ctx.send("❌ Invalid Steam ID format. Steam IDs are 17-digit numbers.")
            return
        
        loading_msg = await ctx.send("🔍 Fetching recent games...")
        
        try:
            recent = self.bot.steam_api.get_recent_games(steam_id)
            message = format_recent_games(recent)
            await loading_msg.edit(content=message)
            
        except Exception as e:
            logger.error(f"Error fetching recent games: {e}")
            await loading_msg.edit(content="❌ Error fetching recent games. Please try again later.")
    
    @commands.command(name='achievements')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def achievements_command(self, ctx, steam_id: str, app_id: str):
        """Get user's achievements for a specific game"""
        if not validate_steam_id(steam_id):
            await ctx.send("❌ Invalid Steam ID format. Steam IDs are 17-digit numbers.")
            return
        
        if not validate_app_id(app_id):
            await ctx.send("❌ Invalid App ID format. App IDs are numeric.")
            return
        
        loading_msg = await ctx.send("🔍 Fetching achievements...")
        
        try:
            achievements = self.bot.steam_api.get_player_achievements(steam_id, app_id)
            schema = self.bot.steam_api.get_game_schema(app_id)
            message = format_achievements(achievements, schema)
            await loading_msg.edit(content=message)
            
        except Exception as e:
            logger.error(f"Error fetching achievements: {e}")
            await loading_msg.edit(content="❌ Error fetching achievements. Please try again later.")
    
    @commands.command(name='playercount')
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def playercount_command(self, ctx, app_id: str):
        """Get current player count for a game"""
        if not validate_app_id(app_id):
            await ctx.send("❌ Invalid App ID format. App IDs are numeric.")
            return
        
        loading_msg = await ctx.send("🔍 Fetching player count...")
        
        try:
            count = self.bot.steam_api.get_player_count(app_id)
            if count is not None:
                game = self.bot.steam_api.get_game_details(app_id)
                game_name = game.get('name', 'Unknown Game') if game else 'Unknown Game'
                
                embed = discord.Embed(
                    title=f"👥 {game_name}",
                    description=f"🎮 **Current Players:** {count:,}",
                    color=discord.Color.green()
                )
                
                await loading_msg.edit(content="", embed=embed)
            else:
                await loading_msg.edit(content="❌ Could not fetch player count for this game.")
                
        except Exception as e:
            logger.error(f"Error fetching player count: {e}")
            await loading_msg.edit(content="❌ Error fetching player count. Please try again later.")
    
    @commands.command(name='news')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def news_command(self, ctx, app_id: str):
        """Get game news"""
        if not validate_app_id(app_id):
            await ctx.send("❌ Invalid App ID format. App IDs are numeric.")
            return
        
        loading_msg = await ctx.send("🔍 Fetching news...")
        
        try:
            news = self.bot.steam_api.get_app_news(app_id)
            message = format_news(news)
            
            # Split long messages if needed
            if len(message) > 2000:
                chunks = [message[i:i+1900] for i in range(0, len(message), 1900)]
                await loading_msg.delete()
                for i, chunk in enumerate(chunks):
                    await ctx.send(f"📰 News (Part {i+1}/{len(chunks)}):\n{chunk}")
            else:
                await loading_msg.edit(content=message)
                
        except Exception as e:
            logger.error(f"Error fetching news: {e}")
            await loading_msg.edit(content="❌ Error fetching news. Please try again later.")
    
    @commands.command(name='friends')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def friends_command(self, ctx, steam_id: str):
        """Get user's friends list"""
        if not validate_steam_id(steam_id):
            await ctx.send("❌ Invalid Steam ID format. Steam IDs are 17-digit numbers.")
            return
        
        loading_msg = await ctx.send("🔍 Fetching friends list...")
        
        try:
            friends = self.bot.steam_api.get_friend_list(steam_id)
            message = format_friends_list(friends)
            await loading_msg.edit(content=message)
            
        except Exception as e:
            logger.error(f"Error fetching friends: {e}")
            await loading_msg.edit(content="❌ Error fetching friends list. Please try again later.")
    
    @commands.command(name='topgames')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def topgames_command(self, ctx):
        """Get top trending games"""
        loading_msg = await ctx.send("🔍 Fetching top games...")
        
        try:
            featured = self.bot.steam_api.get_featured_games()
            if featured and featured.get('featured_win'):
                games = featured['featured_win'].get('items', [])
                
                embed = discord.Embed(
                    title="🔥 Top Games on Steam",
                    color=discord.Color.orange()
                )
                
                for i, game in enumerate(games[:10], 1):
                    name = game.get('name', 'Unknown')
                    app_id = game.get('id', 'Unknown')
                    embed.add_field(
                        name=f"{i}. {name}",
                        value=f"App ID: {app_id}",
                        inline=False
                    )
                
                await loading_msg.edit(content="", embed=embed)
            else:
                await loading_msg.edit(content="❌ Could not fetch top games.")
                
        except Exception as e:
            logger.error(f"Error fetching top games: {e}")
            await loading_msg.edit(content="❌ Error fetching top games. Please try again later.")
    
    @commands.command(name='randomgame')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def randomgame_command(self, ctx):
        """Get a random game suggestion"""
        loading_msg = await ctx.send("🎲 Finding a random game...")
        
        try:
            game = self.bot.steam_api.get_random_game()
            if game:
                name = game.get('name', 'Unknown')
                app_id = game.get('id', 'Unknown')
                
                # Get more details about the game
                game_details = self.bot.steam_api.get_game_details(app_id)
                if game_details:
                    message = format_game_details(game_details)
                    
                    embed = discord.Embed(
                        title=f"🎮 Random Game: {name}",
                        description=message,
                        color=discord.Color.purple(),
                        url=f"https://store.steampowered.com/app/{app_id}"
                    )
                    
                    if game_details.get('header_image'):
                        embed.set_thumbnail(url=game_details.get('header_image'))
                    
                    await loading_msg.edit(content="", embed=embed)
                else:
                    embed = discord.Embed(
                        title=f"🎮 Random Game: {name}",
                        description=f"App ID: {app_id}",
                        color=discord.Color.purple()
                    )
                    await loading_msg.edit(content="", embed=embed)
            else:
                await loading_msg.edit(content="❌ Could not find a random game.")
                
        except Exception as e:
            logger.error(f"Error getting random game: {e}")
            await loading_msg.edit(content="❌ Error getting random game. Please try again later.")
    
    @commands.command(name='compare')
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def compare_command(self, ctx, steam_id1: str, steam_id2: str):
        """Compare two Steam users"""
        if not validate_steam_id(steam_id1) or not validate_steam_id(steam_id2):
            await ctx.send("❌ Invalid Steam ID format. Steam IDs are 17-digit numbers.")
            return
        
        loading_msg = await ctx.send("🔍 Comparing users...")
        
        try:
            user1_games = self.bot.steam_api.get_owned_games(steam_id1)
            user2_games = self.bot.steam_api.get_owned_games(steam_id2)
            
            message = format_comparison(user1_games, user2_games, steam_id1, steam_id2)
            
            # Split long messages if needed
            if len(message) > 2000:
                chunks = [message[i:i+1900] for i in range(0, len(message), 1900)]
                await loading_msg.delete()
                for i, chunk in enumerate(chunks):
                    await ctx.send(f"📊 Comparison (Part {i+1}/{len(chunks)}):\n{chunk}")
            else:
                await loading_msg.edit(content=message)
                
        except Exception as e:
            logger.error(f"Error comparing users: {e}")
            await loading_msg.edit(content="❌ Error comparing users. Please try again later.")
    
    @commands.command(name='level')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def level_command(self, ctx, steam_id: str):
        """Get user's Steam level"""
        if not validate_steam_id(steam_id):
            await ctx.send("❌ Invalid Steam ID format. Steam IDs are 17-digit numbers.")
            return
        
        loading_msg = await ctx.send("🔍 Fetching Steam level...")
        
        try:
            level = self.bot.steam_api.get_user_level(steam_id)
            if level is not None:
                profile = self.bot.steam_api.get_user_profile(steam_id)
                name = profile.get('personaname', 'Unknown') if profile else 'Unknown'
                
                embed = discord.Embed(
                    title="📊 Steam Level",
                    description=f"👤 **User:** {name}\n⭐ **Level:** {level}",
                    color=discord.Color.gold()
                )
                
                await loading_msg.edit(content="", embed=embed)
            else:
                await loading_msg.edit(content="❌ Could not fetch Steam level. Profile might be private.")
                
        except Exception as e:
            logger.error(f"Error fetching level: {e}")
            await loading_msg.edit(content="❌ Error fetching Steam level. Please try again later.")
    
    @commands.command(name='badges')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def badges_command(self, ctx, steam_id: str):
        """Get user's badges"""
        if not validate_steam_id(steam_id):
            await ctx.send("❌ Invalid Steam ID format. Steam IDs are 17-digit numbers.")
            return
        
        loading_msg = await ctx.send("🔍 Fetching badges...")
        
        try:
            badges = self.bot.steam_api.get_badges(steam_id)
            message = format_badges(badges)
            await loading_msg.edit(content=message)
            
        except Exception as e:
            logger.error(f"Error fetching badges: {e}")
            await loading_msg.edit(content="❌ Error fetching badges. Please try again later.")

class AdminCommands(commands.Cog):
    """Cog containing admin and utility commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='debug')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def debug_command(self, ctx):
        """Show bot debug information"""
        uptime = datetime.now() - self.bot.start_time
        uptime_str = str(uptime).split('.')[0]  # Remove microseconds
        
        embed = discord.Embed(
            title="🔧 Bot Debug Information",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="📊 Statistics",
            value=f"**Uptime:** {uptime_str}\n"
                  f"**Commands Used:** {self.bot.command_count}\n"
                  f"**Errors:** {self.bot.error_count}\n"
                  f"**Servers:** {len(self.bot.guilds)}\n"
                  f"**Users:** {len(self.bot.users)}",
            inline=False
        )
        
        embed.add_field(
            name="⚙️ System Info",
            value=f"**Latency:** {round(self.bot.latency * 1000)}ms\n"
                  f"**Python Version:** {discord.__version__}\n"
                  f"**Discord.py Version:** {discord.__version__}",
            inline=False
        )
        
        embed.add_field(
            name="🔗 Links",
            value="[GitHub Repository](https://github.com/your-repo)\n"
                  "[Support Server](https://discord.gg/your-server)",
            inline=False
        )
        
        embed.set_footer(text=f"Requested by {ctx.author.display_name}")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='ping')
    async def ping_command(self, ctx):
        """Check bot latency"""
        latency = round(self.bot.latency * 1000)
        
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"**Latency:** {latency}ms",
            color=discord.Color.green() if latency < 100 else discord.Color.orange() if latency < 200 else discord.Color.red()
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='info')
    async def info_command(self, ctx):
        """Show bot information"""
        embed = discord.Embed(
            title="ℹ️ Steam Bot Information",
            description="A comprehensive Discord bot that integrates with the Steam Web API to provide various Steam-related features and information.",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="🎮 Features",
            value="• Steam profile information\n"
                  "• Game details and statistics\n"
                  "• Player counts and achievements\n"
                  "• Friends lists and comparisons\n"
                  "• News and recommendations",
            inline=False
        )
        
        embed.add_field(
            name="📝 Commands",
            value="Use `!help` to see all available commands",
            inline=False
        )
        
        embed.set_footer(text="Made with ❤️ using discord.py")
        
        await ctx.send(embed=embed)


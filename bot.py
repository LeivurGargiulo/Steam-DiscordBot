import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
from steam_api import SteamAPI
from utils import *
from config import Config
from logging_config import setup_logging, log_command, log_api_call, log_error

# Setup logging
logger = setup_logging()

class SteamTelegramBot:
    """Main Telegram bot class with Steam API integration"""
    
    def __init__(self):
        self.steam_api = SteamAPI()
        self.application = None
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = """
🎮 **Welcome to Steam Bot!**

I can help you with various Steam-related queries. Here are some commands:

**Profile & Games:**
• `/profile <steamid>` - Get user profile info
• `/library <steamid>` - List owned games
• `/recent <steamid>` - Recently played games
• `/achievements <steamid> <appid>` - Game achievements
• `/level <steamid>` - Steam level
• `/badges <steamid>` - User badges

**Game Information:**
• `/game <appid>` - Game details
• `/playercount <appid>` - Current players
• `/news <appid>` - Game news
• `/topgames` - Trending games
• `/randomgame` - Random game suggestion

**Social Features:**
• `/friends <steamid>` - Friends list
• `/compare <steamid1> <steamid2>` - Compare users

**Other Features:**
• `/wishlist <steamid>` - Wishlist (if public)
• `/recommend <steamid>` - Game recommendations
• `/pricehistory <appid>` - Price history (placeholder)

**Examples:**
• `/profile 76561198000000000`
• `/game 730` (CS2)
• `/playercount 730`

Need help? Just ask!
        """
        
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        await self.start(update, context)
    
    async def profile_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /profile command"""
        log_command(update, "/profile")
        
        if not context.args:
            await update.message.reply_text("❌ Please provide a Steam ID.\nUsage: `/profile <steamid>`", parse_mode='Markdown')
            return
        
        steam_id = context.args[0]
        if not validate_steam_id(steam_id):
            await update.message.reply_text("❌ Invalid Steam ID format. Steam IDs are 17-digit numbers.")
            return
        
        await update.message.reply_text("🔍 Fetching profile...")
        
        try:
            profile = self.steam_api.get_user_profile(steam_id)
            log_api_call("get_user_profile", {"steam_id": steam_id}, success=True)
            message = format_user_profile(profile)
            await update.message.reply_text(message, parse_mode='Markdown', disable_web_page_preview=True)
        except Exception as e:
            log_api_call("get_user_profile", {"steam_id": steam_id}, success=False, error=str(e))
            log_error(e, f"Profile command failed for Steam ID: {steam_id}")
            await update.message.reply_text("❌ Error fetching profile. Please try again later.")
    
    async def game_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /game command"""
        if not context.args:
            await update.message.reply_text("❌ Please provide a game App ID.\nUsage: `/game <appid>`", parse_mode='Markdown')
            return
        
        app_id = context.args[0]
        if not validate_app_id(app_id):
            await update.message.reply_text("❌ Invalid App ID format. App IDs are numeric.")
            return
        
        await update.message.reply_text("🔍 Fetching game details...")
        
        try:
            game = self.steam_api.get_game_details(app_id)
            message = format_game_details(game)
            await update.message.reply_text(message, parse_mode='Markdown', disable_web_page_preview=True)
        except Exception as e:
            logger.error(f"Error fetching game: {e}")
            await update.message.reply_text("❌ Error fetching game details. Please try again later.")
    
    async def library_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /library command"""
        if not context.args:
            await update.message.reply_text("❌ Please provide a Steam ID.\nUsage: `/library <steamid>`", parse_mode='Markdown')
            return
        
        steam_id = context.args[0]
        if not validate_steam_id(steam_id):
            await update.message.reply_text("❌ Invalid Steam ID format. Steam IDs are 17-digit numbers.")
            return
        
        await update.message.reply_text("🔍 Fetching library...")
        
        try:
            games = self.steam_api.get_owned_games(steam_id)
            message = format_owned_games(games)
            await update.message.reply_text(message, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Error fetching library: {e}")
            await update.message.reply_text("❌ Error fetching library. Please try again later.")
    
    async def recent_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /recent command"""
        if not context.args:
            await update.message.reply_text("❌ Please provide a Steam ID.\nUsage: `/recent <steamid>`", parse_mode='Markdown')
            return
        
        steam_id = context.args[0]
        if not validate_steam_id(steam_id):
            await update.message.reply_text("❌ Invalid Steam ID format. Steam IDs are 17-digit numbers.")
            return
        
        await update.message.reply_text("🔍 Fetching recent games...")
        
        try:
            recent = self.steam_api.get_recent_games(steam_id)
            message = format_recent_games(recent)
            await update.message.reply_text(message, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Error fetching recent games: {e}")
            await update.message.reply_text("❌ Error fetching recent games. Please try again later.")
    
    async def achievements_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /achievements command"""
        if len(context.args) < 2:
            await update.message.reply_text("❌ Please provide Steam ID and App ID.\nUsage: `/achievements <steamid> <appid>`", parse_mode='Markdown')
            return
        
        steam_id = context.args[0]
        app_id = context.args[1]
        
        if not validate_steam_id(steam_id):
            await update.message.reply_text("❌ Invalid Steam ID format. Steam IDs are 17-digit numbers.")
            return
        
        if not validate_app_id(app_id):
            await update.message.reply_text("❌ Invalid App ID format. App IDs are numeric.")
            return
        
        await update.message.reply_text("🔍 Fetching achievements...")
        
        try:
            achievements = self.steam_api.get_player_achievements(steam_id, app_id)
            schema = self.steam_api.get_game_schema(app_id)
            message = format_achievements(achievements, schema)
            await update.message.reply_text(message, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Error fetching achievements: {e}")
            await update.message.reply_text("❌ Error fetching achievements. Please try again later.")
    
    async def playercount_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /playercount command"""
        if not context.args:
            await update.message.reply_text("❌ Please provide a game App ID.\nUsage: `/playercount <appid>`", parse_mode='Markdown')
            return
        
        app_id = context.args[0]
        if not validate_app_id(app_id):
            await update.message.reply_text("❌ Invalid App ID format. App IDs are numeric.")
            return
        
        await update.message.reply_text("🔍 Fetching player count...")
        
        try:
            count = self.steam_api.get_player_count(app_id)
            if count is not None:
                game = self.steam_api.get_game_details(app_id)
                game_name = game.get('name', 'Unknown Game') if game else 'Unknown Game'
                message = f"👥 **{game_name}**\n\n🎮 **Current Players:** {count:,}"
                await update.message.reply_text(message, parse_mode='Markdown')
            else:
                await update.message.reply_text("❌ Could not fetch player count for this game.")
        except Exception as e:
            logger.error(f"Error fetching player count: {e}")
            await update.message.reply_text("❌ Error fetching player count. Please try again later.")
    
    async def news_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /news command"""
        if not context.args:
            await update.message.reply_text("❌ Please provide a game App ID.\nUsage: `/news <appid>`", parse_mode='Markdown')
            return
        
        app_id = context.args[0]
        if not validate_app_id(app_id):
            await update.message.reply_text("❌ Invalid App ID format. App IDs are numeric.")
            return
        
        await update.message.reply_text("🔍 Fetching news...")
        
        try:
            news = self.steam_api.get_app_news(app_id)
            message = format_news(news)
            await update.message.reply_text(message, parse_mode='Markdown', disable_web_page_preview=True)
        except Exception as e:
            logger.error(f"Error fetching news: {e}")
            await update.message.reply_text("❌ Error fetching news. Please try again later.")
    
    async def friends_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /friends command"""
        if not context.args:
            await update.message.reply_text("❌ Please provide a Steam ID.\nUsage: `/friends <steamid>`", parse_mode='Markdown')
            return
        
        steam_id = context.args[0]
        if not validate_steam_id(steam_id):
            await update.message.reply_text("❌ Invalid Steam ID format. Steam IDs are 17-digit numbers.")
            return
        
        await update.message.reply_text("🔍 Fetching friends list...")
        
        try:
            friends = self.steam_api.get_friend_list(steam_id)
            message = format_friends_list(friends)
            await update.message.reply_text(message, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Error fetching friends: {e}")
            await update.message.reply_text("❌ Error fetching friends list. Please try again later.")
    
    async def wishlist_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /wishlist command (placeholder)"""
        if not context.args:
            await update.message.reply_text("❌ Please provide a Steam ID.\nUsage: `/wishlist <steamid>`", parse_mode='Markdown')
            return
        
        steam_id = context.args[0]
        if not validate_steam_id(steam_id):
            await update.message.reply_text("❌ Invalid Steam ID format. Steam IDs are 17-digit numbers.")
            return
        
        message = f"📋 **Wishlist for {steam_id}**\n\n"
        message += "⚠️ **Note:** Steam doesn't provide a public API for wishlists.\n"
        message += "This feature would require:\n"
        message += "• Public profile access\n"
        message += "• Web scraping of Steam profile pages\n"
        message += "• Third-party service integration\n\n"
        message += "For now, this is a placeholder feature."
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def topgames_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /topgames command"""
        await update.message.reply_text("🔍 Fetching top games...")
        
        try:
            featured = self.steam_api.get_featured_games()
            if featured and featured.get('featured_win'):
                games = featured['featured_win'].get('items', [])
                
                message = "🔥 **Top Games on Steam**\n\n"
                for i, game in enumerate(games[:10], 1):
                    name = game.get('name', 'Unknown')
                    app_id = game.get('id', 'Unknown')
                    message += f"{i}. **{name}** (ID: {app_id})\n"
                
                await update.message.reply_text(message, parse_mode='Markdown')
            else:
                await update.message.reply_text("❌ Could not fetch top games.")
        except Exception as e:
            logger.error(f"Error fetching top games: {e}")
            await update.message.reply_text("❌ Error fetching top games. Please try again later.")
    
    async def recommend_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /recommend command"""
        if not context.args:
            await update.message.reply_text("❌ Please provide a Steam ID.\nUsage: `/recommend <steamid>`", parse_mode='Markdown')
            return
        
        steam_id = context.args[0]
        if not validate_steam_id(steam_id):
            await update.message.reply_text("❌ Invalid Steam ID format. Steam IDs are 17-digit numbers.")
            return
        
        await update.message.reply_text("🔍 Generating recommendations...")
        
        try:
            recommendations = self.steam_api.get_game_recommendations(steam_id)
            if recommendations:
                message = "🎯 **Game Recommendations**\n\n"
                for i, game in enumerate(recommendations, 1):
                    name = game.get('name', 'Unknown')
                    app_id = game.get('id', 'Unknown')
                    message += f"{i}. **{name}** (ID: {app_id})\n"
                
                await update.message.reply_text(message, parse_mode='Markdown')
            else:
                await update.message.reply_text("❌ Could not generate recommendations. Profile might be private.")
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            await update.message.reply_text("❌ Error generating recommendations. Please try again later.")
    
    async def compare_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /compare command"""
        if len(context.args) < 2:
            await update.message.reply_text("❌ Please provide two Steam IDs.\nUsage: `/compare <steamid1> <steamid2>`", parse_mode='Markdown')
            return
        
        steam_id1 = context.args[0]
        steam_id2 = context.args[1]
        
        if not validate_steam_id(steam_id1) or not validate_steam_id(steam_id2):
            await update.message.reply_text("❌ Invalid Steam ID format. Steam IDs are 17-digit numbers.")
            return
        
        await update.message.reply_text("🔍 Comparing users...")
        
        try:
            user1_games = self.steam_api.get_owned_games(steam_id1)
            user2_games = self.steam_api.get_owned_games(steam_id2)
            
            message = format_comparison(user1_games, user2_games, steam_id1, steam_id2)
            await update.message.reply_text(message, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Error comparing users: {e}")
            await update.message.reply_text("❌ Error comparing users. Please try again later.")
    
    async def level_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /level command"""
        if not context.args:
            await update.message.reply_text("❌ Please provide a Steam ID.\nUsage: `/level <steamid>`", parse_mode='Markdown')
            return
        
        steam_id = context.args[0]
        if not validate_steam_id(steam_id):
            await update.message.reply_text("❌ Invalid Steam ID format. Steam IDs are 17-digit numbers.")
            return
        
        await update.message.reply_text("🔍 Fetching Steam level...")
        
        try:
            level = self.steam_api.get_user_level(steam_id)
            if level is not None:
                profile = self.steam_api.get_user_profile(steam_id)
                name = profile.get('personaname', 'Unknown') if profile else 'Unknown'
                message = f"📊 **Steam Level**\n\n👤 **User:** {name}\n⭐ **Level:** {level}"
                await update.message.reply_text(message, parse_mode='Markdown')
            else:
                await update.message.reply_text("❌ Could not fetch Steam level. Profile might be private.")
        except Exception as e:
            logger.error(f"Error fetching level: {e}")
            await update.message.reply_text("❌ Error fetching Steam level. Please try again later.")
    
    async def badges_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /badges command"""
        if not context.args:
            await update.message.reply_text("❌ Please provide a Steam ID.\nUsage: `/badges <steamid>`", parse_mode='Markdown')
            return
        
        steam_id = context.args[0]
        if not validate_steam_id(steam_id):
            await update.message.reply_text("❌ Invalid Steam ID format. Steam IDs are 17-digit numbers.")
            return
        
        await update.message.reply_text("🔍 Fetching badges...")
        
        try:
            badges = self.steam_api.get_badges(steam_id)
            message = format_badges(badges)
            await update.message.reply_text(message, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Error fetching badges: {e}")
            await update.message.reply_text("❌ Error fetching badges. Please try again later.")
    
    async def pricehistory_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /pricehistory command (placeholder)"""
        if not context.args:
            await update.message.reply_text("❌ Please provide a game App ID.\nUsage: `/pricehistory <appid>`", parse_mode='Markdown')
            return
        
        app_id = context.args[0]
        if not validate_app_id(app_id):
            await update.message.reply_text("❌ Invalid App ID format. App IDs are numeric.")
            return
        
        message = f"📈 **Price History for Game {app_id}**\n\n"
        message += "⚠️ **Note:** Steam doesn't provide price history via API.\n"
        message += "This feature would require:\n"
        message += "• Third-party API integration (SteamDB, SteamSpy)\n"
        message += "• Web scraping of price tracking sites\n"
        message += "• Historical data collection\n\n"
        message += "For now, this is a placeholder feature."
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def randomgame_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /randomgame command"""
        await update.message.reply_text("🎲 Finding a random game...")
        
        try:
            game = self.steam_api.get_random_game()
            if game:
                name = game.get('name', 'Unknown')
                app_id = game.get('id', 'Unknown')
                
                # Get more details about the game
                game_details = self.steam_api.get_game_details(app_id)
                if game_details:
                    message = format_game_details(game_details)
                else:
                    message = f"🎮 **Random Game: {name}**\n\nApp ID: {app_id}"
                
                await update.message.reply_text(message, parse_mode='Markdown', disable_web_page_preview=True)
            else:
                await update.message.reply_text("❌ Could not find a random game.")
        except Exception as e:
            logger.error(f"Error getting random game: {e}")
            await update.message.reply_text("❌ Error getting random game. Please try again later.")
    
    async def sale_alerts_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle sale alerts (placeholder)"""
        message = "💰 **Steam Sale Alerts**\n\n"
        message += "⚠️ **Note:** This feature would require:\n"
        message += "• Monitoring Steam sales\n"
        message += "• User preference storage\n"
        message += "• Automated notifications\n"
        message += "• Price tracking integration\n\n"
        message += "For now, this is a placeholder feature."
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def leaderboard_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle leaderboard command (placeholder)"""
        message = "🏆 **Game Hours Leaderboard**\n\n"
        message += "⚠️ **Note:** This feature would require:\n"
        message += "• Group chat integration\n"
        message += "• User data storage\n"
        message += "• Periodic updates\n"
        message += "• Leaderboard calculations\n\n"
        message += "For now, this is a placeholder feature."
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def new_releases_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle new releases alerts (placeholder)"""
        message = "🆕 **New Release Alerts**\n\n"
        message += "⚠️ **Note:** This feature would require:\n"
        message += "• Monitoring new releases\n"
        message += "• Genre preference tracking\n"
        message += "• Automated notifications\n"
        message += "• Release date tracking\n\n"
        message += "For now, this is a placeholder feature."
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def trade_offers_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle trade offer notifications (placeholder)"""
        message = "🤝 **Trade Offer Notifications**\n\n"
        message += "⚠️ **Note:** This feature would require:\n"
        message += "• Steam trading API access\n"
        message += "• User authentication\n"
        message += "• Real-time monitoring\n"
        message += "• Secure token handling\n\n"
        message += "For now, this is a placeholder feature."
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    def setup_handlers(self):
        """Setup all command handlers"""
        handlers = [
            CommandHandler("start", self.start),
            CommandHandler("help", self.help_command),
            CommandHandler("profile", self.profile_command),
            CommandHandler("game", self.game_command),
            CommandHandler("library", self.library_command),
            CommandHandler("recent", self.recent_command),
            CommandHandler("achievements", self.achievements_command),
            CommandHandler("playercount", self.playercount_command),
            CommandHandler("news", self.news_command),
            CommandHandler("friends", self.friends_command),
            CommandHandler("wishlist", self.wishlist_command),
            CommandHandler("topgames", self.topgames_command),
            CommandHandler("recommend", self.recommend_command),
            CommandHandler("compare", self.compare_command),
            CommandHandler("level", self.level_command),
            CommandHandler("badges", self.badges_command),
            CommandHandler("pricehistory", self.pricehistory_command),
            CommandHandler("randomgame", self.randomgame_command),
            CommandHandler("salealerts", self.sale_alerts_command),
            CommandHandler("leaderboard", self.leaderboard_command),
            CommandHandler("newreleases", self.new_releases_command),
            CommandHandler("tradeoffers", self.trade_offers_command),
        ]
        
        for handler in handlers:
            self.application.add_handler(handler)
    
    async def run(self):
        """Run the bot"""
        # Validate configuration
        Config.validate_config()
        
        # Create application
        self.application = Application.builder().token(Config.TELEGRAM_TOKEN).build()
        
        # Setup handlers
        self.setup_handlers()
        
        # Start the bot
        logger.info("Starting Steam Telegram Bot...")
        await self.application.run_polling()
#!/usr/bin/env python3
"""
Steam Discord Bot - Main Entry Point

A comprehensive Discord bot that integrates with the Steam Web API
to provide various Steam-related features and information.

Author: Steam Bot Developer
Version: 1.0.0
"""

import asyncio
import sys
import logging
from discord_bot import SteamDiscordBot
from logging_config import setup_logging, cleanup_logs

async def main():
    """Main function to run the Steam Discord Bot"""
    logger = setup_logging()
    
    try:
        logger.info("Starting Steam Discord Bot...")
        
        # Clean up old logs
        cleanup_logs()
        
        # Create and run the bot
        from config import Config
        bot = SteamDiscordBot()
        await bot.start(Config.DISCORD_TOKEN)
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user (KeyboardInterrupt)")
        print("\n🛑 Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Critical error running bot: {e}", exc_info=True)
        print(f"❌ Error running bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Run the bot
    asyncio.run(main())
#!/usr/bin/env python3
"""
Optimized Steam Discord Bot Startup Script

This script provides a production-ready startup process with:
- Proper initialization of all components
- Graceful error handling and recovery
- Health monitoring and restart capabilities
- Configuration validation
- Performance optimization
"""

import asyncio
import sys
import signal
import os
import time
from pathlib import Path
from typing import Optional

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from optimized_discord_bot import OptimizedDiscordBot
    from optimized_config import Config
    from optimized_logging import initialize_logging, get_log_manager
    from optimized_steam_api import OptimizedSteamAPI
except ImportError as e:
    print(f"Error importing optimized modules: {e}")
    print("Please ensure all optimized_*.py files are in the project directory")
    sys.exit(1)

class BotManager:
    """Manages the Discord bot lifecycle with monitoring and recovery"""
    
    def __init__(self):
        self.bot: Optional[OptimizedDiscordBot] = None
        self.logger = None
        self.log_manager = None
        self.start_time = None
        self.restart_count = 0
        self.max_restarts = 5
        self.restart_delay = 30  # seconds
        
        # Signal handling
        self.shutdown_requested = False
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        print(f"\nReceived signal {signum}. Shutting down gracefully...")
        self.shutdown_requested = True
        if self.bot:
            asyncio.create_task(self.bot.close())
    
    async def initialize_logging(self):
        """Initialize the logging system"""
        try:
            config = {
                'log_level': Config.logging.level,
                'log_dir': 'logs',
                'enable_json': True,
                'enable_metrics': True,
                'max_file_size': Config.logging.max_file_size,
                'backup_count': Config.logging.backup_count
            }
            
            self.logger, metrics, self.log_manager = initialize_logging(config)
            self.logger.info("Logging system initialized successfully")
            
        except Exception as e:
            print(f"Failed to initialize logging: {e}")
            sys.exit(1)
    
    async def validate_configuration(self):
        """Validate all configuration settings"""
        try:
            if not Config.validate_config():
                raise ValueError("Configuration validation failed")
            
            self.logger.info("Configuration validated successfully")
            self.logger.info(f"Bot will connect to Discord with token: {Config.discord_token[:10]}...")
            self.logger.info(f"Steam API key configured: {Config.steam_api_key[:10]}...")
            
        except Exception as e:
            self.logger.error(f"Configuration validation failed: {e}")
            raise
    
    async def create_bot(self):
        """Create and configure the Discord bot"""
        try:
            self.bot = OptimizedDiscordBot()
            self.logger.info("Discord bot instance created successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to create bot instance: {e}")
            raise
    
    async def start_bot(self):
        """Start the Discord bot"""
        try:
            self.start_time = time.time()
            self.logger.info("Starting Discord bot...")
            
            await self.bot.start(Config.discord_token)
            
        except Exception as e:
            self.logger.error(f"Failed to start bot: {e}")
            raise
    
    async def run_bot(self):
        """Main bot running loop with monitoring"""
        try:
            while not self.shutdown_requested:
                try:
                    # Start the bot
                    await self.start_bot()
                    
                    # Keep the bot running
                    await self.bot.wait_closed()
                    
                    if self.shutdown_requested:
                        break
                    
                    # Handle unexpected shutdown
                    self.logger.warning("Bot disconnected unexpectedly")
                    
                    if self.restart_count < self.max_restarts:
                        self.restart_count += 1
                        self.logger.info(f"Restarting bot (attempt {self.restart_count}/{self.max_restarts})")
                        await asyncio.sleep(self.restart_delay)
                    else:
                        self.logger.error("Maximum restart attempts reached. Shutting down.")
                        break
                        
                except Exception as e:
                    self.logger.error(f"Error in bot main loop: {e}")
                    if self.restart_count < self.max_restarts:
                        self.restart_count += 1
                        self.logger.info(f"Restarting after error (attempt {self.restart_count}/{self.max_restarts})")
                        await asyncio.sleep(self.restart_delay)
                    else:
                        self.logger.error("Maximum restart attempts reached after errors. Shutting down.")
                        break
                        
        except Exception as e:
            self.logger.error(f"Critical error in bot manager: {e}")
            raise
    
    async def shutdown(self):
        """Graceful shutdown of the bot"""
        try:
            self.logger.info("Initiating graceful shutdown...")
            
            if self.bot:
                await self.bot.close()
            
            # Log final statistics
            if self.log_manager:
                summary = self.log_manager.get_summary()
                self.logger.info(f"Final statistics: {summary}")
            
            self.logger.info("Shutdown completed successfully")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
    
    async def health_check(self):
        """Periodic health check"""
        try:
            if self.bot and self.log_manager:
                # Check bot health
                if not self.bot.is_ready():
                    self.logger.warning("Bot is not ready")
                
                # Check for alerts
                alerts = self.log_manager.check_alerts()
                if alerts:
                    self.logger.warning(f"Health alerts: {alerts}")
                
                # Log performance metrics
                if self.start_time:
                    uptime = time.time() - self.start_time
                    self.logger.info(f"Bot uptime: {uptime:.0f} seconds")
                
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")

async def main():
    """Main entry point"""
    manager = BotManager()
    
    try:
        # Initialize logging first
        await manager.initialize_logging()
        manager.logger.info("=" * 80)
        manager.logger.info("Optimized Steam Discord Bot Starting")
        manager.logger.info("=" * 80)
        
        # Validate configuration
        await manager.validate_configuration()
        
        # Create bot instance
        await manager.create_bot()
        
        # Start health check task
        health_task = asyncio.create_task(periodic_health_check(manager))
        
        # Run the bot
        await manager.run_bot()
        
    except KeyboardInterrupt:
        manager.logger.info("Received keyboard interrupt")
    except Exception as e:
        if manager.logger:
            manager.logger.error(f"Critical error: {e}")
        else:
            print(f"Critical error: {e}")
    finally:
        # Cleanup
        await manager.shutdown()
        
        # Cancel health check task
        if 'health_task' in locals():
            health_task.cancel()
            try:
                await health_task
            except asyncio.CancelledError:
                pass

async def periodic_health_check(manager: BotManager):
    """Run periodic health checks"""
    while not manager.shutdown_requested:
        try:
            await asyncio.sleep(300)  # Check every 5 minutes
            await manager.health_check()
        except asyncio.CancelledError:
            break
        except Exception as e:
            if manager.logger:
                manager.logger.error(f"Health check error: {e}")

def check_environment():
    """Check if the environment is properly set up"""
    print("Checking environment...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        return False
    
    # Check for .env file
    if not Path('.env').exists():
        print("Warning: .env file not found. Please create one with your configuration.")
        return False
    
    # Check for required directories
    Path('logs').mkdir(exist_ok=True)
    
    print("Environment check completed.")
    return True

if __name__ == "__main__":
    # Check environment before starting
    if not check_environment():
        sys.exit(1)
    
    # Set up asyncio policy for better performance
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    else:
        # Use uvloop on Unix systems for better performance
        try:
            import uvloop
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
            print("Using uvloop for enhanced performance")
        except ImportError:
            print("uvloop not available, using standard event loop")
    
    # Run the bot
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
import logging
import logging.handlers
import os
from datetime import datetime

def setup_logging():
    """Setup comprehensive logging for the Steam Telegram Bot"""
    
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Clear any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Console handler (INFO level)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    # File handler for all logs (DEBUG level)
    all_logs_handler = logging.handlers.RotatingFileHandler(
        'logs/steam_bot.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    all_logs_handler.setLevel(logging.DEBUG)
    all_logs_handler.setFormatter(detailed_formatter)
    logger.addHandler(all_logs_handler)
    
    # File handler for errors only
    error_handler = logging.handlers.RotatingFileHandler(
        'logs/steam_bot_errors.log',
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    logger.addHandler(error_handler)
    
    # File handler for API calls
    api_handler = logging.handlers.RotatingFileHandler(
        'logs/steam_bot_api.log',
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    api_handler.setLevel(logging.INFO)
    api_handler.setFormatter(detailed_formatter)
    
    # Create API logger
    api_logger = logging.getLogger('steam_api')
    api_logger.setLevel(logging.INFO)
    api_logger.addHandler(api_handler)
    
    # Create bot logger
    bot_logger = logging.getLogger('steam_bot')
    bot_logger.setLevel(logging.INFO)
    
    # Log startup
    logging.info("=" * 60)
    logging.info("Steam Telegram Bot Starting")
    logging.info(f"Startup Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info("=" * 60)
    
    return logger

def log_command(update, command):
    """Log user commands for analytics"""
    user_id = update.effective_user.id if update.effective_user else 'Unknown'
    username = update.effective_user.username if update.effective_user else 'Unknown'
    chat_id = update.effective_chat.id if update.effective_chat else 'Unknown'
    
    logging.info(f"Command executed - User: {user_id} (@{username}) Chat: {chat_id} Command: {command}")

def log_api_call(api_name, params=None, success=True, error=None):
    """Log API calls for monitoring"""
    api_logger = logging.getLogger('steam_api')
    
    if success:
        api_logger.info(f"API Call Success - {api_name} - Params: {params}")
    else:
        api_logger.error(f"API Call Failed - {api_name} - Params: {params} - Error: {error}")

def log_error(error, context=None):
    """Log errors with context"""
    logging.error(f"Error occurred: {error}")
    if context:
        logging.error(f"Context: {context}")
    
    # Log to error file
    error_logger = logging.getLogger('steam_bot_errors')
    error_logger.error(f"Error: {error} - Context: {context}")

def cleanup_logs():
    """Clean up old log files"""
    import glob
    import time
    
    # Remove logs older than 30 days
    current_time = time.time()
    log_files = glob.glob('logs/*.log.*')
    
    for log_file in log_files:
        if os.path.getmtime(log_file) < current_time - (30 * 24 * 60 * 60):
            try:
                os.remove(log_file)
                logging.info(f"Removed old log file: {log_file}")
            except OSError as e:
                logging.warning(f"Could not remove old log file {log_file}: {e}")
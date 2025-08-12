"""
Optimized Logging Configuration

This module provides comprehensive logging setup with:
- Structured logging with JSON format
- Performance monitoring and metrics
- Error tracking and alerting
- Log rotation and archival
- Different log levels for different components
- Async logging for better performance
"""

import logging
import logging.handlers
import json
import os
import sys
import time
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import threading
from pathlib import Path

@dataclass
class LogMetrics:
    """Logging metrics for monitoring"""
    total_logs: int = 0
    error_count: int = 0
    warning_count: int = 0
    info_count: int = 0
    debug_count: int = 0
    api_calls: int = 0
    command_executions: int = 0
    response_times: deque = None
    
    def __post_init__(self):
        if self.response_times is None:
            self.response_times = deque(maxlen=1000)
    
    def add_log(self, level: str):
        """Add a log entry to metrics"""
        self.total_logs += 1
        if level == 'ERROR':
            self.error_count += 1
        elif level == 'WARNING':
            self.warning_count += 1
        elif level == 'INFO':
            self.info_count += 1
        elif level == 'DEBUG':
            self.debug_count += 1
    
    def add_api_call(self, response_time: float):
        """Add API call metrics"""
        self.api_calls += 1
        self.response_times.append(response_time)
    
    def add_command(self):
        """Add command execution metric"""
        self.command_executions += 1
    
    def get_error_rate(self) -> float:
        """Calculate error rate"""
        return self.error_count / self.total_logs if self.total_logs > 0 else 0
    
    def get_avg_response_time(self) -> float:
        """Calculate average response time"""
        return sum(self.response_times) / len(self.response_times) if self.response_times else 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary"""
        return {
            'total_logs': self.total_logs,
            'error_count': self.error_count,
            'warning_count': self.warning_count,
            'info_count': self.info_count,
            'debug_count': self.debug_count,
            'api_calls': self.api_calls,
            'command_executions': self.command_executions,
            'error_rate': self.get_error_rate(),
            'avg_response_time': self.get_avg_response_time(),
            'recent_response_times': list(self.response_times)[-10:] if self.response_times else []
        }

class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add extra fields if present
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry, ensure_ascii=False)
    
    def formatException(self, exc_info):
        """Format exception information"""
        return ''.join(self.formatException(exc_info))

class MetricsHandler(logging.Handler):
    """Handler that tracks logging metrics"""
    
    def __init__(self, metrics: LogMetrics):
        super().__init__()
        self.metrics = metrics
    
    def emit(self, record: logging.LogRecord):
        """Emit log record and update metrics"""
        self.metrics.add_log(record.levelname)

class AsyncLogHandler(logging.Handler):
    """Asynchronous log handler for better performance"""
    
    def __init__(self, target_handler: logging.Handler):
        super().__init__()
        self.target_handler = target_handler
        self.queue = asyncio.Queue()
        self.worker_task = None
        self._start_worker()
    
    def _start_worker(self):
        """Start the async worker task"""
        if self.worker_task is None or self.worker_task.done():
            self.worker_task = asyncio.create_task(self._worker())
    
    async def _worker(self):
        """Worker task to process log records"""
        while True:
            try:
                record = await self.queue.get()
                self.target_handler.emit(record)
                self.queue.task_done()
            except Exception as e:
                # Fallback to synchronous logging if async fails
                print(f"Async logging failed: {e}")
                self.target_handler.emit(record)
    
    def emit(self, record: logging.LogRecord):
        """Emit log record to async queue"""
        try:
            # Schedule the record for async processing
            asyncio.create_task(self.queue.put(record))
        except Exception:
            # Fallback to synchronous processing
            self.target_handler.emit(record)

class PerformanceFilter(logging.Filter):
    """Filter to track performance-related logs"""
    
    def __init__(self, metrics: LogMetrics):
        super().__init__()
        self.metrics = metrics
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Filter and track performance logs"""
        if 'response_time' in record.getMessage():
            try:
                # Extract response time from log message
                import re
                match = re.search(r'(\d+\.?\d*)s', record.getMessage())
                if match:
                    response_time = float(match.group(1))
                    self.metrics.add_api_call(response_time)
            except (ValueError, AttributeError):
                pass
        
        if 'command' in record.getMessage().lower():
            self.metrics.add_command()
        
        return True

def setup_optimized_logging(
    log_level: str = "INFO",
    log_dir: str = "logs",
    enable_json: bool = True,
    enable_metrics: bool = True,
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> tuple[logging.Logger, LogMetrics]:
    """Setup comprehensive logging system"""
    
    # Create logs directory
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Initialize metrics
    metrics = LogMetrics()
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create formatters
    if enable_json:
        json_formatter = JSONFormatter()
        console_formatter = JSONFormatter()  # Use JSON for console too
    else:
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        console_formatter = simple_formatter
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handlers with rotation
    handlers = []
    
    # All logs file
    all_logs_handler = logging.handlers.RotatingFileHandler(
        log_path / 'steam_bot_all.log',
        maxBytes=max_file_size,
        backupCount=backup_count,
        encoding='utf-8'
    )
    all_logs_handler.setLevel(logging.DEBUG)
    all_logs_handler.setFormatter(json_formatter if enable_json else detailed_formatter)
    handlers.append(all_logs_handler)
    
    # Error logs file
    error_handler = logging.handlers.RotatingFileHandler(
        log_path / 'steam_bot_errors.log',
        maxBytes=max_file_size,
        backupCount=backup_count,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(json_formatter if enable_json else detailed_formatter)
    handlers.append(error_handler)
    
    # API calls file
    api_handler = logging.handlers.RotatingFileHandler(
        log_path / 'steam_bot_api.log',
        maxBytes=max_file_size,
        backupCount=backup_count,
        encoding='utf-8'
    )
    api_handler.setLevel(logging.INFO)
    api_handler.setFormatter(json_formatter if enable_json else detailed_formatter)
    
    # Create API logger
    api_logger = logging.getLogger('steam_api')
    api_logger.setLevel(logging.INFO)
    api_logger.addHandler(api_handler)
    api_logger.propagate = False  # Don't propagate to root logger
    
    # Commands file
    commands_handler = logging.handlers.RotatingFileHandler(
        log_path / 'steam_bot_commands.log',
        maxBytes=max_file_size,
        backupCount=backup_count,
        encoding='utf-8'
    )
    commands_handler.setLevel(logging.INFO)
    commands_handler.setFormatter(json_formatter if enable_json else detailed_formatter)
    
    # Create commands logger
    commands_logger = logging.getLogger('steam_commands')
    commands_logger.setLevel(logging.INFO)
    commands_logger.addHandler(commands_handler)
    commands_logger.propagate = False
    
    # Performance file
    performance_handler = logging.handlers.RotatingFileHandler(
        log_path / 'steam_bot_performance.log',
        maxBytes=max_file_size,
        backupCount=backup_count,
        encoding='utf-8'
    )
    performance_handler.setLevel(logging.INFO)
    performance_handler.setFormatter(json_formatter if enable_json else detailed_formatter)
    
    # Create performance logger
    performance_logger = logging.getLogger('steam_performance')
    performance_logger.setLevel(logging.INFO)
    performance_logger.addHandler(performance_handler)
    performance_logger.propagate = False
    
    # Add handlers to root logger
    for handler in handlers:
        root_logger.addHandler(handler)
    
    # Add metrics tracking if enabled
    if enable_metrics:
        metrics_handler = MetricsHandler(metrics)
        metrics_handler.setLevel(logging.DEBUG)
        root_logger.addHandler(metrics_handler)
        
        # Add performance filter
        performance_filter = PerformanceFilter(metrics)
        root_logger.addFilter(performance_filter)
    
    # Log startup
    startup_logger = logging.getLogger('startup')
    startup_logger.info("=" * 80)
    startup_logger.info("Optimized Steam Bot Starting")
    startup_logger.info(f"Startup Time: {datetime.now().isoformat()}")
    startup_logger.info(f"Log Level: {log_level}")
    startup_logger.info(f"JSON Logging: {enable_json}")
    startup_logger.info(f"Metrics Enabled: {enable_metrics}")
    startup_logger.info(f"Log Directory: {log_path.absolute()}")
    startup_logger.info("=" * 80)
    
    return root_logger, metrics

def log_command(context, command: str, extra_fields: Dict[str, Any] = None):
    """Log user commands with structured data"""
    logger = logging.getLogger('steam_commands')
    
    # Extract context information
    if hasattr(context, 'author'):  # Discord context
        user_id = context.author.id if context.author else 'Unknown'
        username = context.author.display_name if context.author else 'Unknown'
        guild_id = context.guild.id if context.guild else 'Unknown'
        channel_id = context.channel.id if context.channel else 'Unknown'
        platform = 'Discord'
    elif hasattr(context, 'effective_user'):  # Telegram context
        user_id = context.effective_user.id if context.effective_user else 'Unknown'
        username = context.effective_user.username if context.effective_user else 'Unknown'
        guild_id = context.effective_chat.id if context.effective_chat else 'Unknown'
        channel_id = context.effective_chat.id if context.effective_chat else 'Unknown'
        platform = 'Telegram'
    else:
        user_id = 'Unknown'
        username = 'Unknown'
        guild_id = 'Unknown'
        channel_id = 'Unknown'
        platform = 'Unknown'
    
    # Create structured log entry
    log_data = {
        'command': command,
        'user_id': user_id,
        'username': username,
        'guild_id': guild_id,
        'channel_id': channel_id,
        'platform': platform,
        'timestamp': datetime.now().isoformat()
    }
    
    if extra_fields:
        log_data.update(extra_fields)
    
    # Create log record with extra fields
    record = logging.LogRecord(
        name='steam_commands',
        level=logging.INFO,
        pathname='',
        lineno=0,
        msg=f"Command executed: {command}",
        args=(),
        exc_info=None
    )
    record.extra_fields = log_data
    
    logger.handle(record)

def log_api_call(
    endpoint: str, 
    params: Dict[str, Any], 
    success: bool = True, 
    error: str = None,
    response_time: float = None
):
    """Log API calls with structured data"""
    logger = logging.getLogger('steam_api')
    
    log_data = {
        'endpoint': endpoint,
        'params': params,
        'success': success,
        'response_time': response_time,
        'timestamp': datetime.now().isoformat()
    }
    
    if error:
        log_data['error'] = error
    
    # Create log record
    record = logging.LogRecord(
        name='steam_api',
        level=logging.ERROR if not success else logging.INFO,
        pathname='',
        lineno=0,
        msg=f"API call to {endpoint}: {'SUCCESS' if success else 'FAILED'}",
        args=(),
        exc_info=None
    )
    record.extra_fields = log_data
    
    logger.handle(record)

def log_error(error: Exception, context: str = None, extra_fields: Dict[str, Any] = None):
    """Log errors with structured data"""
    logger = logging.getLogger('steam_errors')
    
    log_data = {
        'error_type': type(error).__name__,
        'error_message': str(error),
        'context': context,
        'timestamp': datetime.now().isoformat()
    }
    
    if extra_fields:
        log_data.update(extra_fields)
    
    # Create log record
    record = logging.LogRecord(
        name='steam_errors',
        level=logging.ERROR,
        pathname='',
        lineno=0,
        msg=f"Error in {context}: {error}",
        args=(),
        exc_info=(type(error), error, error.__traceback__)
    )
    record.extra_fields = log_data
    
    logger.handle(record)

def log_performance(operation: str, duration: float, extra_fields: Dict[str, Any] = None):
    """Log performance metrics"""
    logger = logging.getLogger('steam_performance')
    
    log_data = {
        'operation': operation,
        'duration': duration,
        'timestamp': datetime.now().isoformat()
    }
    
    if extra_fields:
        log_data.update(extra_fields)
    
    # Create log record
    record = logging.LogRecord(
        name='steam_performance',
        level=logging.INFO,
        pathname='',
        lineno=0,
        msg=f"Performance: {operation} took {duration:.3f}s",
        args=(),
        exc_info=None
    )
    record.extra_fields = log_data
    
    logger.handle(record)

class LogManager:
    """Centralized log management with metrics and monitoring"""
    
    def __init__(self, metrics: LogMetrics):
        self.metrics = metrics
        self.start_time = datetime.now()
        self.alert_thresholds = {
            'error_rate': 0.1,  # 10% error rate
            'avg_response_time': 5.0,  # 5 seconds
            'consecutive_errors': 5
        }
        self.consecutive_errors = 0
    
    def check_alerts(self) -> List[str]:
        """Check for alert conditions"""
        alerts = []
        
        # Check error rate
        error_rate = self.metrics.get_error_rate()
        if error_rate > self.alert_thresholds['error_rate']:
            alerts.append(f"High error rate: {error_rate:.2%}")
        
        # Check response time
        avg_response_time = self.metrics.get_avg_response_time()
        if avg_response_time > self.alert_thresholds['avg_response_time']:
            alerts.append(f"High average response time: {avg_response_time:.2f}s")
        
        # Check consecutive errors
        if self.consecutive_errors >= self.alert_thresholds['consecutive_errors']:
            alerts.append(f"Consecutive errors: {self.consecutive_errors}")
        
        return alerts
    
    def get_summary(self) -> Dict[str, Any]:
        """Get logging summary"""
        uptime = datetime.now() - self.start_time
        
        return {
            'uptime': str(uptime),
            'uptime_seconds': uptime.total_seconds(),
            'metrics': self.metrics.to_dict(),
            'alerts': self.check_alerts()
        }
    
    def reset_metrics(self):
        """Reset metrics counters"""
        self.metrics = LogMetrics()
        self.consecutive_errors = 0
        logging.info("Log metrics reset")

# Global log manager instance
log_manager = None

def get_log_manager() -> Optional[LogManager]:
    """Get global log manager instance"""
    return log_manager

def initialize_logging(config: Dict[str, Any] = None) -> tuple[logging.Logger, LogMetrics, LogManager]:
    """Initialize the complete logging system"""
    global log_manager
    
    if config is None:
        config = {
            'log_level': 'INFO',
            'log_dir': 'logs',
            'enable_json': True,
            'enable_metrics': True
        }
    
    logger, metrics = setup_optimized_logging(**config)
    log_manager = LogManager(metrics)
    
    return logger, metrics, log_manager
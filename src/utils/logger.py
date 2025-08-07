"""
Centralized logging utility for the financial recommendation system.

Provides consistent logging configuration and utilities to replace print statements
with proper structured logging.
"""

import logging
import sys
from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path

from src.config import config


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for better readability"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        # Add color to the level name
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        
        return super().format(record)


class LoggerFactory:
    """Factory for creating configured loggers"""
    
    _loggers: Dict[str, logging.Logger] = {}
    
    @staticmethod
    def get_logger(name: str, level: str = "INFO", use_colors: bool = True) -> logging.Logger:
        """
        Get or create a logger with consistent configuration.
        
        Args:
            name: Logger name (usually __name__)
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            use_colors: Whether to use colored output
            
        Returns:
            Configured logger instance
        """
        if name in LoggerFactory._loggers:
            return LoggerFactory._loggers[name]
        
        # Create logger
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, level.upper()))
        
        # Avoid duplicate handlers
        if logger.handlers:
            return logger
        
        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level.upper()))
        
        # Create formatter
        if use_colors:
            formatter = ColoredFormatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # Create file handler for persistent logs
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        file_handler = logging.FileHandler(
            log_dir / f"{name.replace('.', '_')}.log",
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Store logger
        LoggerFactory._loggers[name] = logger
        
        return logger
    
    @staticmethod
    def get_performance_logger(name: str = "performance") -> logging.Logger:
        """Get a specialized logger for performance metrics"""
        logger = LoggerFactory.get_logger(name, "INFO")
        logger.propagate = False  # Prevent duplicate logs
        
        # Add performance-specific formatter
        perf_formatter = logging.Formatter(
            '%(asctime)s - PERFORMANCE - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        for handler in logger.handlers:
            handler.setFormatter(perf_formatter)
        
        return logger
    
    @staticmethod
    def get_error_logger(name: str = "errors") -> logging.Logger:
        """Get a specialized logger for error tracking"""
        logger = LoggerFactory.get_logger(name, "ERROR")
        logger.propagate = False  # Prevent duplicate logs
        
        # Add error-specific formatter
        error_formatter = logging.Formatter(
            '%(asctime)s - ERROR - %(name)s - %(levelname)s - %(message)s\n'
            'Exception: %(exc_info)s\n'
            'Stack Trace: %(stack_info)s\n',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        for handler in logger.handlers:
            handler.setFormatter(error_formatter)
        
        return logger


class LoggingMixin:
    """Mixin class to add logging capabilities to any class"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = LoggerFactory.get_logger(self.__class__.__name__)
    
    def log_info(self, message: str, **kwargs):
        """Log info message with optional context"""
        if kwargs:
            message = f"{message} - {kwargs}"
        self.logger.info(message)
    
    def log_warning(self, message: str, **kwargs):
        """Log warning message with optional context"""
        if kwargs:
            message = f"{message} - {kwargs}"
        self.logger.warning(message)
    
    def log_error(self, message: str, error: Optional[Exception] = None, **kwargs):
        """Log error message with optional exception and context"""
        if error:
            message = f"{message} - Error: {str(error)}"
        if kwargs:
            message = f"{message} - {kwargs}"
        self.logger.error(message, exc_info=error is not None)
    
    def log_debug(self, message: str, **kwargs):
        """Log debug message with optional context"""
        if kwargs:
            message = f"{message} - {kwargs}"
        self.logger.debug(message)
    
    def log_performance(self, operation: str, duration: float, **kwargs):
        """Log performance metrics"""
        perf_logger = LoggerFactory.get_performance_logger()
        message = f"{operation} took {duration:.3f}s"
        if kwargs:
            message = f"{message} - {kwargs}"
        perf_logger.info(message)


def setup_logging(level: str = "INFO", use_colors: bool = True) -> None:
    """
    Set up global logging configuration.
    
    Args:
        level: Global logging level
        use_colors: Whether to use colored output
    """
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    
    # Create formatter
    if use_colors:
        formatter = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Create file handler for all logs
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    file_handler = logging.FileHandler(
        log_dir / "application.log",
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)


def log_function_call(func_name: str, **kwargs):
    """Decorator to log function calls with parameters"""
    def decorator(func):
        def wrapper(*args, **func_kwargs):
            logger = LoggerFactory.get_logger(func.__module__)
            logger.debug(f"Calling {func_name} with args: {args}, kwargs: {func_kwargs}")
            try:
                result = func(*args, **func_kwargs)
                logger.debug(f"{func_name} completed successfully")
                return result
            except Exception as e:
                logger.error(f"{func_name} failed with error: {str(e)}", exc_info=True)
                raise
        return wrapper
    return decorator


def log_execution_time(operation_name: str):
    """Decorator to log execution time of functions"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = LoggerFactory.get_logger(func.__module__)
            start_time = datetime.now()
            
            try:
                result = func(*args, **kwargs)
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                logger.info(f"{operation_name} completed in {duration:.3f}s")
                return result
            except Exception as e:
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                logger.error(f"{operation_name} failed after {duration:.3f}s with error: {str(e)}", exc_info=True)
                raise
        return wrapper
    return decorator


# Initialize logging on module import
setup_logging()

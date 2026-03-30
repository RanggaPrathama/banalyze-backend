import logging
import sys
import os
from datetime import datetime
from typing import Optional
from app.core.config import settings


# Custom colored formatter
class ColoredFormatter(logging.Formatter):
    """Custom formatter dengan ANSI color codes"""
    
    FORMATS = {
        logging.DEBUG: f"\33[37m[DEBUG] %(name)s: %(message)s\33[0m",      # White
        logging.INFO: f"\33[36m[INFO] %(name)s: %(message)s\33[0m",       # Cyan
        logging.WARNING: f"\33[33m[WARNING] %(name)s: %(message)s\33[0m",    # Yellow
        logging.ERROR: f"\33[31m[ERROR] %(name)s: %(message)s\33[0m",      # Red
        logging.CRITICAL: f"\33[1m\33[31m[CRITICAL] %(name)s: %(message)s\33[0m",  # Bold Red
    }

    def format(self, record):
        log_format = self.FORMATS.get(record.levelno, self.FORMATS[logging.INFO])
        formatter = logging.Formatter(log_format)
        return formatter.format(record)


def get_log_config():
    """
    Uvicorn logging configuration dengan colored output
    """
    log_level = settings.log_level.upper()
    
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": ColoredFormatter,
            },
            "access": {
                "()": ColoredFormatter,
            },
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
        "access": {
                "formatter": "access",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "uvicorn": {
                "handlers": ["default"],
                "level": log_level,
                "propagate": False,
            },
            "uvicorn.error": {
                "handlers": ["default"],
                "level": log_level,
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["access"],
                "level": log_level,
                "propagate": False,
            },
            "banalyze-backend": {
                "handlers": ["default"],
                "level": log_level,
                "propagate": False,
            },
        },
    }


class BanalyzeLogger:
    """
    Enhanced logger dengan colored output dan specialized methods
    """
    
    def __init__(self, name: str = "banalyze-backend"):
        self.name = name
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logger dengan colored console dan optional file"""
        logger = logging.getLogger(self.name)
        
        # Avoid duplicate handlers
        if logger.handlers:
            return logger
            
        logger.setLevel(getattr(logging, settings.log_level.upper()))
        
        # Colored console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(ColoredFormatter())
        logger.addHandler(console_handler)
        
        # File handler (optional)
        if hasattr(settings, 'log_file') and settings.log_file:
            self._add_file_handler(logger)
        
        return logger
    
    def _add_file_handler(self, logger: logging.Logger):
        """Add file handler tanpa warna untuk file"""
        try:
            log_dir = os.path.dirname(settings.log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
            
            from logging.handlers import RotatingFileHandler
            file_handler = RotatingFileHandler(
                settings.log_file,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
            file_handler.setLevel(logging.DEBUG)
            
            # Plain formatter untuk file (tanpa warna)
            file_formatter = logging.Formatter(
                "%(asctime)s | %(name)s | %(levelname)-8s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
            
        except Exception as e:
            logger.warning(f"Could not setup file logging: {e}")
    
    # Basic logging methods
    def debug(self, message: str, extra: Optional[dict] = None):
        """Debug level logging"""
        self.logger.debug(message, extra=extra)
    
    def info(self, message: str, extra: Optional[dict] = None):
        """Info level logging"""
        self.logger.info(message, extra=extra)
    
    def warning(self, message: str, extra: Optional[dict] = None):
        """Warning level logging"""
        self.logger.warning(message, extra=extra)
    
    def error(self, message: str, exc_info: bool = False, extra: Optional[dict] = None):
        """Error level logging"""
        self.logger.error(message, exc_info=exc_info, extra=extra)
    
    def critical(self, message: str, exc_info: bool = False, extra: Optional[dict] = None):
        """Critical level logging"""
        self.logger.critical(message, exc_info=exc_info, extra=extra)
    
    # Specialized logging methods dengan emoji untuk better readability
    def log_api_request(self, endpoint: str, method: str, user_id: Optional[str] = None):
        """Log API request"""
        user_info = f" | User: {user_id}" if user_id else ""
        self.info(f"🌐 {method} {endpoint}{user_info}")
    
    def log_llm_interaction(self, prompt_type: str, success: bool, response_time: Optional[float] = None):
        """Log LLM interaction"""
        status = "✅" if success else "❌"
        time_info = f" | {response_time:.2f}s" if response_time else ""
        self.info(f"🤖 LLM {prompt_type} {status}{time_info}")
    
    def log_cv_processing(self, filename: str, status: str, details: Optional[str] = None):
        """Log CV processing"""
        detail_info = f" | {details}" if details else ""
        if status == "success":
            self.info(f"📄 CV: {filename} ✅{detail_info}")
        else:
            self.error(f"📄 CV: {filename} ❌ {status}{detail_info}")
    
    def log_service_event(self, service: str, event: str, details: Optional[str] = None):
        """Log service events"""
        detail_info = f" | {details}" if details else ""
        if event in ["started", "startup", "ready"]:
            self.info(f"🚀 {service} {event.title()}{detail_info}")
        elif event in ["stopped", "shutdown"]:
            self.info(f"🛑 {service} {event.title()}{detail_info}")
        else:
            self.info(f"⚙️ {service}: {event}{detail_info}")


# Create global logger instance
logger = BanalyzeLogger("banalyze-backend")

# Convenience functions
def debug(message: str, extra: Optional[dict] = None):
    logger.debug(message, extra)

def info(message: str, extra: Optional[dict] = None):
    logger.info(message, extra)

def warning(message: str, extra: Optional[dict] = None):
    logger.warning(message, extra)

def error(message: str, exc_info: bool = False, extra: Optional[dict] = None):
    logger.error(message, exc_info, extra)

def critical(message: str, exc_info: bool = False, extra: Optional[dict] = None):
    logger.critical(message, exc_info, extra)


# Context manager untuk execution time
class LogExecutionTime:
    """Context manager untuk log execution time dengan warna"""
    
    def __init__(self, operation_name: str, logger_instance: BanalyzeLogger = logger):
        self.operation_name = operation_name
        self.logger = logger_instance
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.debug(f"⏱️ Started: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        if exc_type is None:
            self.logger.info(f"✅ Completed: {self.operation_name} | {duration:.3f}s")
        else:
            self.logger.error(f"❌ Failed: {self.operation_name} | {duration:.3f}s | {exc_val}")
# -*- coding: utf-8 -*-
"""
Logging system with rotation
"""
import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime


class AppLogger:
    """Application logger with file rotation"""
    
    _instance = None
    
    def __new__(cls, log_dir: str = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, log_dir: str = None):
        if hasattr(self, '_initialized'):
            return
            
        self._initialized = True
        
        if log_dir is None:
            log_dir = os.path.join(os.getenv('APPDATA', ''), 'B2BManagement', 'logs')
        
        os.makedirs(log_dir, exist_ok=True)
        
        self.logger = logging.getLogger('B2BManagement')
        self.logger.setLevel(logging.DEBUG)
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            # File handler with rotation
            log_file = os.path.join(log_dir, 'app.log')
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)
            
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # Formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def get_logger(self) -> logging.Logger:
        """Get logger instance"""
        return self.logger
    
    def info(self, message: str):
        self.logger.info(message)
    
    def debug(self, message: str):
        self.logger.debug(message)
    
    def warning(self, message: str):
        self.logger.warning(message)
    
    def error(self, message: str, exc_info=False):
        self.logger.error(message, exc_info=exc_info)
    
    def critical(self, message: str, exc_info=True):
        self.logger.critical(message, exc_info=exc_info)

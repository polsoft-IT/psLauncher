"""
logger.py - Structured logging system for CrossTerm

Provides:
- Multi-level logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Timestamp formatting
- Color-coded console output
- Log file persistence with rotation
- Performance metrics tracking
- Thread-safe operations
"""

from __future__ import annotations

import sys
import os
import time
import threading
import logging
import logging.handlers
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, Callable
from pathlib import Path
from dataclasses import dataclass, field
from collections import deque
from contextlib import contextmanager
import json


class LogLevel(Enum):
    """Log levels with numeric values for filtering"""
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50


@dataclass
class LogEntry:
    """Structured log entry"""
    level: str
    message: str
    timestamp: float
    source_file: Optional[str] = None
    source_line: Optional[int] = None
    function: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    performance_ms: Optional[float] = None


class ColorFormatter(logging.Formatter):
    """Color-coded formatter for console output"""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        # Add color to level name
        levelname = record.levelname
        if levelname in self.COLORS and sys.stdout.isatty():
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.RESET}"
        
        # Format timestamp
        record.asctime = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        
        return super().format(record)


class PerformanceTracker:
    """Track execution performance metrics"""
    
    def __init__(self, max_entries: int = 1000):
        self.metrics: Dict[str, deque] = {}
        self.max_entries = max_entries
        self._lock = threading.Lock()
    
    def record_metric(self, name: str, value: float, unit: str = 'ms') -> None:
        """Record a performance metric"""
        with self._lock:
            if name not in self.metrics:
                self.metrics[name] = deque(maxlen=self.max_entries)
            self.metrics[name].append({
                'value': value,
                'unit': unit,
                'timestamp': time.time()
            })
    
    def get_stats(self, name: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a metric"""
        with self._lock:
            if name not in self.metrics or not self.metrics[name]:
                return None
            
            values = [m['value'] for m in self.metrics[name]]
            return {
                'count': len(values),
                'min': min(values),
                'max': max(values),
                'avg': sum(values) / len(values),
                'latest': values[-1],
                'unit': self.metrics[name][-1]['unit']
            }
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all metrics"""
        with self._lock:
            return {name: self.get_stats(name) for name in self.metrics}


class StructuredLogger:
    """
    Structured logging system with file persistence, rotation, and performance tracking
    """
    
    _instance: Optional['StructuredLogger'] = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        """Singleton pattern"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(
        self,
        log_dir: Optional[str] = None,
        log_file: str = "execution.log",
        max_bytes: int = 10 * 1024 * 1024,  # 10 MB
        backup_count: int = 5,
        console_level: str = "INFO",
        file_level: str = "DEBUG",
        enable_colors: bool = True
    ):
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        self.log_dir = Path(log_dir) if log_dir else Path.cwd() / "logs"
        self.log_file = self.log_dir / log_file
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self.enable_colors = enable_colors
        self.performance = PerformanceTracker()
        
        # Create log directory
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup Python logger
        self.logger = logging.getLogger("CrossTerm")
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, console_level.upper()))
        
        if enable_colors:
            console_formatter = ColorFormatter(
                fmt='%(asctime)s [%(levelname)s] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        else:
            console_formatter = logging.Formatter(
                fmt='%(asctime)s [%(levelname)s] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            self.log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(getattr(logging, file_level.upper()))
        file_formatter = logging.Formatter(
            fmt='%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # In-memory log storage
        self.memory_logs: deque = deque(maxlen=10000)
        self._memory_lock = threading.Lock()
        
        # Performance context tracking
        self._performance_context: Dict[str, float] = {}
        self._context_lock = threading.Lock()
    
    def log(
        self,
        level: str,
        message: str,
        source_file: Optional[str] = None,
        source_line: Optional[int] = None,
        function: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        performanceMs: Optional[float] = None
    ) -> None:
        """Log a message with structured data"""
        # Log to Python logger
        log_level = getattr(logging, level.upper(), logging.INFO)
        self.logger.log(log_level, message)
        
        # Store in memory
        entry = LogEntry(
            level=level,
            message=message,
            timestamp=time.time(),
            source_file=source_file,
            source_line=source_line,
            function=function,
            context=context or {},
            performance_ms=performanceMs
        )
        
        with self._memory_lock:
            self.memory_logs.append(entry)
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message"""
        self.log("DEBUG", message, **kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message"""
        self.log("INFO", message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message"""
        self.log("WARNING", message, **kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """Log error message"""
        self.log("ERROR", message, **kwargs)
    
    def critical(self, message: str, **kwargs) -> None:
        """Log critical message"""
        self.log("CRITICAL", message, **kwargs)
    
    def start_performance(self, name: str) -> None:
        """Start timing a performance metric"""
        with self._context_lock:
            self._performance_context[name] = time.time()
    
    def end_performance(self, name: str, unit: str = 'ms') -> float:
        """End timing and record performance metric"""
        with self._context_lock:
            if name not in self._performance_context:
                return 0.0
            
            duration = (time.time() - self._performance_context[name]) * 1000  # Convert to ms
            del self._performance_context[name]
        
        self.performance.record_metric(name, duration, unit)
        return duration
    
    def log_performance(self, name: str, message: Optional[str] = None) -> None:
        """Log performance metric with optional message"""
        stats = self.performance.get_stats(name)
        if stats:
            msg = message or f"Performance: {name}"
            self.info(
                f"{msg} - avg: {stats['avg']:.2f}{stats['unit']}, "
                f"min: {stats['min']:.2f}{stats['unit']}, "
                f"max: {stats['max']:.2f}{stats['unit']}, "
                f"count: {stats['count']}"
            )
    
    def get_logs(self, level: Optional[str] = None, limit: int = 100) -> list[LogEntry]:
        """Retrieve logs from memory, optionally filtered by level"""
        with self._memory_lock:
            if level:
                return [log for log in self.memory_logs if log.level == level][-limit:]
            return list(self.memory_logs)[-limit:]
    
    def export_logs(self, filepath: Optional[str] = None) -> str:
        """Export logs to JSON file"""
        if filepath is None:
            filepath = self.log_dir / f"logs_export_{int(time.time())}.json"
        
        with self._memory_lock:
            logs_data = [
                {
                    'level': log.level,
                    'message': log.message,
                    'timestamp': log.timestamp,
                    'source_file': log.source_file,
                    'source_line': log.source_line,
                    'function': log.function,
                    'context': log.context,
                    'performance_ms': log.performance_ms
                }
                for log in self.memory_logs
            ]
        
        export_path = Path(filepath)
        export_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(logs_data, f, indent=2)
        
        return str(export_path)
    
    def clear_memory_logs(self) -> None:
        """Clear in-memory log storage"""
        with self._memory_lock:
            self.memory_logs.clear()
    
    def set_level(self, level: str, handler: str = 'console') -> None:
        """Change log level for a specific handler"""
        log_level = getattr(logging, level.upper(), logging.INFO)
        for handler in self.logger.handlers:
            if isinstance(handler, logging.StreamHandler) and handler.stream == sys.stdout:
                if handler == 'console':
                    handler.setLevel(log_level)
            elif isinstance(handler, logging.handlers.RotatingFileHandler):
                if handler == 'file':
                    handler.setLevel(log_level)


# Convenience functions for quick access
_logger_instance: Optional[StructuredLogger] = None


def get_logger() -> StructuredLogger:
    """Get the singleton logger instance"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = StructuredLogger()
    return _logger_instance


def setup_logger(
    log_dir: Optional[str] = None,
    log_file: str = "execution.log",
    **kwargs
) -> StructuredLogger:
    """Setup and configure the logger"""
    global _logger_instance
    _logger_instance = StructuredLogger(log_dir=log_dir, log_file=log_file, **kwargs)
    return _logger_instance


# Quick access functions
def log_debug(message: str, **kwargs) -> None:
    get_logger().debug(message, **kwargs)


def log_info(message: str, **kwargs) -> None:
    get_logger().info(message, **kwargs)


def log_warning(message: str, **kwargs) -> None:
    get_logger().warning(message, **kwargs)


def log_error(message: str, **kwargs) -> None:
    get_logger().error(message, **kwargs)


def log_critical(message: str, **kwargs) -> None:
    get_logger().critical(message, **kwargs)


@contextmanager
def performance_context(name: str):
    """Context manager for performance tracking"""
    get_logger().start_performance(name)
    try:
        yield
    finally:
        get_logger().end_performance(name)


if __name__ == "__main__":
    # Test the logger
    logger = setup_logger(log_dir="test_logs")
    
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
    
    # Test performance tracking
    with performance_context("test_operation"):
        import time
        time.sleep(0.1)
    
    logger.log_performance("test_operation")
    
    # Export logs
    export_path = logger.export_logs()
    print(f"Logs exported to: {export_path}")

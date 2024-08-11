"""
MasterLog Logging Module
=============

This module provides a versatile logging system with configurable log levels, sources, and formatting options. 
It supports colorized output for terminal logging and allows for file-based logging with customizable settings.

Features:
- Log Levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Source-Based Filtering: Log messages can be filtered by source, with optional colorization.
- Customizable Format: Adjust log message format and date format.
- File Logging: Option to save logs to a file with configurable filename.
- Dynamic Source Management: Add or remove logging sources and set a default source.

Usage:
- Configure the logger using the `config` function.
- Log messages at various levels using `debug`, `info`, `warning`, `error`, and `critical`.
- Manage logging sources with `add_source` and `remove_source`.
- Toggle logging with `enable` and `disable`.
- Set or update the default logging source with `set_default_source`.

Example:
    >>> import log
    >>> log.config(level=log.DEBUG, sources=('SYSTEM', 'APP'), format="{asctime} {source} - {levelname}: {message}")
    >>> log.info("This is an info message", source="APP")
    >>> log.error("This is an error message", source="SYSTEM")

Classes:
- `Logger`: Core class responsible for logging operations and configuration.
- `_Buffer`: Manages buffered log entries and performs logging in a separate thread.
- `_Config`: Contains configuration settings for the Logger.

Functions:
- `critical(message: str, source: str=None) -> None`: Logs a CRITICAL level message.
- `error(message: str, source: str=None) -> None`: Logs an ERROR level message.
- `warning(message: str, source: str=None) -> None`: Logs a WARNING level message.
- `info(message: str, source: str=None) -> None`: Logs an INFO level message.
- `debug(message: str, source: str=None) -> None`: Logs a DEBUG level message.
- `log(message: str, source: str=None) -> None`: Logs a message with INFO level by default.
- `config(**kwargs) -> None`: Configures logging settings such as level, sources, format, and file saving options.
- `add_source(source: str, color: str="DIMMED")`: Adds a new logging source with optional color.
- `remove_source(source: str) -> None`: Removes a logging source.
- `set_default_source(source: str, color: str="DIMMED")`: Sets or updates the default logging source.
- `disable() -> None`: Disables logging by setting the level to RELEASE.
- `enable() -> None`: Re-enables logging by restoring the previous logging level.

Notes:
- The logger's color output and file saving features can be enabled or disabled through configuration settings.
- The `sources` argument in `config` can be a tuple of specific sources or the string 'all'/'defined' to log messages from any source or only from sources currently defined in the logger.
- The buffer discards new log entries when full to prevent potential slowdowns or crashes, ensuring that the main application continues to operate smoothly even under heavy logging load.

Author:
- Sergey Hovhannisyan

GitHub:
- github.com/sergey-hovhannisyan

Date:
- August 8, 2024
"""

from datetime import datetime
import threading
import atexit
from collections import deque
from time import sleep
import sys

# Logging Levels
RELEASE = 6
CRITICAL = 5
ERROR = 4
WARNING = 3
INFO = 2
DEBUG = 1

# Mapping of logging level integers to their string representations
_level = {
    RELEASE: "RELEASE",
    CRITICAL: "CRITICAL",
    ERROR: "ERROR",
    WARNING: "WARNING",
    INFO: "INFO",
    DEBUG: "DEBUG",
}

# Default logging level
__currentlevel__ = DEBUG

# Default source for logging
DEFAULT_SOURCE = "SYSTEM"

# Set of current logging sources
_sources = SOURCES = {DEFAULT_SOURCE}

# Colors for terminal output
Colors = {
    "RED": '\033[31m',
    "GREEN": '\033[32m',
    "YELLOW": '\033[33m',
    "BLUE": '\033[34m',
    "MAGENTA": '\033[35m',
    "CYAN": '\033[36m',
    "DIMMED": '\033[2m',
    "BOLD": '\033[1m',
    "RESET": '\033[0m',
}

# Colorized representations of logging levels
ColorizedLevel = {
    CRITICAL: f"{Colors['RED']}{Colors['BOLD']}Critical{Colors['RESET']}",
    ERROR: f"{Colors['RED']}Error{Colors['RESET']}",
    WARNING: f"{Colors['YELLOW']}Warning{Colors['RESET']}",
    INFO: f"{Colors['GREEN']}Info{Colors['RESET']}",
    DEBUG: f"{Colors['DIMMED']}Debug{Colors['RESET']}",
}

# Colorized representations of sources
ColorizedSource = {
    DEFAULT_SOURCE: (f"{Colors['CYAN']}{Colors['BOLD']}{DEFAULT_SOURCE}{Colors['RESET']}", "CYAN"),
}

class Logger:
    _loglock = threading.Lock()
    _buffer_log_thread = None
    _buffer_save_thread = None

    def __init__(self):
        self.config()

    class _Buffer:
        _lock = threading.Lock()
        _event = threading.Event()
        queue = deque()

        @classmethod
        def push(cls, *args, **kwargs) -> None:
            """Push a log entry to the buffer if within the bufferlimit."""
            with cls._lock:
                if len(cls.queue) <= Logger._Config.bufferlimit:
                    cls.queue.append((args, kwargs))

        @classmethod
        def pop(cls):
            """Pop a log entry from the buffer."""
            with cls._lock:
                if cls.queue:
                    return cls.queue.popleft()
                return None

        @classmethod
        def clear(cls) -> None:
            """Clear all log entries in the buffer."""
            cls.queue.clear()

        @classmethod
        def log_buffer(cls) -> None:
            """Print all log entries in the buffer."""
            while cls.queue:
                args, kwargs = cls.pop()
                print(Logger._format(*args, **kwargs))
                sys.stdout.flush()

        @classmethod
        def start_logging(cls) -> None:
            """Start the logging thread to continuously print log entries."""
            while not cls._event.is_set():
                cls.log_buffer()
                sleep(0.1)

        @classmethod
        def stop_logging(cls) -> None:
            """Stop the logging thread."""
            cls._event.set()
            if Logger._buffer_log_thread:
                Logger._buffer_log_thread.join()
                Logger._buffer_log_thread = None

        @classmethod
        def save_buffered_logs(cls) -> None:
            """Save all buffered logs to the configured file."""
            with open(file=Logger._Config.filename, mode='a') as file:
                while cls.queue:
                    args, kwargs = cls.pop()
                    file.write(Logger._format(*args, **kwargs) + '\n')
                file.flush()
        
        @classmethod
        def start_saving(cls) -> None:
            """Start the saving thread to continuously save log entries."""
            while not cls._event.is_set():
                cls.save_buffered_logs()
                sleep(0.1)

        @classmethod
        def stop_saving(cls) -> None:
            """Stop the saving thread."""
            cls._event.set()
            if Logger._buffer_save_thread:
                Logger._buffer_save_thread.join()
                Logger._buffer_save_thread = None

    class _Config:
        """Configuration for the Logger."""
        level = __currentlevel__
        sources = 'all'
        format = "{asctime} {source} : {levelname} -> {message}"
        dateformat = "%H:%M:%S"
        enable_color = True
        enable_save = False
        filename = 'system.log'
        bufferlimit = 1000

    @classmethod
    def config(cls, **kwargs) -> None:
        """Configure the logger settings.

        Args:
            **kwargs: Configuration options to set.
        """
        sleep(0.1)
        for key, value in kwargs.items():
            setattr(cls._Config, key, value)

        if cls._Config.enable_save:
            if not cls._buffer_save_thread:
                cls._Buffer.stop_logging()
                cls._buffer_save_thread = threading.Thread(target=cls._Buffer.start_saving, daemon=True)
                cls._Buffer._event.clear()
                cls._buffer_save_thread.start()
        elif not cls._buffer_log_thread:
            cls._Buffer.stop_saving()
            cls._buffer_log_thread = threading.Thread(target=cls._Buffer.start_logging, daemon=True)
            cls._Buffer._event.clear()
            cls._buffer_log_thread.start()

    @classmethod
    def clean(cls) -> None:
        """Clean up resources by stopping logging and saving threads and clearing the buffer."""
        cls._Buffer.stop_logging()
        cls._Buffer.stop_saving()
        cls._Buffer.clear()

    @staticmethod
    def _time() -> str:
        """Get the current time formatted according to the logger's date format.

        Returns:
            str: The formatted current time.
        """
        now = datetime.now()
        return now.strftime(Logger._Config.dateformat)

    @classmethod
    def _format(cls, timestamp: str, level: int, source: str, message: str) -> None:
        """Format a log entry according to the configuration.

        Args:
            timestamp (str): The timestamp of the log entry.
            level (int): The log level.
            source (str): The source of the log entry.
            message (str): The log message.

        Returns:
            str: The formatted log entry.
        """
        if not cls._Config.enable_save and cls._Config.enable_color:
            levelname = ColorizedLevel.get(level, _level[level])
            source_color, _ = ColorizedSource.get(source, (f"{Colors['DIMMED']}{Colors['BOLD']}{source}{Colors['RESET']}", "DIMMED"))
        else:
            levelname = _level[level]
            source_color = source

        return cls._Config.format.format(
            asctime=timestamp,
            source=source_color,
            levelname=levelname,
            message=message)

    @classmethod
    def _log(cls, level: int, message: str, source: str=None) -> None:
        """Log a message at a specified level and source.

        Args:
            level (int): The log level.
            message (str): The log message.
            source (str): The source of the log entry.
        """
        if not source:
            global DEFAULT_SOURCE
            source = DEFAULT_SOURCE
        if cls._isEnabled(source, level):
            with cls._loglock:
                cls._Buffer.push(cls._time(), level, source, message)

    @classmethod
    def _isEnabled(cls, source: str, level: int) -> bool:
        """Check if logging is enabled for the given source and level.

        Args:
            source (str): The source of the log entry.
            level (int): The log level.

        Returns:
            bool: True if logging is enabled, otherwise False.
        """
        if level >= cls._Config.level:
            if cls._Config.sources == 'all' or source in cls._Config.sources:
                return True
        return False

def config(**kwargs):
    """Configure the logger settings.

    Args:
        level (int): Logging level. Valid values: DEBUG, INFO, WARNING, ERROR, CRITICAL.
        sources (tuple): Tuple of valid sources for logging. Example: 'all', 'defined', (SYSTEM, ...)
        format (fstring): Log message format string. Example: "{asctime} {source} : {levelname} -> {message}"
        dateformat (fstring): Date format string used in logs. Example: "%Y-%m-%d %H:%M:%S"
        enable_color (bool): Enable Styled output in logs. Example: True
        enable_save (bool): Enable saving logs to a file. Example: False
        filename (str): Filename to save logs to. Default: 'system.log'
        bufferlimit (int): Logger buffer limit. Specifies the maximum number of log entries the buffer can hold.
                           If the buffer is full, new log entries will be discarded to ensure smooth operation.
    """
    global __currentlevel__
    if 'level' in kwargs:
        __currentlevel__ = kwargs['level']

    global SOURCES
    global DEFAULT_SOURCE
    if 'sources' in kwargs:
        if kwargs['sources'] == 'all':
            kwargs['sources'] = 'all'
        elif kwargs['sources'] == 'defined':
            kwargs['sources'] = SOURCES
        else:
            new_sources = set(kwargs['sources'])

            for source in new_sources:
                if source not in SOURCES:
                    add_source(source)

            for source in SOURCES.copy():
                if source not in new_sources:
                    remove_source(source)

            SOURCES = new_sources
            kwargs['sources'] = SOURCES
    Logger.config(**kwargs)

def critical(message: str, source: str=None) -> None:
    """Log a message at the CRITICAL level.

    Args:
        message (str): The log message.
        source (str): The source of the log entry.
    """
    Logger._log(CRITICAL, message, source)

def error(message: str, source: str=None) -> None:
    """Log a message at the ERROR level.

    Args:
        message (str): The log message.
        source (str): The source of the log entry.
    """
    Logger._log(ERROR, message, source)

def warning(message: str, source: str=None) -> None:
    """Log a message at the WARNING level.

    Args:
        message (str): The log message.
        source (str): The source of the log entry.
    """
    Logger._log(WARNING, message, source)

def info(message: str, source: str=None) -> None:
    """Log a message at the INFO level.

    Args:
        message (str): The log message.
        source (str): The source of the log entry.
    """
    Logger._log(INFO, message, source)

def debug(message: str, source: str=None) -> None:
    """Log a message at the DEBUG level.

    Args:
        message (str): The log message.
        source (str): The source of the log entry.
    """
    Logger._log(DEBUG, message, source)

def log(message: str, source: str=None) -> None:
    """Log a message at the INFO level.

    Args:
        message (str): The log message.
        source (str): The source of the log entry.
    """
    info(message, source)

def add_source(source: str, color: str = "DIMMED"):
    """Add a new source to the logger.

    Args:
        source (str): The new source to add.
        color (str): The color to use for this source in terminal output.
    """
    from random import choice

    global SOURCES
    SOURCES.add(source)
    color = color.upper()
    if color not in Colors:
        taken_colors = {color for _, color in ColorizedSource.values()}
        available_colors = set(Colors.keys()) - taken_colors - {"RESET", "BOLD"}
        if available_colors:
            color = choice(list(available_colors))
        else:
            color = "DIMMED"

    ColorizedSource[source] = (f"{Colors[color]}{Colors['BOLD']}{source}{Colors['RESET']}", color)

def remove_source(source: str):
    """Remove a source from the logger.

    Args:
        source (str): The source to remove.
    """
    global SOURCES
    if source in SOURCES:
        SOURCES.remove(source)

    if source in ColorizedSource:
        del ColorizedSource[source]
    
    if not SOURCES:
        set_default_source("SYSTEM", "CYAN")
    else:
        if source == DEFAULT_SOURCE:
            from random import choice
            set_default_source(choice(list(SOURCES)), "CYAN")

def set_default_source(source: str, color:str="DIMMED"):
    """Set the default source for logging.

    Args:
        source (str): The new default source.
        color (str): The color to use for this source in terminal output.
    """
    global DEFAULT_SOURCE, SOURCES
    source = source.upper()
    if source not in SOURCES:
        add_source(source, color)
    DEFAULT_SOURCE = source

def disable() -> None:
    """Disable all logging by setting the level to RELEASE."""
    Logger.config(level=RELEASE)

def enable() -> None:
    """Enable logging with the current level."""
    Logger.config(level=__currentlevel__)

__all__ = ['critical', 'error', 'warning', 'info', 'debug', 'log', 'config', 'enable', 'disable',
           'set_default_source', 'add_source', 'remove_source', 
           'CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'DEFAULT_SOURCE', 'SOURCES']

_initialized = False

def initialize_logger():
    """Initialize the logger and register cleanup on exit."""
    global _initialized
    if not _initialized:
        _initialized = True
        Logger.config()
        atexit.register(Logger.clean)

initialize_logger()
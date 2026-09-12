"""
Logger module for my-rxer project.
Provides a flexible logging abstraction with message formatting and key-value pair support.
"""
import json
import logging
import contextvars
import traceback
from typing import Any

logger_context = contextvars.ContextVar("logger_context", default={})

_logger_instance = None


class Logger:
    """
    Custom logger with enhanced capabilities.
    
    Features:
    - Key-value pair logging
    - JSON serialization support
    - Context-aware logging
    """
    _levelToFig = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
    }
    
    Element = type('Element', (), {})
    
    def __init__(self, name: str):
        """Initialize the logger."""
        global _logger_instance
        self.logger = logging.getLogger(name)
        
        Logger.console_handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        Logger.console_handler.setFormatter(formatter)
        self.logger.addHandler(Logger.console_handler)
        
        if _logger_instance is None:
            _logger_instance = self
    
    def get_logger(self):
        """Get the logger instance."""
        return self.logger
    
    # Instance methods - always require message arg
    def _log(self, message: str, level: str = "info", **kwargs: Any) -> None:
        """
        Log a message with the given level and key-value pairs.
        
        Args:
            message: Log message
            level: Log level (debug, info, warning, error)
            **kwargs: Additional key-value pairs to log
        """
        log_level = self._levelToFig.get(level, logging.INFO)
        base_msg = message if message else ""
        kwargs_str = json.dumps(kwargs, default=str, separators=(', ', ': ')) if kwargs else ""
        final_msg = f"{base_msg} - {kwargs_str}".strip()
        record = self.logger.makeRecord(
            self.logger.name,
            log_level,
            "",
            logging.NOTSET,
            final_msg,
            (),
            None,
        )
        self.logger.handle(record)
    
    def debug(self, message: str, **kwargs: Any) -> None:
        """Debug level logging."""
        self._log(message, "debug", **kwargs)
    
    def info(self, message: str, **kwargs: Any) -> None:
        """Info level logging."""
        self._log(message, "info", **kwargs)
    
    def warning(self, message: str, **kwargs: Any) -> None:
        """Warning level logging."""
        self._log(message, "warning", **kwargs)
    
    def error(self, message: str, **kwargs: Any) -> None:
        """Error level logging."""
        self._log(message, "error", **kwargs)
    
    @staticmethod
    def exception(message: str, exception: Exception, **kwargs: Any) -> None:
        """Exception level logging with traceback."""
        try:
            _logger_instance._log(message, "error", traceback=str(traceback.format_exc()), **kwargs)
        except:
            if _logger_instance:
                _logger_instance._log(message, "error", traceback=traceback.format_exc())
    
    # Class methods for convenience
    @classmethod
    def debug(cls, message: str = "", **kwargs: Any) -> None:
        """Debug level logging (class method)."""
        logger_obj = cls.__new__(cls)
        logger_obj.__init__(__name__)
        if _logger_instance:
            _logger_instance._log(message, "debug", **kwargs)
    
    @classmethod
    def info(cls, message: str = "", **kwargs: Any) -> None:
        """Info level logging (class method)."""
        logger_obj = cls.__new__(cls)
        logger_obj.__init__(__name__)
        if _logger_instance:
            _logger_instance._log(message, "info", **kwargs)
    
    @classmethod
    def warning(cls, message: str = "", **kwargs: Any) -> None:
        """Warning level logging (class method)."""
        logger_obj = cls.__new__(cls)
        logger_obj.__init__(__name__)
        if _logger_instance:
            _logger_instance._log(message, "warning", **kwargs)
    
    @classmethod
    def error(cls, message: str = "", **kwargs: Any) -> None:
        """Error level logging (class method)."""
        logger_obj = cls.__new__(cls)
        logger_obj.__init__(__name__)
        if _logger_instance:
            _logger_instance._log(message, "error", **kwargs)
    
    @classmethod
    def exception(cls, message: str = "", exception: Exception = None, **kwargs: Any) -> None:
        """Exception level logging with traceback (class method)."""
        # Use existing singleton instance to avoid re-creation
        # Handle case where _logger_instance might not be set yet
        global _logger_instance
        import sys
        
        # Check if _logger_instance is defined
        if 'global' not in locals() or '_logger_instance' not in locals():
            from typing import Any
            local_vars = {}
            exec('global _logger_instance\n_logger_instance = None', local_vars)
            if '_logger_instance' not in local_vars:
                # Create using static method
                _logger_instance = cls(__name__)
        
        if _logger_instance is None:
            _logger_instance = cls.__new__(cls)
            cls.__init__(_logger_instance, __name__) if hasattr(cls, '__init__') else None
        
        try:
            if exception:
                _logger_instance._log(message, "error", traceback=str(traceback.format_exc()), **kwargs)
            else:
                _logger_instance._log(message, "error", **kwargs)
        except:
            import traceback
            tb = traceback.format_exc()
            if '_logger_instance' in globals() and _logger_instance:
                _logger_instance._log(message, "error", traceback=tb)
    
    @staticmethod
    def get_logger() -> 'Logger':
        """Get the global logger instance."""
        return _logger_instance if _logger_instance is not None else Logger(__name__)
    
    @staticmethod
    def get_context() -> dict:
        """Get the current logging context."""
        return logger_context.get().copy()
    
    @staticmethod
    def set_correlation_id(correlation_id: str) -> None:
        """Set the correlation ID in the current context."""
        logger_context.set({"correlation_id": correlation_id})
    
    @staticmethod
    def set_task(task_id: str, task_name: str) -> None:
        """Set the task context."""
        context = logger_context.get()
        if "task" not in context:
            context["task"] = {}
        context["task"]["id"] = task_id
        context["task"]["name"] = task_name
        if "correlation_id" in context:
            context["task"].update({"correlation_id": context["correlation_id"]})
        logger_context.set(context)


# Initialize a default logger instance
logger = Logger(__name__)

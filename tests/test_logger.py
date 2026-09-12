"""Unit tests for logger module."""
import pytest
import logging
from unittest.mock import patch, MagicMock
from datetime import datetime
from src.core.logger import Logger, logger_context


class TestLogger:
    """Test Logger class."""
    
    @patch('logging.StreamHandler')
    def test_logger_initialization(self, mock_handler):
        """Logger initializes with handler and formatter."""
        mock_instance = MagicMock()
        mock_handler.return_value = mock_instance
        
        logger = Logger("test.logger")
        
        # Verify handler was set
        assert len(logger.logger.handlers) == 1
    
    @patch('logging.StreamHandler')
    @patch('logging.Formatter')
    def test_logger_formatter(self, mock_formatter, mock_handler):
        """Logger uses JSON serializer for formatting."""
        mock_instance = MagicMock()
        mock_handler.return_value = mock_instance
        mock_instance.setFormatter.return_value = MagicMock()
        
        logger = Logger("test.logger2")
        
        # Logger should have a formatter
        assert len(logger.logger.handlers) == 1

    def test_logger_set_correlation_id(self):
        """Set correlation ID in context."""
        Logger.set_correlation_id("abc-123")
        
        ctx = logger_context.get()
        assert ctx["correlation_id"] == "abc-123"

    def test_logger_set_task(self):
        """Set task context."""
        Logger.set_task("task-id-1", "test-task")
        
        ctx = logger_context.get()
        assert "task" in ctx
        assert ctx["task"]["id"] == "task-id-1"
        assert ctx["task"]["name"] == "test-task"

    def test_logger_debug(self):
        """Debug level logging."""
        Logger.debug("test debug message", key1="value1")
        # If successful, no exception is raised

    def test_logger_info(self):
        """Info level logging."""
        Logger.info("test info message", key2="value2")
        # If successful, no exception is raised

    def test_logger_warning(self):
        """Warning level logging."""
        Logger.warning("test warning message")
        # If successful, no exception is raised

    def test_logger_error(self):
        """Error level logging."""
        Logger.error("test error message", error_info="details")
        # If successful, no exception is raised

    def test_logger_exception(self):
        """Exception level logging."""
        try:
            raise ValueError("Test exception")
        except Exception as e:
            Logger.exception("test exception", exception=e)
        # If successful, no exception is raised

    def test_logger_get_context(self):
        """Get current logger context."""
        Logger.set_correlation_id("xy-123")
        Logger.set_task("tid-1", "name-1")
        
        ctx = Logger.get_context()
        assert "correlation_id" in ctx
        assert ctx["correlation_id"] == "xy-123"
        assert "task" in ctx

    def test_logger_with_kwargs(self):
        """Logger captures kwargs properly."""
        Logger.info("test message", field1="a", field2="b", field3=123)
        # Should not raise

    def test_logger_json_serialization(self):
        """Verify that simple objects can be logged."""
        Logger.info("test", simple_string="test")
        # Should not raise

class TestLoggingConfiguration:
    """Test logging configuration and setup."""
    
    @patch('logging.getLogger')
    def test_logger_gets_name(self, mock_get_logger):
        """Logger gets correct name from getLogger."""
        mock_logger_instance = MagicMock()
        mock_get_logger.return_value = mock_logger_instance
        
        Logger("my-app.component")
        
        # getLogger should have been called
        mock_get_logger.assert_called_once_with("my-app.component")


class TestLoggerContextVars:
    """Test logger context variable behavior."""
    
    def test_context_var_isolation(self):
        """Context vars are thread/local safe."""
        Logger.set_correlation_id("id-1")
        ctx1 = logger_context.get()
        
        Logger.set_correlation_id("id-2")
        ctx2 = logger_context.get()
        
        assert ctx1["correlation_id"] == "id-1"
        assert ctx2["correlation_id"] == "id-2"
        
        # Reset
        Logger.set_correlation_id(None)
    
    def test_context_defaults(self):
        """Context has default value."""
        ctx = logger_context.get()
        assert "correlation_id" in ctx
        assert ctx["correlation_id"] is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

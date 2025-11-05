# logger.py
import inspect
import sys

from src.tools.logs_db_manager import LogsDBManager

# IMPORTANT: DO NOT import DBManager at the top level here.

class Logger:
    """
    A centralized logger utility that routes messages to the MySQL 'logs' table.
    It automatically determines the calling class and method.
    """
    def __init__(self):
        """Initializes the Logger without instantiating DBManager."""
        self._db_manager = None
        print("Logger initialized.")

    def _get_db_manager(self):
        """
        Lazy-loads and returns the DBManager instance.
        This is the CRITICAL fix for the circular import.
        """
        if self._db_manager is None:
            # Local import: Only happens when this function is called for the first time
            try:
                self._db_manager = LogsDBManager()
                # Check if connection failed in DBManager's __init__
                if not self._db_manager.conn or not self._db_manager.conn.is_connected():
                    print("CRITICAL: DBManager initialized but connection is inactive.", file=sys.stderr)
                    self._db_manager = None # Mark as None if connection failed
                    
            except Exception as e:
                # Fallback for module import failure
                print(f"CRITICAL: Failed to initialize DBManager in Logger: {e}", file=sys.stderr)
                return None
        return self._db_manager
    
    def _get_caller_info(self) -> str:
        """Get the class name and method name of the caller."""
        frame = inspect.currentframe()
        try:
            # We need to go back 3 frames
            caller_frame = frame.f_back.f_back.f_back
            
            # Get the method name
            method_name = caller_frame.f_code.co_name
            
            # Try to get the class name from 'self' or 'cls'
            class_name = None
            if 'self' in caller_frame.f_locals:
                class_name = caller_frame.f_locals['self'].__class__.__name__
            elif 'cls' in caller_frame.f_locals:
                class_name = caller_frame.f_locals['cls'].__name__
            
            # Format the location
            if class_name:
                return f"{class_name}.{method_name}"
            else:
                # If called from module level, use __main__ instead of <module>
                if method_name == "<module>":
                    return "__main__"
                return method_name
        finally:
            del frame
    
    def _log(self, level: str, message: str):
        """
        Log a message with a specified severity level to the database, including caller information

        :param self: Logger instance used to perform the logging
        :param level: Severity level of the log message (e.g., INFO, ERROR)
        :type level: str
        :param message: The log message to record
        :type message: str
        """
        location = self._get_caller_info()
        if self._db_manager is None: #Lazy loading
            self._db_manager = self._get_db_manager()
        self._db_manager.insert_log(level, location, message)
    
    def info(self, message: str):
        """Log an info message."""
        self._log("INFO", message)
    
    def debug(self, message: str):
        """Log a debug message."""
        self._log("DEBUG", message)
    
    def warning(self, message: str):
        """Log a warning message."""
        self._log("WARNING", message)
    
    def error(self, message: str):
        """Log an error message."""
        self._log("ERROR", message)
    
    def critical(self, message: str):
        """Log a critical message."""
        self._log("CRITICAL", message)

# --- GLOBAL STANDALONE INSTANCE ---
logger = Logger()

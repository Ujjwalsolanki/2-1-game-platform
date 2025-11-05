# logs_db_manager.py
import atexit
import sys
import mysql.connector
from mysql.connector import Error as MySQLError
from src.utils.config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME

class LogsDBManager:
    """
    Dedicated db manager for logging operations to prevent circular dependencies.
    """
    def __init__(self):
        """
        Initialize a database connection for logging and register cleanup on exit

        :param self: Instance of LogsDBManager being initialized
        """
        self.conn = None
        try:
            self.conn = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME 
            )
        except MySQLError as err:
            # Note: Can't log this to the DB, so we print to console
            print(f"❌ LogsDBManager: Connection Error in __init__: {err}", file=sys.stderr)
            self.conn = None

        # Register cleanup on application exit
        atexit.register(self._close_connection)
    
    def _close_connection(self):
        """
        Close the database connection if it is open

        :param self: Instance of LogsDBManager whose connection will be closed
        """
        if self.conn and self.conn.is_connected():
            self.conn.close()

    def _execute_query(self, query: str, params=None, fetch_one=False):
        """
        A general purpose method to execute a query (SELECT, INSERT, UPDATE, DELETE).
        Uses the instance's persistent connection.
        """
        if not self.conn or not self.conn.is_connected():
            print("❌ DBManager: Cannot execute query. Connection is closed or invalid.")
            return None

        result = None
        try:
            cursor = self.conn.cursor(dictionary=True) # Use dictionary=True for column name access
            cursor.execute(query, params or ())
            
            if query.strip().upper().startswith("SELECT"):
                result = cursor.fetchone() if fetch_one else cursor.fetchall()
            
            elif query.strip().upper().startswith("INSERT"):
                self.conn.commit()
                result = cursor.lastrowid
            
            else: # UPDATE, DELETE
                self.conn.commit()
                result = cursor.rowcount 

            cursor.close()
        
        except MySQLError as err:
            print(f"❌ DBManager Query Error: {err}")
            self.conn.rollback()
        
        return result
    
    def insert_log(self, level: str, service: str, message: str):
        """
        Insert a log entry into the database with the specified level, service, and message

        :param self: Instance of LogsDBManager handling the database connection
        :param level: Severity level of the log entry (e.g., info, warning, error)
        :type level: str
        :param service: Name of the service or component generating the log
        :type service: str
        :param message: Log message content to be recorded
        :type message: str
        :return: True if the log was inserted successfully, False otherwise
        :rtype: bool
        """
        result = False
        if not self.conn or not self.conn.is_connected():
            return False # Cannot log if connection is dead

        query = "INSERT INTO logs (level, service, message) VALUES (%s, %s, %s)"
        params = (level.lower(), service, message)
        
        try:
            # Check if the query execution succeeded
            success = self._execute_query(query, params=params)
            if success is None and not str(success).startswith("0"):
                print(f"CRITICAL LOG FAILURE: Could not write log to DB: {message}", file=sys.stderr)
                result = False

            print(f'[{level}.{service}.{message}]')
            result = True
        
        except MySQLError as err:
            print(f"CRITICAL LOG FAILURE: DB Write Error: {err}", file=sys.stderr)
            self.conn.rollback()
        return result
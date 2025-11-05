import atexit
import json
from typing import Any, Dict, List, Optional
import mysql.connector
from mysql.connector import Error as MySQLError # Import specific error for clarity
from src.tools.logger import logger
from src.utils.config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME

class DBManager:

    def __init__(self):
        """
        Attempts to establish a database connection and stores it on the instance.
        """
        self.conn = None
        self.logger = logger
        try:
            self.conn = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME 
            )
            if self.conn.is_connected():
                print("✅ DBManager: MySQL Connection established in __init__.")
            else:
                print("❌ DBManager: Failed to establish MySQL connection.")
        
        except MySQLError as err:
            print(f"❌ DBManager: Connection Error in __init__: {err}")
            # Ensure conn is explicitly None if connection fails
            self.conn = None 
        
        # Register cleanup on application exit
        atexit.register(self._close_connection)

    def _close_connection(self):
        """Closes the database connection safely."""
        if self.conn and self.conn.is_connected():
            self.conn.close()
            self.logger.info("DBManager: Connection closed.")

    def _execute_query(self, query: str, params=None, fetch_one=False):
        """
        A general purpose method to execute a query (SELECT, INSERT, UPDATE, DELETE).
        Uses the instance's persistent connection.
        """
        self.logger.info(f'execute query called {query}')
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
            self.logger.error(f"DBManager Query Error: {err}")
            self.conn.rollback()
        
        return result
    
    def insert_new_game(self, data: Dict[str, Any]) -> bool:
        """
        Inserts a complete game record into the 'games' table in a single transaction.
        Assumes 'data' dictionary keys exactly match the table columns (id, title, description, etc.).
        """
        result = False
        # 1. Define the columns based on the input dictionary keys
        keys = list(data.keys())
        columns = ', '.join(keys)
        
        # 2. Create the SQL placeholders (%s for MySQL parameterization)
        placeholders = ', '.join(['%s'] * len(keys))
        
        # 3. Construct the dynamic SQL statement
        sql = f"INSERT INTO games ({columns}) VALUES ({placeholders})"
        
        # 4. Create the tuple of values for secure execution
        values = tuple(data.values())

        try:
            status = self._execute_query(sql, values)
            if status is not None:
                result = True
            self.logger.info(f"Successfully inserted game: {data['title']} with ID: {data['id']}")

        except mysql.connector.Error as err:
            # Rollback in case of any database error
            if self.conn:
                self.conn.rollback()
            
            # Log the error details
            self.logger.error(f"MySQL Error during game insertion (ID: {data.get('id')}): {err}")
            raise err
        except ValueError as err:
            self.logger.error(f"Data Validation Error: {err}")

        return result
    
    def get_purchased_games(self, user_id: str) -> List[Dict[str, str]]:
        """
        Retrieves a list of games (ID and URL) that the specific user has paid for,
        by joining the 'payments' and 'games' tables.
        """
        query = """
            SELECT 
                p.game_id, 
                g.deployed_url
            FROM 
                payments p
            INNER JOIN 
                games g ON p.game_id = g.id
            WHERE 
                p.user_id = %s;
        """
        # Execute the query and fetch all results as a list of dictionaries
        results = self._execute_query(query, (user_id,), fetch_one=False)
        
        # If the query fails or returns nothing, return an empty list
        return results if isinstance(results, list) else []

    def get_game_details(self, game_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves necessary game details (title, description, deployed_url) 
        from the database using the game_id (UUID).
        """
        # 1. Define the secure, parameterized SELECT query
        query = """
        SELECT id, title, description, deployed_url 
        FROM games 
        WHERE id = %s
        """
        
        # 2. Delegate execution to the helper method
        data = self._execute_query(query, params=(game_id,), fetch_one=True)

        if data:
            # We only return the specific fields the Marketing Agent needs
            return {
                "id": data.get("id"),
                "title": data.get("title"),
                "description": data.get("description"),
                "deployed_url": data.get("deployed_url"),
            }
        
        self.logger.error(f"--- [DBManager] ERROR: Game ID '{game_id}' not found.")
        return None
    
    def save_twitter_post(self,game_id, data):
        """saving twitter post data in database"""
        try:    
            serialized_payload = json.dumps(data)
            query = (
                "INSERT INTO marketing_post (game_id, platform, payload_json, post_url, status) "
                "VALUES (%s, %s, %s, %s, %s)"
            )
            
            params = (
                game_id,
                "twitter",
                serialized_payload,
                "twitter.com/mock_url",
                "posted"
            )
            
            return self._execute_query(query, params)
        
        except Exception as e:
            self.logger.error(e)
    
    def save_linkedin_post(self,game_id, data):
        """
        Logs a new social media marketing post to the database.

        Args:
            game_id: The ID of the game being marketed.
            data: post data (e.g., 'twitter', 'facebook').

        Returns:
            True if the insertion was successful, False otherwise.
        """
        serialized_payload = json.dumps(data)
        query = (
            "INSERT INTO marketing_post (game_id, platform, payload_json, post_url, status) "
            "VALUES (%s, %s, %s, %s, %s)"
        )
        
        params = (
            game_id,
            "linkedin",
            serialized_payload,
            "linkedin.com/mock_url",
            "posted"
        )
        
        # 4. Execute the query using the internal execution method
        # Assuming self._execute_query is the internal method for running commands.
        return self._execute_query(query, params)

    def save_reddit_post(self,game_id, data):
        """
        Logs a new social media marketing post to the database.

        Args:
            game_id: The ID of the game being marketed.
            data: post data.

        Returns:
            True if the insertion was successful, False otherwise.
        """
        serialized_payload = json.dumps(data)
        query = (
            "INSERT INTO marketing_post (game_id, platform, payload_json, post_url, status) "
            "VALUES (%s, %s, %s, %s, %s)"
        )
        
        params = (
            game_id,
            "reddit",
            serialized_payload,
            "reddit.com/mock_url",
            "posted"
        )
        
        # 4. Execute the query using the internal execution method
        # Assuming self._execute_query is the internal method for running commands.
        return self._execute_query(query, params)
    
    def update_payments(self, user_id: str, game_id: str):
        query = (
            "INSERT INTO purchases (user_id, game_id, payment_method, amount, status) "
            "VALUES (%s, %s, 'stripe', 1.0, 'PAID')"
        )
        params = (user_id, game_id)
        
        # Execute the INSERT statement
        return self._execute_query(query, params)

    def check_payment_status(self, user_id: str, game_id: str) -> bool:
        """
        Checks the payments table if a successful transaction already exists.
        """
        query = (
            "SELECT COUNT(*) FROM payments "
            "WHERE user_id = %s AND game_id = %s"
        )
        params = (user_id, game_id)
        
        # Execute the query and fetch the single count result
        result = self._execute_query(query, params, fetch_one=True, fetch_columns=False)
        
        # The result is a tuple like (1,) or (0,). We check if the count > 0.
        count = result[0] if result else 0
        
        return count > 0
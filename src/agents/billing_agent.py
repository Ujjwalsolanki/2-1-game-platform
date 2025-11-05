from typing import Any, Dict, List

from db_manager import DBManager
from src.services.stripe_service import StripeService
from src.tools.logger import logger


class BillingAgent:
    """
    Manages the $1 access charge workflow for a game.
    """
    def __init__(self):
        self.logger = logger
        self.db_manager = DBManager()
        self.payment_service = StripeService()

    def get_purchased_games(self, user_id: str) -> List[Dict[str, str]]:
        self.logger.info('Getting all purchased games from db for user')
        return self.db_manager.get_purchased_games(user_id=user_id)

    def get_access_status(self, user_id: str, game_id: str) -> Dict[str, Any]:
        """
        The main method: Checks payment status and initiates charge if necessary.
        
        Args:
            user_id: The ID of the authenticated user.
            game_id: The ID of the game the user is trying to access.
            
        Returns:
            A status dictionary instructing the UI to redirect (payment) or 
            grant access (deployed_url).
        """
        # 1. Check if the user has already paid for this game
        if self.db_manager.check_payment_status(user_id, game_id):
            self.logger.info(f"User {user_id} has paid. Granting direct access.")
            
            # Retrieve the final deployed URL to grant access
            details = self.db_manager.get_game_details(game_id)
            return {
                "status": "ACCESS_GRANTED",
                "deployed_url": details.get("deployed_url")
            }
        
        # 2. If not paid, initiate the payment process
        else:
            return{
                "status": "ACCESS_DENIED",
                "deployed_url": ""
            }
    
    def initiate_payment(self, user_id, game_id, payment_token):
        self.logger.info('now we are charing user $1 for game')
        return self._handle_successful_payment(user_id, game_id, payment_token)

    def _handle_successful_payment(self, user_id: str, game_id: str, payment_token) -> bool:
        """
        Simulates the backend process upon receiving a successful payment webhook.
        """
        # 1. Verify the transaction with the payment service (security check)
        if self.payment_service.verify_webhook_payment(user_id, game_id):
            
            self.db_manager.update_payments(user_id, game_id)

            self.logger.info(f"successful payment for user {user_id}, game {game_id}")
            
            # Retrieve the final deployed URL to grant access
            details = self.db_manager.get_game_details(game_id)
            return {
                "status": "ACCESS_GRANTED",
                "deployed_url": details.get("deployed_url")
            }
        
        return {
                "status": "ACCESS_DENIED",
                "deployed_url": ""
            }
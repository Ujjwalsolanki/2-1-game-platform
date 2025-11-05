from typing import Any, Dict
from src.agents.game_generator import GameGeneratorAgent
from src.agents.marketing_agent import MarketingAgent
from src.tools.logger import logger


class GameCreationOrchestrator:
    """
    Manages the sequential execution of the automated game creation pipeline.
    Uses simple function calls since state management is handled by game_id.
    """
    def __init__(self):
        # Initialize the agents here
        self.logger = logger
        self.game_generator = GameGeneratorAgent()
        self.marketing_agent = MarketingAgent()

    def run_pipeline(self) -> Dict[str, Any]:
        """
        Executes the full pipeline: Generation followed by Marketing.
        """
        
        self.logger.info(f"*** Starting Orchestration for prompt: ***")
        
        try:
            # 1. GENERATION PHASE
            game_id = self.game_generator.generate_game()
            # 2. MARKETING PHASE
            self.marketing_agent.run_campaign(game_id)
            
            return {
                "status": "SUCCESS",
                "message": "Game created, deployed, and marketing campaign initiated.",
                "game_id": game_id
            }

        except Exception as e:
            self.logger.error(f"!!! ORCHESTRATION FAILED: {e}")
            
            return {
                "status": "FAILURE",
                "message": f"Pipeline failed during execution: {e}",
                "game_id": None
            }
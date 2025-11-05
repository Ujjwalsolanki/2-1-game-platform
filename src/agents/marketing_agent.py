from typing import Dict

from langchain_core.prompts import ChatPromptTemplate

from src.tools.logger import logger
from src.schemas.marketing_schemas import MarketingCampaignSchema
from src.services.linkedin_service import LinkedInService
from src.services.llm_service import LLMService
from src.services.reddit_service import RedditService
from src.services.twitter_service import TwitterService
from src.data.db_manager import DBManager



class MarketingAgent:
    """
    Orchestrates the marketing campaign based on a single game ID.
    Retrieves data, generates platform-specific content, and executes posts.
    """
    def __init__(self, llm_service: LLMService = LLMService()):
        self.logger = logger
        self.llm_client = llm_service.get_client() 
        self.db_manager = DBManager()
        
        # Instantiate mock social services
        self.twitter_service = TwitterService()
        self.reddit_service = RedditService()
        self.linkedin_service = LinkedInService()

    def run_campaign(self, game_id: str) -> Dict[str, str]:
        """
        The main orchestration function for the marketing campaign.
        
        Args:
            game_id: The UUID of the fully generated and deployed game.
            
        Returns:
            A dictionary summarizing the campaign status.
        """
        self.logger.info('Run campaigning initialized')
        if not game_id:
            return {"status": "FAILED", "reason": "Missing game_id."}

        # 1. Retrieve Game Details (Single Source of Truth)
        game_details = self.db_manager.get_game_details(game_id)

        if not game_details or not game_details.get("deployed_url"):
            return {"status": "FAILED", "reason": "Game data or deployed_url not found in database."}

        deployed_url = game_details["deployed_url"]
        
        self.logger.info(f"Marketing Agent starting for Game ID: {game_id}")
        self.logger.info(f"Game Title: {game_details['title']}")
        self.logger.info(f"Deployed URL: {deployed_url}")

        # 2. Generate Platform-Specific Content via LLM
        prompt_template = (
            "You are a master social media strategist. Generate a full marketing campaign for the game described below. "
            "Tailor the tone, content, and hashtags for each platform (Twitter/X, Reddit, LinkedIn). "
            "CRITICAL: The generated content MUST adhere strictly to the MarketingCampaignSchema."
            "\n\nGAME TITLE: {title}\nDESCRIPTION: {description}\n\n"
        )
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", prompt_template),
            ("user", "Generate the content now.")
        ])
        
        # Pass the Pydantic class directly
        structured_chain = prompt | self.llm_client.with_structured_output(MarketingCampaignSchema)

        try:
            # LLM Call for content generation
            llm_output = structured_chain.invoke({
                "title": game_details['title'], 
                "description": game_details['description']
            })
            campaign_data: MarketingCampaignSchema = llm_output


        except Exception as e:
            self.logger.error(f"LLM content generation failed: {e}")
            return {"status": "FAILED", "reason": f"LLM generation error: {e}"}

        # 3. Execute Campaign on Mock Services
        results = {}
        
        # Convert Pydantic object to dict for service consumption
        twitter_data = campaign_data.twitter_x.model_dump()
        reddit_data = campaign_data.reddit.model_dump()
        linkedin_data = campaign_data.linkedin.model_dump()

        self.db_manager.save_twitter_post(game_id, twitter_data)
        self.db_manager.save_linkedin_post(game_id, twitter_data)
        self.db_manager.save_reddit_post(game_id, twitter_data)

        results['twitter_x'] = self.twitter_service.post_campaign(twitter_data, deployed_url)
        results['reddit'] = self.reddit_service.post_campaign(reddit_data, deployed_url)
        results['linkedin'] = self.linkedin_service.post_campaign(linkedin_data, deployed_url)
        
        self.logger.info("status : COMPLETED campaign_results")
        return {"status": "COMPLETED", "campaign_results": results}
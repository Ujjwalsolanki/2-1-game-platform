
from src.tools.logger import logger


class RedditService:

    def __init__(self):
        self.logger = logger

    def post_campaign(self, data: str, deployed_url: str):
        self.logger.info("MOCK Reddit marketing post is live")
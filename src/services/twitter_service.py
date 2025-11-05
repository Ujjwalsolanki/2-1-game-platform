
from src.tools.logger import logger


class TwitterService:

    def __init__(self):
        self.logger = logger

    def post_campaign(self, data: str, deployed_url: str):
        self.logger.info("MOCK Twitter marketing post is live")
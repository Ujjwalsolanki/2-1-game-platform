
from src.tools.logger import logger


class LinkedInService:

    def __init__(self):
        self.logger = logger

    def post_campaign(self, data: str, deployed_url: str):
        self.logger.info("MOCK Linkedin marketing post is live")
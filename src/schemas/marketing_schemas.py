from pydantic import BaseModel, Field
from typing import Dict, List

class PlatformPost(BaseModel):
    """Schema for a single platform's marketing content."""
    headline: str = Field(
        description="A short, catchy headline (under 10 words) appropriate for the platform's audience."
    )
    body: str = Field(
        description="The main content of the post, tailored for the platform's style (e.g., professional for LinkedIn, short/hype for Twitter)."
    )
    hashtags: str = Field(
        description="A comma-separated string of 3-5 relevant hashtags."
    )
    call_to_action: str = Field(
        description="A final, compelling sentence urging the user to click the link."
    )

class MarketingCampaignSchema(BaseModel):
    """Overall schema for generating content across all social media platforms."""
    twitter_x: PlatformPost = Field(
        description="Content specifically designed for the rapid, trending, and concise nature of Twitter (X)."
    )
    reddit: PlatformPost = Field(
        description="Content designed for community engagement, often informative and slightly conversational, suitable for a relevant subreddit."
    )
    linkedin: PlatformPost = Field(
        description="Content designed to be professional and focus on the technical achievement or educational/development aspect of the game."
    )
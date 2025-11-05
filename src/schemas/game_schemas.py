from pydantic import BaseModel, Field

class GameCreationSchema(BaseModel):
    """
    Defines the structured output the LLM must generate. 
    All fields are mandatory as no default or Optional is used.
    """
    title: str = Field(
        description="A concise and creative title for the game, e.g., 'Pixel Planet Panic'."
    )
    description: str = Field(
        description="A detailed, engaging, short description (2-3 sentences) of the game."
    )
    html_code: str = Field(
        description="The complete, self-contained HTML structure (including <body>) for the game." \
        "including javascript and css"
    )
    
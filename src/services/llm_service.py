# llm_service.py
import os
from langchain_openai import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel
from dotenv import load_dotenv

from src.tools.logger import logger
load_dotenv()

class LLMService:
    """
    A service class that acts as a factory to provide configured LLM clients.
    All high-level logic (prompts, structure enforcement) is delegated to the agents.
    """
    
    def __init__(self, model_name: str = "gpt-4o-mini", temperature: float = 0.0):
        # Configuration details are stored here
        self.logger = logger
        self._model_name = model_name
        self._temperature = temperature

    def get_client(self) -> BaseChatModel:
        """
        Returns a configured instance of the LLM client (LangChain ChatModel).
        
        The agents will use this client for all interactions (structured output, 
        tool calling, and chat).
        """
        # Note: API key loading is handled automatically by LangChain if the key
        # is set in the environment variables (e.g., OPENAI_API_KEY).
        self.logger.info(f"LLM client created model: {self._model_name}")
        client = ChatOpenAI(
            model=self._model_name,
            temperature=self._temperature,
        )
        return client
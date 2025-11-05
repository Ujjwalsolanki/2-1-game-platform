import random
import uuid
from pathlib import Path
from typing import Optional

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate

# --- External Service and Schema Imports (Assume these files exist) ---
from src.services.git_handler import GitHandler
from src.tools.logger import logger

from src.data.db_manager import DBManager
from src.schemas.game_schemas import GameCreationSchema
from src.services.llm_service import LLMService

# --- Configuration ---
# Directory where generated HTML and JS files will be stored
OUTPUT_DIR = Path("./server/games")

class GameGeneratorAgent:
    """
    Handles the entire process of generating game code using an LLM, 
    saving files into a UUID-specific directory, and logging metadata 
    in a single database transaction.
    """
    def __init__(self, llm_service: LLMService = LLMService()):
        # Correcting access for mock service
        self.logger = logger
        self.llm_client = llm_service.get_client() 
        self.db_manager = DBManager()
        self.git_handler = GitHandler()
        self._ensure_output_dir()
        # The parser is no longer needed here as it's handled by with_structured_output

    def _ensure_output_dir(self):
        """Ensures the local output directory exists."""
        OUTPUT_DIR.mkdir(exist_ok=True)
        self.logger.info(f"Output directory ensured at: {OUTPUT_DIR.resolve()}")

    def generate_game(self, user_prompt: Optional[str] = None) -> str:
        """
        The main function that orchestrates the generation process. If user_prompt is None,
        it generates a prompt automatically.

        Args:
            user_prompt: The user's request for a game idea, or None for automation.

        Returns:
            The path to the generated HTML file.
        """
        # 1. Automate Prompt Generation if not provided
        GAME_CATEGORIES = ['Tic-Tac-Toe', 'Minesweeper', 'Connect Four', 'Battleship', 'Snake' , 'Breakout/Arkanoid', 'Space Shooter (Top-Down)', 'Flappy Bird Clone', 'Hangman', 'Word Scramble/Unscramble' , 'Typing Speed Test', 'Text Adventure/Interactive Fiction', 'Number Guessing Game', 'Simon Says', 'Sudoku (Basic 3x3 or 4x4)' , 'Memory Card Match', 'Rock, Paper, Scissors', 'Coin Flip/Roulette', 'Clicker/Idle Game', 'Trivia Quiz' ]

        # 2. Define LLM Prompt and Structure
        system_instruction = (
            "You are an expert game developer that generates a **single, self-contained HTML file** "
            "for simple 2D web games. Your output MUST strictly adhere to the provided schema. "
            "Ensure the game is unique and visually distinct from typical templates."
            "CRITICAL: The generated game logic, especially for quizzes or ordering, MUST BE FACTUALLY AND LOGICALLY CORRECT. Verify the solution before generating the code. "
            "The 'html_code' field MUST include ALL HTML, ALL CSS (in a <style> block), and "
            "ALL JAVASCRIPT (in a <script> block, typically before </body>). The generated file must be immediately runnable. Also Make sure to provide instruction on same html page that how to play that game "
        )

        random_game_category = random.choice(GAME_CATEGORIES)

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_instruction),
                ("user", f"Generate a simple game based on the following idea: {random_game_category}"),
            ]
        )

        # Pass the Pydantic class (GameCreationSchema) directly
        structured_chain = prompt | self.llm_client.with_structured_output(GameCreationSchema)
        
        self.logger.info("--- Calling LLM for game content generation... ---")
        try:
            # LLM Call and Parsing
            llm_output = structured_chain.invoke({})
            game_data: GameCreationSchema = llm_output

        except Exception as e:
            self.logger.error(f"An error occurred during LLM invocation or parsing: {e}")
            raise RuntimeError("LLM failed to generate structured output.")

        # 3. Generate UUID and Define Path (SINGLE CALL ENABLED)
        game_id_uuid = str(uuid.uuid4())
        
        # 4. Create Game's dedicated subdirectory based on the UUID
        game_dir = OUTPUT_DIR / game_id_uuid
        game_dir.mkdir(exist_ok=True)
        self.logger.info(f"Created dedicated directory: {game_dir}")

        # 5. Create Standardized File Paths within the new folder
        html_filename = "index.html" # Only one file to save
        html_filepath = game_dir / html_filename

        # 6. The LLM now provides the final_html_content directly in game_data.html_code

        # 7. Save Single Combined HTML File
        try:
            # Saving the complete, runnable HTML file directly
            with open(html_filepath, 'w', encoding='utf-8') as f:
                f.write(game_data.html_code)
            self.logger.info(f"Saved combined HTML/JS/CSS to: {html_filepath}")

        except IOError as e:
            self.logger.error(f"Failed to save file: {e}")
            # Log the failure to the DB
            raise RuntimeError("File system error during game saving.")

        # 8. Single DB Insertion with all final data
        final_log_data = {
            "id": game_id_uuid, 
            "title": game_data.title,
            "description": game_data.description,
            # This field now contains all code (HTML, CSS, JS)
            "html_code": game_data.html_code, 
            "file_url": str(html_filepath.relative_to(OUTPUT_DIR)), 
            "deployed_url": str(html_filepath.relative_to(OUTPUT_DIR)), 
        }
        self.db_manager.insert_new_game(final_log_data)
        self.logger.info("Game is created in database")
        self.git_handler.push_file_to_repo(html_filename)
        self.logger.info("Game file is updated on git repo")

        self.logger.info(f"--- Generation Complete! Game ID: {game_id_uuid} ---")
        return game_id_uuid
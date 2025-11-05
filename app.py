# This will create API endpoints for billing agent.

from fastapi import FastAPI, Form, Header, HTTPException, status
from typing import Any, Dict, Optional

from src.agents.billing_agent import BillingAgent
from src.tools.logger import logger

billing_agent = BillingAgent()

app = FastAPI(
    title="Game Monetization Gateway",
    description="Secure entry point for game access and billing status."
)


@app.get("/", tags=["Health"])
async def read_root():
    """Health check endpoint."""
    logger.info("Billing Gateway is online.")
    return {"message": "Billing Gateway is online."}


@app.get("/api/v1/get_purchased_games/", tags=["Access"])
async def check_game_access(
    game_id: str,
    x_user_id: Optional[str] = Header(None, alias="X-User-ID", description="Authenticated user ID.")
):
    """
    1. check_game_access(user_id, game_id)
    Checks if the user has paid. Returns deployed URL or payment redirect link.
    """
    if not x_user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User authentication required (X-User-ID).")

    # This calls the BillingAgent directly without a caching layer
    logger.info(f'Getting all the purchased games for user {x_user_id}')
    access_result = billing_agent.get_purchased_games(x_user_id)
    
    return access_result



@app.get("/api/v1/access/{game_id}", tags=["Access"])
async def check_game_access(
    game_id: str,
    x_user_id: Optional[str] = Header(None, alias="X-User-ID", description="Authenticated user ID.")
):
    """
    check_game_access(user_id, game_id)
    Checks if the user has paid. Returns deployed URL or payment redirect link.
    """
    if not x_user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User authentication required (X-User-ID).")

    # This calls the BillingAgent directly without a caching layer
    logger.info(f"Getting URL access for specific game {game_id} for user {x_user_id}")
    access_result = billing_agent.get_access_status(x_user_id, game_id)
    
    return access_result


@app.post("/api/v1/charge", tags=["Access"])
async def post_payment_token(
    user_id: str = Form(..., description="The ID of the user requesting access."),
    game_id: str = Form(..., description="The ID of the game being purchased."),
    payment_token: str = Form(..., description="Secure payment token (e.g., card token or mock data).")
) -> Dict[str, Any]:
    """
    Processes the client-initiated payment (card token) and grants game access upon success.
    """
    try:
        logger.info(f'Initiating payment for user {user_id}')
        access_result = billing_agent.initiate_payment(
            user_id=user_id,
            game_id=game_id,
            payment_token=payment_token
        )

        return access_result

    except Exception as e:
        # Log the critical error
        logger.error(f"CRITICAL PAYMENT ERROR: User {user_id}, Game {game_id}, Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not process payment due to a server error."
        )
from src.agents.billing_agent import BillingAgent


def initiate_payment_test():
    
    billing_agent = BillingAgent()

    user_id = ''
    game_id = ''
    result = billing_agent.initiate_payment(user_id=user_id, game_id=game_id)

    assert result['status'] == "ACCESS_GRANTED" 

def get_access_status_test():
    
    billing_agent = BillingAgent()

    user_id = ''
    game_id = ''
    result = billing_agent.get_access_status(user_id=user_id, game_id=game_id)

    assert result['status'] == "ACCESS_GRANTED" 

def get_purchased_games_test():
    
    billing_agent = BillingAgent()

    user_id = ''
    result = billing_agent.get_purchased_games(user_id=user_id)

    assert result is not None
    assert isinstance(result, dict) 


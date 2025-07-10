from Y_config import load_env

def check_risk(trade_history, current_pnl):
    """
    Checks if trading should continue based on risk parameters.
    
    Args:
        trade_history (list): List of dictionaries containing previous trades of the day.
                             Each trade contains details like entry price, exit price,
                             quantity, and P&L.
        current_pnl (float): Current profit/loss for the day.
        
    Returns:
        bool: True if trading can continue, False if risk limits have been reached.
    """

    config = load_env()
    STOP_LOSS = float(config.get('STOP_LOSS'))
    TAKE_PROFIT = float(config.get('TAKE_PROFIT'))
    MAX_DAILY_LOSS = float(config.get('MAX_DAILY_LOSS'))
    MAX_TRADES_PER_DAY = int(config.get('MAX_TRADES_PER_DAY'))

    if current_pnl <= -MAX_DAILY_LOSS:
        return False

    if len(trade_history) >= MAX_TRADES_PER_DAY:
        return False
    
    for trade in trade_history:
        if trade['pnl'] < -STOP_LOSS:
            return False
        if trade['pnl'] > TAKE_PROFIT:
            return False

    return True

if __name__ == '__main__':
    example_trades = [{'pnl': -500, 'id': 1}]
    print(check_risk(example_trades, current_pnl=-200))
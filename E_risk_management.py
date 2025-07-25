from Y_config import load_env

def check_risk(trade_history, current_pnl, current_position_pnl=0):
    """
    Checks if trading should continue based on risk parameters.
    
    Args:
        trade_history (list): List of dictionaries containing previous trades
        current_pnl (float): Current profit/loss for the day
        current_position_pnl (float): Current unrealized P&L of open position
        
    Returns:
        dict: Contains 'continue_trading' (bool) and 'reason' (str) if trading should stop
    """
    config = load_env()
    STOP_LOSS = float(config.get('STOP_LOSS'))
    TAKE_PROFIT = float(config.get('TAKE_PROFIT'))
    MAX_DAILY_LOSS = float(config.get('MAX_DAILY_LOSS'))
    MAX_TRADES_PER_DAY = int(config.get('MAX_TRADES_PER_DAY'))

    result = {'continue_trading': True, 'reason': None}
    
    if current_pnl <= -MAX_DAILY_LOSS:
        result['continue_trading'] = False
        result['reason'] = 'MAX_DAILY_LOSS'
        return result

    if len(trade_history) >= MAX_TRADES_PER_DAY:
        result['continue_trading'] = False
        result['reason'] = 'MAX_TRADES_PER_DAY'
        return result
    
    if current_position_pnl <= -STOP_LOSS:
        result['continue_trading'] = False
        result['reason'] = 'STOP_LOSS'
        return result
        
    if current_position_pnl >= TAKE_PROFIT:
        result['continue_trading'] = False
        result['reason'] = 'TAKE_PROFIT'
        return result

    return result

if __name__ == '__main__':
    example_trades = [{'pnl': -500, 'id': 1}]
    print(check_risk(example_trades, current_pnl=-200))
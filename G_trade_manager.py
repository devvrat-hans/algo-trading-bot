from Y_config import load_env
from B_market_data import market_data
from C_strategy import generate_signal
from D_order_execution import execute_buy_order, execute_sell_order
from E_risk_management import check_risk
from dotenv import load_dotenv
import time
from datetime import datetime

load_dotenv()

def manage_trades():
    """
    Orchestrates the complete trading workflow.
    
    Args:
        None
        
    Returns:
        dict: Summary of trading activity for the session including:
              - total_trades (int): Number of trades executed
              - profitable_trades (int): Number of profitable trades
              - losing_trades (int): Number of losing trades
              - net_pnl (float): Net profit/loss for the session
              - win_rate (float): Percentage of profitable trades
    """

    config = load_env()
    INSTRUMENT_KEY = config.get('INSTRUMENT_KEY')
    UNIT = config.get('UNIT')
    INTERVAL = config.get('INTERVAL')
    QUANTITY = config.get('QUANTITY')
    TRADE_CHECK_INTERVAL = config.get('TRADE_CHECK_INTERVAL')
    MAX_RUNTIME = config.get('MAX_RUNTIME')

    trade_history = []
    current_pnl = 0.0
    start_time = time.time()
    last_signal = None
    iteration = 0

    print(f"{'=' * 80}")
    print(f"TRADING SESSION STARTED AT {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"INSTRUMENT: {INSTRUMENT_KEY}, QUANTITY: {QUANTITY}, INTERVAL: {INTERVAL} {UNIT}")
    print(f"MAX RUNTIME: {MAX_RUNTIME/60:.1f} minutes, CHECK INTERVAL: {TRADE_CHECK_INTERVAL} seconds")
    print(f"{'=' * 80}")

    while check_risk(trade_history, current_pnl) and (time.time() - start_time < MAX_RUNTIME):
        iteration += 1
        current_time = datetime.now().strftime("%H:%M:%S")
        elapsed = round((time.time() - start_time) / 60, 2)
        
        print(f"\n[{current_time}] Iteration {iteration} | Running for {elapsed} minutes")
        
        price_data = market_data(INSTRUMENT_KEY, UNIT, INTERVAL)
        if not price_data.empty:
            latest_close = price_data['Close'].iloc[-1] if not price_data.empty else "N/A"
            latest_timestamp = price_data['Timestamp'].iloc[-1] if not price_data.empty else "N/A"
            print(f"Latest price data: Close={latest_close} at {latest_timestamp}")
        else:
            print("Warning: No price data available")
        
        signal = generate_signal(price_data)
        print(f"Signal generated: {signal} | Previous signal: {last_signal}")
        
        trade = None

        if signal != 'hold' and signal != last_signal:
            print(f"\n{'*' * 20} ACTION TRIGGERED: {signal.upper()} {'*' * 20}")
            if signal == 'buy':
                trade = execute_buy_order(INSTRUMENT_KEY, QUANTITY)
                if trade:
                    print(f"✅ Buy order executed at: {trade.get('price', 'N/A')}") 
                    print(f"Order details: {trade}")
            elif signal == 'sell':
                trade = execute_sell_order(INSTRUMENT_KEY, QUANTITY)
                if trade:
                    print(f"✅ Sell order executed at: {trade.get('price', 'N/A')}")
                    print(f"Order details: {trade}")
            
            last_signal = signal 

            if trade:
                trade_history.append(trade)
                current_pnl += trade.get('pnl', 0)
                print(f"➕ Trade #{len(trade_history)} added to history")
                print(f"💰 Current P&L: {current_pnl:.2f}")
                
                profitable_trades = sum(1 for t in trade_history if t.get('pnl', 0) > 0)
                current_win_rate = (profitable_trades / len(trade_history)) * 100 if trade_history else 0
                print(f"📊 Current win rate: {current_win_rate:.1f}%")
        else:
            print(f"ℹ️ No action taken. Maintaining current position: {last_signal if last_signal else 'none'}")
        
        print(f"Current trading stats:")
        print(f"- Total trades: {len(trade_history)}")
        print(f"- Current P&L: {current_pnl:.2f}")
        print(f"- Time left: {round((MAX_RUNTIME - (time.time() - start_time)) / 60, 2)} minutes")
        
        time.sleep(TRADE_CHECK_INTERVAL)

    print(f"\n{'=' * 80}")
    print(f"TRADING SESSION ENDED AT {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'=' * 80}")

    total_trades = len(trade_history)
    profitable_trades = sum(1 for t in trade_history if t.get('pnl', 0) > 0)
    losing_trades = sum(1 for t in trade_history if t.get('pnl', 0) < 0)
    net_pnl = sum(t.get('pnl', 0) for t in trade_history)
    win_rate = (profitable_trades / total_trades) * 100 if total_trades > 0 else 0

    return {
        'total_trades': total_trades,
        'profitable_trades': profitable_trades,
        'losing_trades': losing_trades,
        'net_pnl': net_pnl,
        'win_rate': win_rate
    }

if __name__ == '__main__':
    summary = manage_trades()
    print("\n📊 TRADING SESSION SUMMARY 📊")
    print(f"{'=' * 40}")
    for key, value in summary.items():
        if 'pnl' in key:
            print(f"{key.replace('_', ' ').title()}: {value:.2f}")
        elif 'rate' in key:
            print(f"{key.replace('_', ' ').title()}: {value:.1f}%")
        else:
            print(f"{key.replace('_', ' ').title()}: {value}")
    print(f"{'=' * 40}")
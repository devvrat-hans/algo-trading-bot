import sys
sys.dont_write_bytecode = True

from Y_config import load_env
from B_market_data import market_data
from C_strategy import process_market_data
from D_order_execution import execute_buy_order, execute_sell_order
from E_risk_management import check_risk
from F_get_prices import get_live_price
from H_get_instrument_key import get_trading_instrument
import time
from datetime import datetime
from A_account_connect import account_connect

def get_atm_option_instrument(underlying_price, option_type):
    """
    Get ATM option instrument key based on underlying price.
    
    Args:
        underlying_price (float): Current price of underlying
        option_type (str): 'CE' for Call or 'PE' for Put
        
    Returns:
        str: ATM option instrument key or None if not found
    """
    instruments_df = get_trading_instrument()
    
    if instruments_df.empty:
        return None
    
    # Filter for specific option type
    options_df = instruments_df[instruments_df['instrument_type'] == option_type]
    
    if options_df.empty:
        return None
    
    # Find ATM strike (rounding to nearest 50 for Bank Nifty)
    atm_strike = round(underlying_price / 50) * 50
    
    # Filter for ATM strike
    atm_options = options_df[options_df['strike'] == atm_strike]
    
    if not atm_options.empty:
        return atm_options.iloc[0]['instrument_key']
    
    # If exact ATM not found, find nearest strike as a fallback
    options_df['strike_diff'] = abs(options_df['strike'] - atm_strike)
    nearest_option = options_df.loc[options_df['strike_diff'].idxmin()]
    
    return nearest_option['instrument_key']

def close_position(access_token, position_instrument, position_entry_price, current_position, trade_history, current_pnl, quantity):
    """Helper function to close a position and update trade history"""
    print(f"\n{'='*80}\n📊 CLOSING POSITION: {current_position} at {datetime.now().strftime('%H:%M:%S')}\n{'='*80}")
    # To close a long position (CE or PE), we need to sell it.
    sell_result = execute_sell_order(access_token, position_instrument, quantity)
    
    if sell_result:
        exit_price = get_live_price(access_token, position_instrument)
        if exit_price is None:
            print("❌ Could not fetch exit price. P&L cannot be calculated.")
            exit_price = position_entry_price # Assume no change for record keeping
        
        trade_pnl = (exit_price - position_entry_price) * quantity
        current_pnl += trade_pnl
        
        trade_history.append({
            'entry_time': datetime.now(),
            'entry_price': position_entry_price,
            'exit_price': exit_price,
            'quantity': quantity,
            'pnl': trade_pnl,
            'signal': current_position,
            'instrument': position_instrument
        })
        
        print(f"✅ Position closed successfully")
        print(f"  Instrument: {position_instrument}")
        print(f"  Entry price: {position_entry_price:.2f}")
        print(f"  Exit price: {exit_price:.2f}")
        print(f"  Quantity: {quantity}")
        print(f"  Trade P&L: {'📈' if trade_pnl > 0 else '📉'} {trade_pnl:.2f}")
    else:
        print("❌ Failed to close position")
    
    return None, None, 0.0, current_pnl

def print_trading_summary(trade_history, current_pnl, runtime):
    """Print a summary of the trading session so far"""
    print(f"\n{'='*80}")
    print(f"📈 TRADING SESSION SUMMARY - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}")
    print(f"  ⏱️  Runtime: {runtime:.2f} minutes")
    print(f"  💰 Current P&L: {current_pnl:.2f}")
    print(f"  🔢 Total trades: {len(trade_history)}")
    
    if trade_history:
        profitable_trades = len([t for t in trade_history if t['pnl'] > 0])
        losing_trades = len([t for t in trade_history if t['pnl'] <= 0])
        win_rate = (profitable_trades / len(trade_history) * 100)
        print(f"  ✅ Profitable trades: {profitable_trades}")
        print(f"  ❌ Losing trades: {losing_trades}")
        print(f"  📊 Win rate: {win_rate:.2f}%")
        
        if trade_history:
            print(f"\n  RECENT TRADES:")
            for i, trade in enumerate(trade_history[-3:]):
                print(f"   {i+1}. {trade['instrument']} - {'📈' if trade['pnl'] > 0 else '📉'} {trade['pnl']:.2f}")
    print(f"{'='*80}\n")

def manage_trades():
    """
    Orchestrates the complete trading workflow with ATM options.
    
    Returns:
        dict: Summary of trading activity for the session
    """
    config = load_env()
    account_details = account_connect()
    access_token = account_details.get('access_token')
    
    instrument_key = config.get('INSTRUMENT_KEY') # This is the underlying index
    unit = config.get('UNIT')
    interval = config.get('INTERVAL')
    quantity = config.get('QUANTITY')
    trade_check_interval = config.get('TRADE_CHECK_INTERVAL')
    max_runtime = config.get('MAX_RUNTIME')
    
    trade_history = []
    current_pnl = 0.0
    start_time = time.time()
    last_signal = None
    iteration = 0
    current_position = None # Will be 'CE' or 'PE'
    position_entry_price = 0.0
    position_instrument = None # The actual option instrument key
    
    print(f"\n{'='*80}")
    print(f"🚀 TRADING SESSION STARTED - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}")
    print(f"  📈 Underlying Instrument: {instrument_key}")
    print(f"  📊 Chart Interval: {interval} {unit}")
    print(f"  🔢 Quantity per trade: {quantity}")
    print(f"  ⏱️  Check Interval: {trade_check_interval}s")
    print(f"  ⏰ Maximum Runtime: {max_runtime/3600:.2f} hours")
    print(f"{'='*80}\n")
    
    while time.time() - start_time < max_runtime:
        iteration += 1
        elapsed_minutes = (time.time() - start_time) / 60
        
        print(f"\n{'*'*80}")
        print(f"ITERATION {iteration} - {datetime.now().strftime('%H:%M:%S')} (Runtime: {elapsed_minutes:.2f} min)")
        print(f"{'*'*80}")
        
        if iteration > 1 and iteration % 10 == 0:
            print_trading_summary(trade_history, current_pnl, elapsed_minutes)
        
        current_position_pnl = 0
        if current_position:
            current_price = get_live_price(access_token, position_instrument)
            if current_price is not None and position_entry_price > 0:
                current_position_pnl = (current_price - position_entry_price) * quantity
                print(f"📍 Current position: {current_position}")
                print(f"  Instrument: {position_instrument}")
                print(f"  Entry price: {position_entry_price:.2f}")
                print(f"  Current price: {current_price:.2f}")
                print(f"  Unrealized P&L: {'📈' if current_position_pnl > 0 else '📉'} {current_position_pnl:.2f}")
            else:
                print(f"📍 Current position: {current_position} (Could not fetch live price)")
        else:
            print("📍 No active position")
        
        risk_result = check_risk(trade_history, current_pnl, current_position_pnl)
        if not risk_result['continue_trading']:
            print(f"\n⚠️ RISK LIMIT REACHED: {risk_result['reason']} ⚠️")
            
            if current_position:
                print(f"⏰ Closing position due to risk limit.")
                current_position, position_instrument, position_entry_price, current_pnl = close_position(
                    access_token, position_instrument, position_entry_price, current_position, 
                    trade_history, current_pnl, quantity
                )
            
            if risk_result['reason'] in ['MAX_TRADES_PER_DAY', 'MAX_DAILY_LOSS']:
                print(f"⛔ {risk_result['reason']} limit hit. Stopping trading for the day.")
                break
        
        print("\n📊 Fetching market data for underlying...")
        req_market_data = market_data(access_token, instrument_key, unit, interval)
        
        if req_market_data is None or req_market_data.empty:
            print("❌ No market data available for underlying. Waiting...")
            time.sleep(trade_check_interval)
            continue
        
        print("🧮 Analyzing market data and generating signal...")
        signal = process_market_data(req_market_data)
        print(f"🔍 Signal generated: {signal}")
        
        # We only act on new, non-hold signals
        if signal != 'hold' and signal != last_signal:
            print(f"\n🔄 New signal detected: {signal.upper()}")
            
            if current_position is not None:
                print("🔄 Closing current position before taking new position...")
                current_position, position_instrument, position_entry_price, current_pnl = close_position(
                    access_token, position_instrument, position_entry_price, current_position, 
                    trade_history, current_pnl, quantity
                )
            
            print("🔷 Processing new position...")
            underlying_price = get_live_price(access_token, instrument_key)
            if underlying_price is None:
                print("❌ Could not fetch underlying price. Cannot determine ATM strike. Skipping trade.")
                time.sleep(trade_check_interval)
                continue
            
            print(f"💹 Underlying price: {underlying_price:.2f}")
            
            option_type_to_buy = 'CE' if signal == 'buy' else 'PE'
            print(f"🔎 Searching for ATM {option_type_to_buy} option...")
            
            option_instrument_to_trade = get_atm_option_instrument(underlying_price, option_type_to_buy)
            
            if option_instrument_to_trade:
                print(f"  Selected ATM {option_type_to_buy}: {option_instrument_to_trade}")
                # We always BUY the option (either CE or PE)
                buy_result = execute_buy_order(access_token, option_instrument_to_trade, quantity)
                
                if buy_result:
                    print(f"✅ BUY order placed for {option_instrument_to_trade}")
                    current_position = option_type_to_buy
                    position_instrument = option_instrument_to_trade
                    # Get entry price after placing order
                    position_entry_price = get_live_price(access_token, position_instrument)
                    if position_entry_price is not None:
                         print(f"  Entry price: {position_entry_price:.2f}")
                    else:
                        print("  Could not confirm entry price.")
                        position_entry_price = 0 # Set to 0 if fetch fails
                else:
                    print(f"❌ Failed to execute buy order for {option_instrument_to_trade}")
            else:
                print(f"❌ Could not find suitable {option_type_to_buy} option to trade.")
        
        last_signal = signal
        
        print(f"\n💰 Current P&L: {current_pnl:.2f}")
        print(f"📝 Total trades: {len(trade_history)}")
        
        print(f"\n⏱️  Waiting {trade_check_interval} seconds until next check...")
        time.sleep(trade_check_interval)
    
    if current_position is not None:
        print("\n⏰ Session ending. Closing final position.")
        current_position, position_instrument, position_entry_price, current_pnl = close_position(
            access_token, position_instrument, position_entry_price, current_position, 
            trade_history, current_pnl, quantity
        )
    
    profitable_trades = len([t for t in trade_history if t['pnl'] > 0])
    losing_trades = len([t for t in trade_history if t['pnl'] <= 0])
    win_rate = (profitable_trades / len(trade_history) * 100) if trade_history else 0
    
    summary = {
        'total_trades': len(trade_history),
        'profitable_trades': profitable_trades,
        'losing_trades': losing_trades,
        'net_pnl': current_pnl,
        'win_rate': win_rate
    }
    
    print(f"\n{'='*80}")
    print(f"🏁 TRADING SESSION ENDED - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}")
    print(f"  📈 Total trades: {summary['total_trades']}")
    print(f"  ✅ Profitable trades: {summary['profitable_trades']}")
    print(f"  ❌ Losing trades: {summary['losing_trades']}")
    print(f"  💰 Net P&L: {summary['net_pnl']:.2f}")
    print(f"  📊 Win rate: {summary['win_rate']:.2f}%")
    print(f"{'='*80}")
    
    return summary

if __name__ == '__main__':
    summary = manage_trades()
    print(f"\nFinal Summary: {summary}")
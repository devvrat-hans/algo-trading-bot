import sys
sys.dont_write_bytecode = True

from Y_config import load_env
from B_market_data import market_data
from C_strategy import process_market_data
from D_order_execution import execute_buy_order, execute_sell_order
from E_risk_management import check_risk
from F_get_prices import get_live_price
import time
from datetime import datetime, timedelta
from A_account_connect import account_connect

def get_current_expiry():
    """Get current weekly expiry date in required format"""
    today = datetime.now()
    days_until_thursday = (3 - today.weekday()) % 7
    expiry_date = today + timedelta(days=days_until_thursday)
    return expiry_date.strftime("%d%b").upper()

def get_atm_option_instrument(underlying_price, expiry_date, option_type):
    """
    Get ATM option instrument key based on underlying price.
    
    Args:
        underlying_price (float): Current price of underlying
        expiry_date (str): Option expiry date
        option_type (str): 'CE' for Call or 'PE' for Put
        
    Returns:
        str: ATM option instrument key
    """
    atm_strike = round(underlying_price / 50) * 50
    instrument_key = f"NSE_FO|{atm_strike}{option_type}{expiry_date}"
    return instrument_key

def close_position(access_token, position_instrument, position_entry_price, current_position, trade_history, current_pnl, quantity):
    """Helper function to close a position and update trade history"""
    print(f"\n{'='*80}\n📊 CLOSING POSITION: {current_position} at {datetime.now().strftime('%H:%M:%S')}\n{'='*80}")
    sell_result = execute_sell_order(access_token, position_instrument, quantity)
    
    if sell_result:
        exit_price = get_live_price(access_token, position_instrument)
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
        losing_trades = len([t for t in trade_history if t['pnl'] < 0])
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
    # Load config and connect to account only ONCE
    config = load_env()
    account_details = account_connect()
    access_token = account_details.get('access_token')
    
    # Get trading parameters from config
    instrument_key = config.get('INSTRUMENT_KEY')
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
    current_position = None
    position_entry_price = 0.0
    position_instrument = None
    
    print(f"\n{'='*80}")
    print(f"🚀 TRADING SESSION STARTED - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}")
    print(f"  📈 Trading instrument: {instrument_key}")
    print(f"  📊 Chart interval: {interval} {unit}")
    print(f"  🔢 Quantity: {quantity}")
    print(f"  ⏱️  Check interval: {trade_check_interval}s")
    print(f"  ⏰ Maximum runtime: {max_runtime/3600:.2f} hours")
    print(f"{'='*80}\n")
    
    while time.time() - start_time < max_runtime:
        iteration += 1
        elapsed_minutes = (time.time() - start_time) / 60
        
        print(f"\n{'*'*80}")
        print(f"ITERATION {iteration} - {datetime.now().strftime('%H:%M:%S')} (Runtime: {elapsed_minutes:.2f} min)")
        print(f"{'*'*80}")
        
        # Print trading summary every 10 iterations
        if iteration % 10 == 0:
            print_trading_summary(trade_history, current_pnl, elapsed_minutes)
        
        current_position_pnl = 0
        if current_position:
            current_price = get_live_price(access_token, position_instrument)
            current_position_pnl = (current_price - position_entry_price) * quantity
            print(f"📍 Current position: {current_position}")
            print(f"  Instrument: {position_instrument}")
            print(f"  Entry price: {position_entry_price:.2f}")
            print(f"  Current price: {current_price:.2f}")
            print(f"  Unrealized P&L: {'📈' if current_position_pnl > 0 else '📉'} {current_position_pnl:.2f}")
        else:
            print("📍 No active position")
        
        risk_result = check_risk(trade_history, current_pnl, current_position_pnl)
        if not risk_result['continue_trading']:
            print(f"\n⚠️ RISK LIMIT REACHED: {risk_result['reason']} ⚠️")
            
            # Immediately close position if stop loss or take profit hit
            if risk_result['reason'] in ['STOP_LOSS', 'TAKE_PROFIT'] and current_position:
                print(f"⏰ {risk_result['reason']} triggered. Closing position immediately.")
                current_position, position_instrument, position_entry_price, current_pnl = close_position(
                    access_token, position_instrument, position_entry_price, current_position, 
                    trade_history, current_pnl, quantity
                )
            
            # If max trades or max loss hit, stop trading completely
            if risk_result['reason'] in ['MAX_TRADES_PER_DAY', 'MAX_DAILY_LOSS']:
                print(f"⛔ {risk_result['reason']} limit hit. Stopping trading.")
                if current_position:
                    current_position, position_instrument, position_entry_price, current_pnl = close_position(
                        access_token, position_instrument, position_entry_price, current_position, 
                        trade_history, current_pnl, quantity
                    )
                break
        
        print("\n📊 Fetching market data...")
        req_market_data = market_data(access_token, instrument_key, unit, interval)
        
        if req_market_data is None or req_market_data.empty:
            print("❌ No market data available")
            time.sleep(trade_check_interval)
            continue
        
        print("🧮 Analyzing market data and generating signal...")
        signal = process_market_data(req_market_data)
        print(f"🔍 Signal generated: {signal}")
        
        underlying_price = get_live_price(access_token, instrument_key)
        print(f"💹 Underlying price: {underlying_price:.2f}")
        
        current_time = datetime.now()
        expiry_date = get_current_expiry()
        
        if signal != 'hold' and signal != last_signal:
            print(f"\n🔄 New signal detected: {signal}")
            
            if current_position is not None:
                print("🔄 Closing current position before taking new position")
                current_position, position_instrument, position_entry_price, current_pnl = close_position(
                    access_token, position_instrument, position_entry_price, current_position, 
                    trade_history, current_pnl, quantity
                )
            
            if signal == 'buy':
                print("\n🔷 Processing BUY signal")
                atm_ce_instrument = get_atm_option_instrument(underlying_price, expiry_date, 'CE')
                print(f"  Selected ATM CE: {atm_ce_instrument}")
                buy_result = execute_buy_order(access_token, atm_ce_instrument, quantity)
                
                if buy_result:
                    current_position = 'CE'
                    position_instrument = atm_ce_instrument
                    position_entry_price = get_live_price(access_token, atm_ce_instrument)
                    print(f"✅ Bought ATM CE: {atm_ce_instrument} at {position_entry_price:.2f}")
                else:
                    print("❌ Failed to execute buy order")
            
            elif signal == 'sell':
                print("\n🔶 Processing SELL signal")
                atm_pe_instrument = get_atm_option_instrument(underlying_price, expiry_date, 'PE')
                print(f"  Selected ATM PE: {atm_pe_instrument}")
                buy_result = execute_buy_order(access_token, atm_pe_instrument, quantity)
                
                if buy_result:
                    current_position = 'PE'
                    position_instrument = atm_pe_instrument
                    position_entry_price = get_live_price(access_token, atm_pe_instrument)
                    print(f"✅ Bought ATM PE: {atm_pe_instrument} at {position_entry_price:.2f}")
                else:
                    print("❌ Failed to execute buy order")
        
        last_signal = signal
        
        print(f"\n💰 Current P&L: {current_pnl:.2f}")
        print(f"📝 Total trades: {len(trade_history)}")
        
        print(f"\n⏱️  Waiting {trade_check_interval} seconds until next check...")
        time.sleep(trade_check_interval)
    
    if current_position is not None:
        print("\n⏰ Maximum runtime reached. Closing final position before session end.")
        current_position, position_instrument, position_entry_price, current_pnl = close_position(
            access_token, position_instrument, position_entry_price, current_position, 
            trade_history, current_pnl, quantity
        )
    
    profitable_trades = len([t for t in trade_history if t['pnl'] > 0])
    losing_trades = len([t for t in trade_history if t['pnl'] < 0])
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
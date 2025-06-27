"""
Integrated Algo Trading Bot
Combines signal generation with order execution using Alpaca API
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import logging
import json
import sys
import os
from typing import Dict, Optional, List

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from get_candles import CandleDataProvider
from signalGenerators.signalSuperTrend import SuperTrendSignalGenerator
from place_order import AlpacaOrderManager
from config import (
    DEFAULT_INSTRUMENT, SUPERTREND_CONFIG, RISK_MANAGEMENT,
    ENVIRONMENT, TRADING_SESSIONS, STRATEGY_CONFIG
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AlgoTradingBot:
    """
    Main trading bot that integrates signal generation and order execution
    """
    
    def __init__(self, symbol: str = None, paper_trading: bool = True):
        """
        Initialize the trading bot
        
        Args:
            symbol: Trading symbol (default from config)
            paper_trading: Use paper trading mode
        """
        self.symbol = symbol or DEFAULT_INSTRUMENT
        self.paper_trading = paper_trading
        
        # Initialize components
        self.candle_provider = CandleDataProvider()
        self.signal_generator = SuperTrendSignalGenerator(
            period=SUPERTREND_CONFIG['default_period'],
            multiplier=SUPERTREND_CONFIG['default_multiplier']
        )
        self.order_manager = AlpacaOrderManager()
        
        # Bot state
        self.is_running = False
        self.last_signal_time = None
        self.last_signal = 0
        self.position_info = None
        self.daily_trades = 0
        self.start_time = datetime.now()
        
        # Performance tracking
        self.trade_history = []
        self.total_pnl = 0.0
        
        logger.info(f"Algo Trading Bot initialized")
        logger.info(f"Symbol: {self.symbol}")
        logger.info(f"Paper Trading: {self.paper_trading}")
        logger.info(f"SuperTrend: Period={SUPERTREND_CONFIG['default_period']}, Multiplier={SUPERTREND_CONFIG['default_multiplier']}")
    
    def check_connection(self) -> bool:
        """Check if all components are connected and ready"""
        if not self.order_manager.is_connected:
            logger.error("Order manager not connected to Alpaca API")
            return False
        
        # Test data connection
        test_price = self.order_manager.get_current_price(self.symbol)
        if test_price is None:
            logger.error(f"Cannot get price data for {self.symbol}")
            return False
        
        logger.info(f"All connections verified. Current {self.symbol} price: ${test_price:.2f}")
        return True
    
    def get_current_position(self) -> Optional[Dict]:
        """Get current position for the trading symbol"""
        return self.order_manager.get_position(self.symbol)
    
    def should_trade(self, signal_data: Dict) -> bool:
        """
        Determine if we should execute a trade based on various conditions
        
        Args:
            signal_data: Signal data from the generator
        
        Returns:
            True if we should trade, False otherwise
        """
        # Check if markets are open (simplified)
        current_hour = datetime.now().hour
        if TRADING_SESSIONS['regular_hours_only']:
            if current_hour < 9 or current_hour >= 16:  # Simplified market hours
                logger.info("Outside regular trading hours")
                return False
        
        # Check daily trade limit
        if self.daily_trades >= RISK_MANAGEMENT['max_daily_trades']:
            logger.info(f"Daily trade limit reached: {self.daily_trades}")
            return False
        
        # Check signal timestamp to avoid duplicate trades
        current_signal_time = signal_data['current_status']['timestamp']
        if (self.last_signal_time and 
            current_signal_time <= self.last_signal_time):
            return False
        
        # Check if there's actually a new signal
        current_signal = signal_data['current_status']['signal']
        if current_signal == 0:  # No signal
            return False
        
        # Check if it's the same signal as before
        if current_signal == self.last_signal:
            return False
        
        # Check position limits
        positions = self.order_manager.get_positions()
        if positions and len(positions) >= RISK_MANAGEMENT['max_open_positions']:
            logger.info(f"Maximum open positions reached: {len(positions)}")
            return False
        
        return True
    
    def execute_trade(self, signal_data: Dict) -> Optional[Dict]:
        """
        Execute a trade based on the signal
        
        Args:
            signal_data: Signal data from the generator
        
        Returns:
            Execution result or None
        """
        current_status = signal_data['current_status']
        signal = current_status['signal']
        current_price = current_status['close_price']
        timestamp = current_status['timestamp']
        
        logger.info(f"Executing trade signal: {signal} for {self.symbol}")
        logger.info(f"Price: ${current_price:.2f} at {timestamp}")
        
        # Calculate signal strength based on trend and price relative to SuperTrend
        supertrend_value = current_status['supertrend_value']
        price_distance = abs(current_price - supertrend_value) / supertrend_value
        signal_strength = min(1.0, price_distance * 10)  # Simple strength calculation
        
        # Execute the signal
        execution_result = self.order_manager.execute_signal(
            symbol=self.symbol,
            signal=signal,
            current_price=current_price,
            signal_strength=signal_strength
        )
        
        if execution_result and execution_result['orders']:
            # Update bot state
            self.last_signal = signal
            self.last_signal_time = timestamp
            self.daily_trades += 1
            
            # Log the trade
            trade_record = {
                'timestamp': timestamp,
                'symbol': self.symbol,
                'signal': signal,
                'price': current_price,
                'signal_strength': signal_strength,
                'orders': execution_result['orders'],
                'supertrend_value': supertrend_value
            }
            self.trade_history.append(trade_record)
            
            # Save trade to file if enabled
            if ENVIRONMENT['save_trades']:
                self.save_trade_record(trade_record)
            
            logger.info(f"Trade executed successfully: {len(execution_result['orders'])} orders")
            return execution_result
        
        else:
            logger.warning("Trade execution failed or no orders placed")
            return None
    
    def save_trade_record(self, trade_record: Dict):
        """Save trade record to CSV file"""
        try:
            df = pd.DataFrame([{
                'timestamp': trade_record['timestamp'],
                'symbol': trade_record['symbol'],
                'signal': trade_record['signal'],
                'price': trade_record['price'],
                'signal_strength': trade_record['signal_strength'],
                'supertrend_value': trade_record['supertrend_value'],
                'orders_count': len(trade_record['orders'])
            }])
            
            # Append to CSV file
            df.to_csv(ENVIRONMENT['trade_log_file'], mode='a', 
                     header=not os.path.exists(ENVIRONMENT['trade_log_file']), 
                     index=False)
        except Exception as e:
            logger.error(f"Error saving trade record: {e}")
    
    def run_single_cycle(self) -> Dict:
        """Run a single trading cycle and return results"""
        try:
            # Get latest signals
            signal_data = self.signal_generator.get_latest_signal()
            if not signal_data:
                return {'status': 'error', 'message': 'Failed to get signal data'}
            
            # Get current position
            current_position = self.get_current_position()
            
            # Check if we should trade
            if self.should_trade(signal_data):
                execution_result = self.execute_trade(signal_data)
                status = 'trade_executed' if execution_result else 'trade_failed'
            else:
                execution_result = None
                status = 'no_trade'
            
            # Get account info for reporting
            account_info = self.order_manager.get_account_info()
            
            return {
                'status': status,
                'timestamp': datetime.now(),
                'signal_data': signal_data,
                'current_position': current_position,
                'execution_result': execution_result,
                'account_info': account_info,
                'daily_trades': self.daily_trades
            }
            
        except Exception as e:
            logger.error(f"Error in trading cycle: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def display_status(self, cycle_result: Dict):
        """Display current bot status"""
        print("\n" + "="*80)
        print(f"ALGO TRADING BOT STATUS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        # Account information
        if cycle_result.get('account_info'):
            account = cycle_result['account_info']
            print(f"💰 Account Value: ${account['portfolio_value']:,.2f}")
            print(f"💵 Buying Power: ${account['buying_power']:,.2f}")
            print(f"📊 Daily Trades: {self.daily_trades}/{RISK_MANAGEMENT['max_daily_trades']}")
        
        # Current position
        if cycle_result.get('current_position'):
            pos = cycle_result['current_position']
            print(f"📈 Position: {pos['qty']} shares @ ${pos['current_price']:.2f}")
            print(f"💹 P&L: ${pos['unrealized_pl']:,.2f} ({pos['unrealized_plpc']:.2%})")
        else:
            print("📈 Position: No open position")
        
        # Signal information
        if cycle_result.get('signal_data'):
            signal_data = cycle_result['signal_data']
            current = signal_data['current_status']
            
            print(f"🎯 Symbol: {self.symbol}")
            print(f"💲 Current Price: ${current['close_price']:.2f}")
            print(f"📈 SuperTrend: ${current['supertrend_value']:.2f}")
            print(f"📊 Trend: {'UP' if current['trend'] == 1 else 'DOWN'}")
            
            if current['signal'] == 1:
                print("🟢 Signal: BUY")
            elif current['signal'] == -1:
                print("🔴 Signal: SELL")
            else:
                print("⚪ Signal: HOLD")
        
        # Execution status
        status = cycle_result.get('status', 'unknown')
        status_icons = {
            'trade_executed': '✅',
            'trade_failed': '❌',
            'no_trade': '⏸️',
            'error': '⚠️'
        }
        print(f"{status_icons.get(status, '❓')} Status: {status.replace('_', ' ').title()}")
        
        # Trading session info
        runtime = datetime.now() - self.start_time
        print(f"⏱️ Runtime: {str(runtime).split('.')[0]}")
        print(f"📊 Total Trades: {len(self.trade_history)}")
        
        print("="*80)
    
    def run_bot(self, check_interval: int = 300, max_runtime_hours: int = 8):
        """
        Run the trading bot continuously
        
        Args:
            check_interval: Seconds between checks (default: 5 minutes)
            max_runtime_hours: Maximum runtime in hours
        """
        if not self.check_connection():
            logger.error("Bot startup failed - connection issues")
            return
        
        logger.info(f"Starting Algo Trading Bot")
        logger.info(f"Check interval: {check_interval} seconds")
        logger.info(f"Max runtime: {max_runtime_hours} hours")
        logger.info(f"Press Ctrl+C to stop")
        
        self.is_running = True
        max_runtime = timedelta(hours=max_runtime_hours)
        
        try:
            while self.is_running:
                # Check runtime limit
                if datetime.now() - self.start_time > max_runtime:
                    logger.info("Maximum runtime reached, stopping bot")
                    break
                
                # Run trading cycle
                cycle_result = self.run_single_cycle()
                
                # Display status
                self.display_status(cycle_result)
                
                # Handle errors
                if cycle_result['status'] == 'error':
                    logger.error(f"Cycle error: {cycle_result.get('message')}")
                
                # Wait before next cycle
                logger.info(f"Next check in {check_interval} seconds...")
                time.sleep(check_interval)
                
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.error(f"Unexpected error in bot main loop: {e}")
        finally:
            self.is_running = False
            self.shutdown()
    
    def shutdown(self):
        """Cleanup and shutdown procedures"""
        logger.info("Shutting down Algo Trading Bot...")
        
        # Cancel any pending orders (optional)
        if hasattr(self, 'cancel_all_orders_on_shutdown') and self.cancel_all_orders_on_shutdown:
            pending_orders = self.order_manager.get_orders(status='open')
            if pending_orders:
                logger.info(f"Cancelling {len(pending_orders)} pending orders")
                for order in pending_orders:
                    self.order_manager.cancel_order(order['id'])
        
        # Final status report
        final_positions = self.order_manager.get_positions()
        if final_positions:
            logger.info(f"Final positions: {len(final_positions)}")
            for pos in final_positions:
                logger.info(f"  {pos['symbol']}: {pos['qty']} shares, P&L: ${pos['unrealized_pl']:,.2f}")
        
        logger.info(f"Total trades executed: {len(self.trade_history)}")
        logger.info(f"Bot session completed")

def main():
    """Main function to run the trading bot"""
    print("🤖 Algo Trading Bot - SuperTrend Strategy")
    print("=" * 60)
    
    # Configuration summary
    print(f"📊 Trading Symbol: {DEFAULT_INSTRUMENT}")
    print(f"📈 Strategy: SuperTrend (Period: {SUPERTREND_CONFIG['default_period']}, Multiplier: {SUPERTREND_CONFIG['default_multiplier']})")
    print(f"💰 Max Position Size: ${RISK_MANAGEMENT['max_position_size']:,}")
    print(f"🛑 Stop Loss: {RISK_MANAGEMENT['stop_loss_pct']*100}%")
    print(f"🎯 Take Profit: {RISK_MANAGEMENT['take_profit_pct']*100}%")
    print(f"🔄 Max Daily Trades: {RISK_MANAGEMENT['max_daily_trades']}")
    print(f"🧪 Paper Trading: {ENVIRONMENT['mode'] == 'paper'}")
    
    # Initialize bot
    bot = AlgoTradingBot(symbol=DEFAULT_INSTRUMENT)
    
    # Check connections
    if not bot.check_connection():
        print("❌ Failed to initialize bot. Please check configuration and connections.")
        return
    
    print("✅ Bot initialized successfully!")
    
    # Menu
    while True:
        print("\n" + "="*50)
        print("Choose an option:")
        print("1. Run single check")
        print("2. Start continuous trading")
        print("3. View current positions")
        print("4. View account info")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            # Single check
            print("\n🔍 Running single check...")
            result = bot.run_single_cycle()
            bot.display_status(result)
            
        elif choice == '2':
            # Continuous trading
            interval = input("Check interval in seconds (default: 300): ").strip()
            try:
                interval = int(interval) if interval else 300
            except ValueError:
                interval = 300
            
            max_hours = input("Max runtime in hours (default: 8): ").strip()
            try:
                max_hours = int(max_hours) if max_hours else 8
            except ValueError:
                max_hours = 8
            
            bot.run_bot(check_interval=interval, max_runtime_hours=max_hours)
            
        elif choice == '3':
            # View positions
            positions = bot.order_manager.get_positions()
            if positions:
                print(f"\n📈 Current Positions ({len(positions)}):")
                for pos in positions:
                    print(f"  {pos['symbol']}: {pos['qty']} shares @ ${pos['current_price']:.2f}")
                    print(f"    Value: ${pos['market_value']:,.2f}, P&L: ${pos['unrealized_pl']:,.2f}")
            else:
                print("\n📈 No current positions")
                
        elif choice == '4':
            # View account info
            account = bot.order_manager.get_account_info()
            if account:
                print(f"\n💰 Account Information:")
                print(f"  Status: {account['status']}")
                print(f"  Portfolio Value: ${account['portfolio_value']:,.2f}")
                print(f"  Buying Power: ${account['buying_power']:,.2f}")
                print(f"  Cash: ${account['cash']:,.2f}")
                print(f"  Day Trade Count: {account['day_trade_count']}")
            else:
                print("❌ Unable to fetch account information")
                
        elif choice == '5':
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()

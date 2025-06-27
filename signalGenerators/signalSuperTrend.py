import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from get_candles import CandleDataProvider
from indicators.superTrend import supertrend, supertrend_signals
from config import DEFAULT_INSTRUMENT, SUPERTREND_CONFIG

class SuperTrendSignalGenerator:
    def __init__(self, period=None, multiplier=None):
        self.candle_provider = CandleDataProvider()
        self.period = period or SUPERTREND_CONFIG['default_period']
        self.multiplier = multiplier or SUPERTREND_CONFIG['default_multiplier']
        self.last_signal_time = None
        
    def get_5min_candles(self, period="1d"):
        """Get 5-minute candle data"""
        try:
            candles = self.candle_provider.get_candles(DEFAULT_INSTRUMENT, period=period, interval="5m")
            if candles is None or candles.empty:
                print("No candle data received")
                return None
            
            # Ensure column names are lowercase for SuperTrend function
            candles.columns = [col.lower() for col in candles.columns]
            return candles
        except Exception as e:
            print(f"Error getting 5-minute candles: {e}")
            return None
    
    def generate_signals(self, candles_df):
        """Generate SuperTrend signals from candle data"""
        if candles_df is None or candles_df.empty:
            return None
        
        try:
            # Apply SuperTrend indicator
            signals_data = supertrend_signals(candles_df, self.period, self.multiplier)
            st_df = supertrend(candles_df, self.period, self.multiplier)
            
            # Add timestamp and price info
            st_df['timestamp'] = candles_df.index
            st_df['datetime'] = pd.to_datetime(st_df['timestamp'])
            
            return {
                'dataframe': st_df,
                'buy_signals': signals_data['buy_signals'],
                'sell_signals': signals_data['sell_signals'],
                'supertrend_values': signals_data['supertrend_values'],
                'trend': signals_data['trend']
            }
        except Exception as e:
            print(f"Error generating signals: {e}")
            return None
    
    def get_latest_signal(self):
        """Get the latest signal based on current day's 5-minute candles"""
        candles = self.get_5min_candles(period="1d")
        if candles is None:
            return None
        
        signals = self.generate_signals(candles)
        if signals is None:
            return None
        
        df = signals['dataframe']
        latest_idx = len(df) - 1
        
        # Get current signal status
        current_signal = {
            'timestamp': df['datetime'].iloc[latest_idx],
            'close_price': df['close'].iloc[latest_idx],
            'supertrend_value': df['supertrend'].iloc[latest_idx],
            'trend': df['trend'].iloc[latest_idx],
            'atr': df['atr'].iloc[latest_idx],
            'signal': df['signal'].iloc[latest_idx] if latest_idx > 0 else 0
        }
        
        # Find recent signals
        recent_signals = []
        for i in range(max(0, latest_idx - 10), latest_idx + 1):
            if df['signal'].iloc[i] != 0:
                recent_signals.append({
                    'timestamp': df['datetime'].iloc[i],
                    'signal_type': 'BUY' if df['signal'].iloc[i] == 1 else 'SELL',
                    'price': df['close'].iloc[i],
                    'supertrend': df['supertrend'].iloc[i]
                })
        
        return {
            'current_status': current_signal,
            'recent_signals': recent_signals,
            'total_candles': len(df)
        }
    
    def display_signal_summary(self, signal_data):
        """Display formatted signal summary"""
        if signal_data is None:
            print("No signal data available")
            return
        
        current = signal_data['current_status']
        
        print("\n" + "="*60)
        print("SUPERTREND SIGNAL ANALYSIS")
        print("="*60)
        print(f"Timestamp: {current['timestamp']}")
        print(f"Current Price: ₹{current['close_price']:.2f}")
        print(f"SuperTrend Value: ₹{current['supertrend_value']:.2f}")
        print(f"ATR: {current['atr']:.2f}")
        
        # Determine position relative to SuperTrend
        if current['close_price'] > current['supertrend_value']:
            position = "ABOVE SuperTrend (Bullish Zone)"
        else:
            position = "BELOW SuperTrend (Bearish Zone)"
        
        print(f"Position: {position}")
        print(f"Current Trend: {'UPTREND' if current['trend'] == 1 else 'DOWNTREND'}")
        
        # Latest signal
        if current['signal'] == 1:
            print("🟢 LATEST SIGNAL: BUY")
        elif current['signal'] == -1:
            print("🔴 LATEST SIGNAL: SELL")
        else:
            print("⚪ LATEST SIGNAL: HOLD")
        
        print(f"\nTotal Candles Analyzed: {signal_data['total_candles']}")
        
        # Recent signals
        if signal_data['recent_signals']:
            print("\nRECENT SIGNALS:")
            print("-" * 50)
            for signal in signal_data['recent_signals'][-5:]:  # Last 5 signals
                signal_emoji = "🟢" if signal['signal_type'] == 'BUY' else "🔴"
                print(f"{signal_emoji} {signal['timestamp'].strftime('%H:%M')} | "
                      f"{signal['signal_type']} at ₹{signal['price']:.2f} "
                      f"(ST: ₹{signal['supertrend']:.2f})")
        else:
            print("\nNo recent signals found")
        
        print("="*60)
    
    def monitor_signals(self, check_interval=300):  # Check every 5 minutes
        """Monitor signals in real-time"""
        print(f"Starting SuperTrend signal monitoring...")
        print(f"Period: {self.period}, Multiplier: {self.multiplier}")
        print(f"Check interval: {check_interval} seconds")
        print("Press Ctrl+C to stop monitoring\n")
        
        try:
            while True:
                print(f"\n📊 Checking signals at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                signal_data = self.get_latest_signal()
                if signal_data:
                    self.display_signal_summary(signal_data)
                    
                    # Check for new signals
                    current_signal = signal_data['current_status']['signal']
                    current_time = signal_data['current_status']['timestamp']
                    
                    if (current_signal != 0 and 
                        (self.last_signal_time is None or current_time > self.last_signal_time)):
                        
                        signal_type = "BUY" if current_signal == 1 else "SELL"
                        price = signal_data['current_status']['close_price']
                        
                        print(f"\n🚨 NEW SIGNAL ALERT! 🚨")
                        print(f"Signal: {signal_type}")
                        print(f"Price: ₹{price:.2f}")
                        print(f"Time: {current_time}")
                        
                        self.last_signal_time = current_time
                
                else:
                    print("❌ Unable to fetch signal data")
                
                print(f"\n⏰ Next check in {check_interval} seconds...")
                time.sleep(check_interval)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Signal monitoring stopped by user")
        except Exception as e:
            print(f"\n❌ Error in signal monitoring: {e}")

def main():
    """Main function to demonstrate signal generation"""
    # Initialize signal generator with custom parameters
    signal_gen = SuperTrendSignalGenerator(period=10, multiplier=3.0)
    
    print("SuperTrend Signal Generator")
    print(f"Parameters: Period={signal_gen.period}, Multiplier={signal_gen.multiplier}")
    
    # Get and display current signals
    print("\n📈 Fetching current day's 5-minute signals...")
    signal_data = signal_gen.get_latest_signal()
    
    if signal_data:
        signal_gen.display_signal_summary(signal_data)
        
        # Ask user if they want to start monitoring
        response = input("\nStart real-time signal monitoring? (y/n): ").lower().strip()
        if response == 'y':
            signal_gen.monitor_signals(check_interval=300)  # Check every 5 minutes
    else:
        print("❌ Unable to generate signals. Please check data connection.")

if __name__ == "__main__":
    main()

import yfinance as yf
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
from typing import Optional
import warnings
warnings.filterwarnings('ignore')

class CandleDataProvider:
    def __init__(self):
        self.nifty_symbol = "^NSEI"  # Nifty 50 index symbol for yfinance
        
    def get_nifty_current_price(self) -> float:
        """Get current Nifty 50 price"""
        try:
            nifty = yf.Ticker(self.nifty_symbol)
            data = nifty.history(period="1d", interval="1m")
            if not data.empty:
                return data['Close'].iloc[-1]
            return None
        except Exception as e:
            print(f"Error getting Nifty price: {e}")
            return None
    

    
    def get_candles(self, symbol: str = None, period: str = "1d", interval: str = "1m") -> Optional[pd.DataFrame]:
        """
        Get candlestick data for a specific symbol or Nifty 50 by default
        """
        if symbol is None:
            symbol = self.nifty_symbol
            
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            if not data.empty:
                return data
            return None
        except Exception as e:
            print(f"Error getting data for {symbol}: {e}")
            return None
    def get_nifty_candles(self, period: str = "1d", interval: str = "1m") -> pd.DataFrame:
        """
        Get Nifty 50 candlestick data
        """
        return self.get_candles(self.nifty_symbol, period, interval)

def main():
    """
    Main function to demonstrate the usage
    """
    candle_provider = CandleDataProvider()
    
    print("Getting current Nifty 50 price...")
    current_price = candle_provider.get_nifty_current_price()
    print(f"Current Nifty 50 price: {current_price}")
    
    print("\nGetting Nifty 50 candlestick data...")
    candles = candle_provider.get_nifty_candles(period="1d", interval="5m")
    if candles is not None and not candles.empty:
        print("Latest Nifty candles:")
        print(candles.tail())
    
    print("\nGetting custom symbol data...")
    # Example: Get data for another symbol
    custom_data = candle_provider.get_candles("RELIANCE.NS", period="1d", interval="5m")
    if custom_data is not None and not custom_data.empty:
        print("Latest Reliance candles:")
        print(custom_data.tail())

if __name__ == "__main__":
    main()
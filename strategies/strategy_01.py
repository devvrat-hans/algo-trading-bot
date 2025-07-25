'''
This module implements a trading strategy based on the 9-15 EMA crossover.
It generates buy and sell signals based on the crossover of two Exponential Moving Averages (EMAs):
- 9-period EMA (fast)
- 15-period EMA (slow)
It includes additional filters for price action, volume, and momentum to confirm signals.
- Price action: Current price relative to EMAs
- Volume: Current volume vs. average volume
- Momentum: Current close vs. previous close
        
'''

def calculate_ema(data, period):
    """
    Calculate Exponential Moving Average for given period.
    
    Args:
        data (pd.Series): Price data (typically Close prices)
        period (int): EMA period
        
    Returns:
        pd.Series: EMA values
    """
    return data.ewm(span=period, adjust=False).mean()

def generate_signal(req_market_data):
    """
    Analyzes market data using 9-15 EMA crossover strategy and generates trading signals.
    
    Strategy Details:
    - Uses 9-period EMA (fast) and 15-period EMA (slow)
    - BUY signal: When 9-EMA crosses above 15-EMA (bullish crossover)
    - SELL signal: When 9-EMA crosses below 15-EMA (bearish crossover)
    - Additional filters: Price above both EMAs for buy, below both for sell
    - Volume confirmation: Current volume > average volume of last 10 periods
    - Momentum filter: Current close > previous close for buy signals

    Args:
        req_market_data (pd.DataFrame): DataFrame containing OHLCV data with columns for
                                       Timestamp, Open, High, Low, Close, Volume, and Open Interest.

    Returns:
        str: Trading signal, one of:
             - 'buy': Strong bullish signal with EMA crossover and confirmations
             - 'sell': Strong bearish signal with EMA crossover and confirmations  
             - 'hold': No clear signal or insufficient data
    """
    
    if req_market_data is None or req_market_data.empty:
        return 'hold'
    
    # Need at least 20 candles for reliable EMA calculation
    if len(req_market_data) < 20:
        return 'hold'
    
    # Calculate EMAs
    req_market_data['EMA_9'] = calculate_ema(req_market_data['Close'], 9)
    req_market_data['EMA_15'] = calculate_ema(req_market_data['Close'], 15)
    
    # Calculate average volume for volume filter
    req_market_data['Avg_Volume_10'] = req_market_data['Volume'].rolling(window=10).mean()
    
    # Get last few candles for analysis
    current_candle = req_market_data.iloc[-1]
    previous_candle = req_market_data.iloc[-2]
    
    # Extract values for current and previous candles
    current_close = current_candle['Close']
    current_ema_9 = current_candle['EMA_9']
    current_ema_15 = current_candle['EMA_15']
    current_volume = current_candle['Volume']
    current_avg_volume = current_candle['Avg_Volume_10']
    
    previous_ema_9 = previous_candle['EMA_9']
    previous_ema_15 = previous_candle['EMA_15']
    previous_close = previous_candle['Close']
    
    # Check for bullish crossover (9-EMA crosses above 15-EMA)
    bullish_crossover = (previous_ema_9 <= previous_ema_15) and (current_ema_9 > current_ema_15)
    
    # Check for bearish crossover (9-EMA crosses below 15-EMA)
    bearish_crossover = (previous_ema_9 >= previous_ema_15) and (current_ema_9 < current_ema_15)
    
    # Additional confirmation filters
    price_above_emas = current_close > current_ema_9 and current_close > current_ema_15
    price_below_emas = current_close < current_ema_9 and current_close < current_ema_15
    
    # Volume confirmation (current volume should be above average)
    volume_confirmation = current_volume > current_avg_volume
    
    # Momentum confirmation
    bullish_momentum = current_close > previous_close
    bearish_momentum = current_close < previous_close
    
    # EMA trend confirmation (9-EMA should be trending in signal direction)
    ema_9_rising = current_ema_9 > req_market_data.iloc[-3]['EMA_9']
    ema_9_falling = current_ema_9 < req_market_data.iloc[-3]['EMA_9']
    
    # Generate BUY signal
    if (bullish_crossover and 
        price_above_emas and 
        volume_confirmation and 
        bullish_momentum and 
        ema_9_rising):
        return 'buy'
    
    # Generate SELL signal  
    elif (bearish_crossover and 
          price_below_emas and 
          volume_confirmation and 
          bearish_momentum and 
          ema_9_falling):
        return 'sell'
    
    # Additional buy condition: Strong uptrend continuation
    elif (current_ema_9 > current_ema_15 and 
          previous_ema_9 > previous_ema_15 and
          price_above_emas and
          bullish_momentum and
          volume_confirmation and
          (current_ema_9 - current_ema_15) > (previous_ema_9 - previous_ema_15)):
        return 'buy'
    
    # Additional sell condition: Strong downtrend continuation  
    elif (current_ema_9 < current_ema_15 and 
          previous_ema_9 < previous_ema_15 and
          price_below_emas and
          bearish_momentum and
          volume_confirmation and
          (current_ema_15 - current_ema_9) > (previous_ema_15 - previous_ema_9)):
        return 'sell'
    
    else:
        return 'hold'


import pandas as pd
import numpy as np

def supertrend(df, period=10, multiplier=3.0):
    """
    Calculate SuperTrend indicator
    
    Parameters:
    df (pd.DataFrame): DataFrame with 'high', 'low', 'close' columns
    period (int): Period for ATR calculation (default: 10)
    multiplier (float): Multiplier for ATR (default: 3.0)
    
    Returns:
    pd.DataFrame: DataFrame with SuperTrend values and signals
    """
    df = df.copy()
    
    # Calculate True Range
    df['prev_close'] = df['close'].shift(1)
    df['tr1'] = df['high'] - df['low']
    df['tr2'] = abs(df['high'] - df['prev_close'])
    df['tr3'] = abs(df['low'] - df['prev_close'])
    df['true_range'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)
    
    # Calculate Average True Range (ATR)
    df['atr'] = df['true_range'].rolling(window=period).mean()
    
    # Calculate basic upper and lower bands
    df['hl_avg'] = (df['high'] + df['low']) / 2
    df['upper_band'] = df['hl_avg'] + (multiplier * df['atr'])
    df['lower_band'] = df['hl_avg'] - (multiplier * df['atr'])
    
    # Initialize SuperTrend columns
    df['supertrend_upper'] = df['upper_band']
    df['supertrend_lower'] = df['lower_band']
    df['supertrend'] = 0.0
    df['trend'] = 1  # 1 for uptrend, -1 for downtrend
    
    # Calculate SuperTrend values
    for i in range(1, len(df)):
        # Upper band logic
        if df['upper_band'].iloc[i] < df['supertrend_upper'].iloc[i-1] or df['close'].iloc[i-1] > df['supertrend_upper'].iloc[i-1]:
            df.loc[df.index[i], 'supertrend_upper'] = df['upper_band'].iloc[i]
        else:
            df.loc[df.index[i], 'supertrend_upper'] = df['supertrend_upper'].iloc[i-1]
        
        # Lower band logic
        if df['lower_band'].iloc[i] > df['supertrend_lower'].iloc[i-1] or df['close'].iloc[i-1] < df['supertrend_lower'].iloc[i-1]:
            df.loc[df.index[i], 'supertrend_lower'] = df['lower_band'].iloc[i]
        else:
            df.loc[df.index[i], 'supertrend_lower'] = df['supertrend_lower'].iloc[i-1]
        
        # Trend determination
        if df['close'].iloc[i] <= df['supertrend_lower'].iloc[i]:
            df.loc[df.index[i], 'trend'] = -1
        elif df['close'].iloc[i] >= df['supertrend_upper'].iloc[i]:
            df.loc[df.index[i], 'trend'] = 1
        else:
            df.loc[df.index[i], 'trend'] = df['trend'].iloc[i-1]
        
        # SuperTrend value
        if df['trend'].iloc[i] == 1:
            df.loc[df.index[i], 'supertrend'] = df['supertrend_lower'].iloc[i]
        else:
            df.loc[df.index[i], 'supertrend'] = df['supertrend_upper'].iloc[i]
    
    # Generate signals
    df['signal'] = 0
    df['signal'] = np.where((df['trend'] == 1) & (df['trend'].shift(1) == -1), 1, df['signal'])  # Buy signal
    df['signal'] = np.where((df['trend'] == -1) & (df['trend'].shift(1) == 1), -1, df['signal'])  # Sell signal
    
    # Clean up intermediate columns
    columns_to_keep = ['close', 'supertrend', 'trend', 'signal', 'atr', 'supertrend_upper', 'supertrend_lower']
    if 'high' in df.columns and 'low' in df.columns:
        columns_to_keep.extend(['high', 'low'])
    
    return df[columns_to_keep]

def supertrend_signals(df, period=10, multiplier=3.0):
    """
    Generate buy/sell signals based on SuperTrend indicator
    
    Returns:
    dict: Dictionary with 'buy_signals' and 'sell_signals' as boolean arrays
    """
    st_df = supertrend(df, period, multiplier)
    
    return {
        'buy_signals': st_df['signal'] == 1,
        'sell_signals': st_df['signal'] == -1,
        'supertrend_values': st_df['supertrend'],
        'trend': st_df['trend']
    }

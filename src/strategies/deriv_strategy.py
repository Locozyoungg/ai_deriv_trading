"""
Volatility index trading strategy for Deriv platform

File Location: src/strategies/deriv_strategy.py
"""

import numpy as np
import pandas as pd

class VolatilityIndexStrategy:
    """Implements mean-reversion strategy for volatility indices"""
    
    def __init__(self, lookback_period: int = 14):
        """
        Initialize strategy parameters
        
        Args:
            lookback_period: Window for volatility calculation (default: 14)
        """
        self.lookback = lookback_period
        self.entry_threshold = 2.0  # Standard deviations
        self.exit_threshold = 0.5

    def generate_signal(self, ohlc_data: pd.DataFrame) -> Optional[Dict]:
        """
        Analyze market data to generate trade signals
        
        Args:
            ohlc_data: DataFrame with Open/High/Low/Close/Volume
            
        Returns:
            dict: Trade signal details or None
        """
        # Calculate volatility using ATR
        atr = self._calculate_atr(ohlc_data)
        
        # Compute Bollinger Bands
        mean = ohlc_data['close'].rolling(self.lookback).mean()
        std = ohlc_data['close'].rolling(self.lookback).std()
        
        current_price = ohlc_data['close'].iloc[-1]
        
        # Generate long signal
        if current_price < (mean.iloc[-1] - self.entry_threshold * std.iloc[-1]):
            return {
                'direction': 'CALL',
                'entry': current_price,
                'stake': self._calculate_position_size(atr),
                'duration': 300  # 5 minutes
            }
            
        # Generate short signal
        elif current_price > (mean.iloc[-1] + self.entry_threshold * std.iloc[-1]):
            return {
                'direction': 'PUT',
                'entry': current_price,
                'stake': self._calculate_position_size(atr),
                'duration': 300
            }
            
        return None
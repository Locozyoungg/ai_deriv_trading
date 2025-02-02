"""
Market data processing and feature engineering

File Location: src/utils/data_processor.py
"""

import pandas as pd

class DerivDataProcessor:
    """Handles data normalization and technical indicator calculation"""
    
    def __init__(self, window_size: int = 20):
        """
        Initialize processing parameters
        
        Args:
            window_size: Rolling window for indicators (default: 20)
        """
        self.window = window_size
        self.scaler = None  # Placeholder for normalization model

    def preprocess_data(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and normalize raw market data
        
        Args:
            raw_data: DataFrame with raw market data
            
        Returns:
            pd.DataFrame: Processed data with features
        """
        # Handle missing values
        data = raw_data.dropna().copy()
        
        # Add technical indicators
        data['rsi'] = self._calculate_rsi(data)
        data['atr'] = self._calculate_atr(data)
        data['volume_ma'] = data['volume'].rolling(self.window).mean()
        
        # Normalize price data
        data[['open', 'high', 'low', 'close']] = self._normalize_prices(data)
        
        return data

    def _calculate_rsi(self, data: pd.DataFrame) -> pd.Series:
        """Relative Strength Index calculation"""
        delta = data['close'].diff()
        gain = delta.where(delta > 0, 0.0)
        loss = -delta.where(delta < 0, 0.0)
        # ... RSI calculation logic ...
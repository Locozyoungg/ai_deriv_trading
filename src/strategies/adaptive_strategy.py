"""
Self-improving trading strategy combining RL and technical analysis

File Location: src/strategies/adaptive_strategy.py
"""

import numpy as np
import pandas as pd
from typing import Optional, Dict

class AdaptiveTradingStrategy:
    def __init__(self, learner):
        """
        Initialize adaptive strategy components
        
        Args:
            learner: Reference to OnlineLearner instance
        """
        self.learner = learner
        self.state_buffer = deque(maxlen=10)  # State history
        
        # Technical analysis parameters
        self.base_strategy_config = {
            'rsi_window': 14,
            'atr_window': 20,
            'bb_window': 20
        }

    def generate_signal(self, processed_data: pd.DataFrame) -> Optional[Dict]:
        """
        Generate trade signal using combined RL and rule-based approach
        
        Args:
            processed_data: DataFrame with features
            
        Returns:
            dict: Trade signal with metadata
        """
        # Get current market state
        state = self._create_state_vector(processed_data)
        
        # Exploration vs exploitation
        if np.random.rand() < self.learner.epsilon:
            action = np.random.choice([0, 1, 2])  # Random action
        else:
            action = self.learner.model.predict([state])[0]
            
        # Convert action to trade signal
        return self._action_to_signal(action, processed_data)

    def _create_state_vector(self, data: pd.DataFrame) -> np.ndarray:
        """Create normalized state vector for RL model"""
        latest = data.iloc[-1]
        return np.array([
            latest['rsi'] / 100,          # Normalized RSI 
            latest['atr'] / data['close'].mean(),  # Relative volatility
            latest['volume_ma'] / 1e6,    # Volume in millions
            data['close'].pct_change(5).iloc[-1],  # 5-period return
            self._market_trend(data)      # Trend strength
        ])

    def _action_to_signal(self, action: int, data: pd.DataFrame) -> Dict:
        """Map RL action to executable trade signal"""
        # Base strategy parameters from current market regime
        if action == 1:  # Buy
            return {
                'direction': 'CALL',
                'confidence': self.learner.model.predict_proba(
                    [self._create_state_vector(data)]
                )[0][1],
                **self._calculate_size_params(data)
            }
        # Similar for other actions...
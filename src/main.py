"""
Main trading loop with learning integration

File Location: src/main.py
"""
import asyncio
from typing import Dict, Any


class TradingSession:
    def __init__(self, config: Dict):
        # Initialize components
        self.learner = TradingModelUpdater()
        self.strategy = AdaptiveTradingStrategy(self.learner)
        # ... other components ...

    async def _execute_trade_cycle(self):
        """Single iteration of trading loop"""
        data = await self.get_market_data()
        processed_data = self.processor.preprocess(data)
        
        signal = self.strategy.generate_signal(processed_data)
        
        if signal and self.risk_manager.validate(signal):
            # Execute trade and get outcome
            trade_result = await self.client.execute_order(signal)
            
            # Calculate reward (profit normalized by risk)
            reward = self._calculate_reward(trade_result)
            
            # Get next state for learning
            next_data = await self.get_market_data()
            next_state = self.strategy.create_state_vector(next_data)
            
            # Update learning model
            self.learner.update_model(
                state=current_state,
                action=signal['action_code'],
                reward=reward,
                next_state=next_state,
                done=False
            )
            
            # Decay exploration rate
            self.learner.epsilon = max(
                self.learner.epsilon_min,
                self.learner.epsilon * self.learner.epsilon_decay
            )
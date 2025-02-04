"""
Main trading loop with learning integration

File Location: src/main.py
Responsibilities:
1. Orchestrate core trading components
2. Manage real-time execution loop
3. Handle learning updates
4. Enforce risk controls
"""

import asyncio
from typing import Dict, Any
import logging
from src.brokers.deriv_client import DerivTradingClient
from src.risk_management.deriv_risk import DerivRiskManager
from src.utils.data_processor import DerivDataProcessor
from src.learning.online_learner import TradingModelUpdater
from src.strategies.adaptive_strategy import AdaptiveTradingStrategy

class TradingSession:
    def __init__(self, config: Dict):
        """
        Initialize trading components
        
        Args:
            config: Dictionary of parameters from config/params.yaml
        """
        # Initialize core components with config
        self.config = config
        self.learner = TradingModelUpdater(
            memory_size=config['learning']['replay_buffer'],
            batch_size=config['learning']['batch_size']
        )
        self.strategy = AdaptiveTradingStrategy(
            self.learner,
            base_confidence=config['strategy']['base_confidence']
        )
        self.risk_manager = DerivRiskManager(
            initial_balance=config['account']['initial_balance'],
            max_daily_loss=config['risk']['max_daily_loss']
        )
        self.client = DerivTradingClient(
            app_id=config['deriv']['app_id'],
            token=config['deriv']['token']
        )
        self.data_processor = DerivDataProcessor(
            window_size=config['processing']['window_size']
        )
        
        # Initialize state management
        self.balance = config['account']['initial_balance']
        self.open_positions = []
        self.trade_history = []
        self.current_state = None

    async def run(self):
        """Main trading execution loop"""
        try:
            await self.client.connect()
            logging.info("Connected to Deriv API")
            
            # Warmup data for initial state
            await self._warmup_data()
            
            while True:
                await self._execute_trade_cycle()
                await asyncio.sleep(self.config['execution']['interval'])
                
        except Exception as e:
            logging.error(f"Critical error: {str(e)}")
            await self.shutdown()
        finally:
            await self.client.close()

    async def _warmup_data(self):
        """Collect initial data for strategy warmup"""
        data = await self.client.get_ohlc(
            symbol=self.config['symbols'][0],
            timeframe=self.config['strategy']['timeframe'],
            count=self.config['processing']['data_window']
        )
        self.current_state = self.data_processor.preprocess(data)

    async def _execute_trade_cycle(self):
        """Single iteration of trading loop"""
        try:
            # Data Acquisition and Processing
            data = await self._get_market_data()
            processed_data = self.data_processor.preprocess(data)
            
            # Generate trading signal
            signal = self.strategy.generate_signal(processed_data)
            
            if signal and self.risk_manager.validate_trade(signal['symbol'], signal['amount']):
                # Execute trade
                trade_result = await self.client.execute_order(
                    symbol=signal['symbol'],
                    direction=signal['direction'],
                    amount=signal['amount'],
                    duration=signal['duration']
                )
                
                if trade_result['success']:
                    # Update portfolio state
                    self._update_portfolio_state(trade_result)
                    
                    # Calculate learning components
                    reward = self._calculate_reward(trade_result)
                    next_data = await self._get_market_data()
                    next_state = self.data_processor.preprocess(next_data)
                    
                    # Update learning model
                    self.learner.update_model(
                        state=self.current_state,
                        action=signal['action_code'],
                        reward=reward,
                        next_state=next_state,
                        done=False
                    )
                    
                    # Update current state
                    self.current_state = next_state
                    
                    # Decay exploration rate
                    self.learner.epsilon = max(
                        self.learner.epsilon_min,
                        self.learner.epsilon * self.config['learning']['epsilon_decay']
                    )
        
        except Exception as e:
            logging.error(f"Trade cycle error: {str(e)}")

    async def _get_market_data(self) -> Dict:
        """Fetch latest market data"""
        return await self.client.get_ohlc(
            symbol=self.config['symbols'][0],
            timeframe=self.config['strategy']['timeframe'],
            count=self.config['processing']['data_window']
        )

    def _calculate_reward(self, trade_result: Dict) -> float:
        """Calculate risk-adjusted reward for learning"""
        profit = trade_result['profit']
        risk = trade_result['risk']
        duration = trade_result['duration']
        
        # Normalize reward between -1 and 1
        risk_adjusted = (profit / risk) if risk != 0 else 0
        time_adjusted = risk_adjusted / (duration / 60)  # Per minute
        return max(min(time_adjusted, 1), -1)

    def _update_portfolio_state(self, trade_result: Dict):
        """Update portfolio tracking"""
        self.balance += trade_result['profit']
        self.open_positions = [
            pos for pos in self.open_positions 
            if pos['contract_id'] != trade_result['contract_id']
        ]
        self.trade_history.append(trade_result)

    async def shutdown(self):
        """Graceful shutdown procedure"""
        logging.info("Initiating shutdown...")
        # Close all open positions
        for position in self.open_positions:
            await self.client.close_position(position['contract_id'])
        
        # Save learning state
        self.learner.save_model(self.config['learning']['model_path'])
        
        # Generate final report
        logging.info(f"Final balance: {self.balance}")
        logging.info(f"Total trades: {len(self.trade_history)}")
        logging.info("Shutdown complete")
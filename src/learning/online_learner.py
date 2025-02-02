"""
Reinforcement Learning-based strategy optimizer
Implements Q-learning with experience replay for continuous improvement

File Location: src/learning/online_learner.py
"""

import numpy as np
from collections import deque
from river import drift
from sklearn.linear_model import SGDClassifier

class TradingModelUpdater:
    def __init__(self, state_size: int = 10, memory_size: int = 10000):
        """
        Initialize learning components
        
        Args:
            state_size: Number of features in state representation
            memory_size: Experience replay buffer size
        """
        # Concept drift detector
        self.drift_detector = drift.ADWIN(delta=0.002)
        
        # Online learning model (Partial Fit)
        self.model = SGDClassifier(loss='log_loss', warm_start=True)
        
        # Experience replay memory
        self.memory = deque(maxlen=memory_size)
        
        # Q-learning parameters
        self.gamma = 0.95  # Discount factor
        self.epsilon = 1.0  # Exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995

    def update_model(self, state: np.ndarray, action: int, 
                   reward: float, next_state: np.ndarray, done: bool):
        """
        Update model with new experience using Q-learning update rule
        
        Args:
            state: Current market state
            action: Taken action (0=hold, 1=buy, 2=sell)
            reward: Resulting reward from action
            next_state: Subsequent market state
            done: End of episode flag
        """
        # Store experience in memory
        self.memory.append((state, action, reward, next_state, done))
        
        # Detect concept drift in rewards
        self.drift_detector.update(reward)
        
        # Retrain model if drift detected
        if self.drift_detector.drift_detected:
            self._retrain_on_current_regime()
            self.epsilon = max(self.epsilon_min, self.epsilon * 0.9)

        # Mini-batch training
        if len(self.memory) > 100:
            self._experience_replay(batch_size=32)

    def _experience_replay(self, batch_size: int):
        """Q-learning update using experience replay"""
        batch = np.random.choice(len(self.memory), batch_size, replace=False)
        for index in batch:
            state, action, reward, next_state, done = self.memory[index]
            
            # Predict Q-values for current state
            q_values = self.model.predict_proba([state])[0]
            
            if done:
                q_update = reward
            else:
                # Predict future Q-values
                next_q = np.max(self.model.predict_proba([next_state])[0])
                q_update = reward + self.gamma * next_q
                
            # Update Q-value for taken action
            q_values[action] = q_update
            
            # Partial fit model
            self.model.partial_fit([state], [np.argmax(q_values)], 
                                 classes=[0, 1, 2])

    def _retrain_on_current_regime(self):
        """Full retraining using current market regime data"""
        states = [exp[0] for exp in self.memory]
        actions = [exp[1] for exp in self.memory]
        self.model.fit(states, actions)
"""
Learning performance monitoring dashboard

File Location: src/utils/monitor.py
"""

class LearningMonitor:
    def __init__(self, learner):
        """Initialize monitoring components"""
        self.learner = learner
        self.performance_history = []
        
    def generate_report(self):
        """Create learning performance summary"""
        return {
            'exploration_rate': self.learner.epsilon,
            'memory_utilization': len(self.learner.memory)/self.learner.memory.maxlen,
            'drift_detected': self.learner.drift_detector.drift_detected,
            'model_accuracy': self._calculate_accuracy(),
            'recent_rewards': self.performance_history[-100:]
        }
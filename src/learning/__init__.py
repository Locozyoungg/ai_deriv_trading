"""
Self-improvement system architecture:

1. Data Collection: Trade outcomes and market states
2. Experience Storage: Circular buffer (experience replay)
3. Continuous Learning: Online model updates
4. Concept Adaptation: Drift detection and regime retraining
5. Strategy Evolution: Exploration-exploitation balance

File Location: src/learning/
"""

# Learning Flow Diagram
"""
                ┌──────────────┐
                │ Trade Execution │
                └───────┬──────┘
                        ↓
                ┌──────────────┐
                │ Reward Calculation │
                └───────┬──────┘
                        ↓
                ┌──────────────┐
                │ Experience Storage │
                └───────┬──────┘
                        ↓
        ┌───────────────┴───────────────┐
        │                               │
┌───────▼──────┐             ┌──────────▼─────────┐
│ Online Update │             │ Regime Retraining │
│ (Mini-batch)  │             │ (Full Dataset)    │
└───────┬──────┘             └──────────┬─────────┘
        │                               │
        └───────────────┬───────────────┘
                        ↓
                ┌──────────────┐
                │ Model Update │
                └───────┬──────┘
                        ↓
                ┌──────────────┐
                │ Strategy Adaptation│
                └───────────────────┘
"""
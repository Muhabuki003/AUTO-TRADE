"""
Strategy Agent — decides when to enter and exit trades.
Considers memory agent's past lessons before generating signals.
"""
import random
import logging
from typing import Optional

logger = logging.getLogger("autotrade.strategy")

class StrategyAgent:
    """Generates trade signals based on market analysis + past lessons."""

    def __init__(self, config: dict = None):
        self.config = config or {}
        logger.info("Strategy Agent initialized")

    def analyze_market(self) -> dict:
        """
        Analyze current market conditions.
        Returns market state for other agents to consume.
        """
        # TODO: Real market data integration
        return {
            "trend": "neutral",
            "volatility": "medium",
            "market_condition": "range_bound",
            "timestamp": None,
        }

    def generate_signal(self, past_mistakes: list = None) -> Optional[dict]:
        """
        Generate a trade signal.
        Past mistakes from the memory agent are considered to
        avoid repeating errors.
        """
        market = self.analyze_market()

        # Check if any past lessons tell us NOT to trade
        if past_mistakes:
            active_warnings = [
                m for m in past_mistakes
                if m.get("market_condition") == market.get("market_condition")
            ]
            if len(active_warnings) >= 3:
                logger.warning("3+ similar past mistakes — skipping trade")
                return None

        # TODO: Real signal generation with technical indicators
        signal = {
            "direction": "long",
            "entry_price": None,
            "stop_loss": None,
            "take_profit": None,
            "signal_type": "trend_following",
            "market_condition": market.get("market_condition"),
            "confidence": 0.0,
            "timestamp": None,
        }
        return signal

    def validate_signal(self, signal: dict) -> bool:
        """Validate that a signal meets minimum quality threshold."""
        return signal.get("confidence", 0) >= 0.6

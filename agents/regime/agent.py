"""
Regime Agent — knows when NOT to trade.
Measures ATR (volatility) and ADX (trend strength).
"""
import logging
from typing import Optional

logger = logging.getLogger("autotrade.regime")

class RegimeAgent:
    """Detects market regime and decides if conditions are tradeable."""

    def __init__(self, config: dict = None):
        self.config = config or {}
        self.min_adx = self.config.get("min_adx", 20)  # Minimum trend strength
        self.max_atr_percent = self.config.get("max_atr_percent", 0.05)  # Max 5% ATR
        logger.info(f"Regime Agent initialized — min ADX: {self.min_adx}, max ATR: {self.max_atr_percent*100:.0f}%")

    def analyze(self) -> dict:
        """
        Analyze current market regime.
        Returns regime data for other agents.
        """
        # TODO: Real market data integration
        return {
            "adx": 22.0,
            "atr": 0.45,
            "trend": "weak_uptrend",
            "volatility": "moderate",
            "tradeable": True,
            "reason": "ADX above 20, manageable volatility",
        }

    def is_tradeable(self) -> bool:
        """Quick check — is now a good time to trade?"""
        regime = self.analyze()
        return regime.get("tradeable", False)

    def get_regime_summary(self) -> dict:
        """Return regime summary for the dashboard."""
        return self.analyze()

"""
Risk Agent — the safety net.
Manages position sizing, drawdown limits, and the kill switch.
"""
import logging
from typing import Optional

logger = logging.getLogger("autotrade.risk")

class RiskAgent:
    """Enforces risk management rules on every trade."""

    def __init__(self, config: dict = None):
        self.config = config or {}
        self.max_risk_per_trade = self.config.get("max_risk_per_trade", 0.02)  # 2%
        self.max_daily_drawdown = self.config.get("max_daily_drawdown", 0.05)  # 5%
        self.max_position_size = self.config.get("max_position_size", 0.5)  # 50% of capital
        logger.info(
            f"Risk Agent initialized — {self.max_risk_per_trade*100:.0f}% risk/trade, "
            f"{self.max_daily_drawdown*100:.0f}% daily drawdown limit"
        )

    def approve_trade(self, signal: dict, state: dict) -> bool:
        """
        Check if a trade meets all risk criteria.
        Returns True if trade is approved.
        """
        # Check kill switch
        if state.get("kill_switch"):
            logger.warning("Kill switch active — trade rejected")
            return False

        # Check daily drawdown limit
        if state.get("current_drawdown", 0) >= state.get("capital", 0) * self.max_daily_drawdown:
            logger.warning("Daily drawdown limit hit — trade rejected")
            self._trigger_kill_switch(state, "Daily drawdown limit exceeded")
            return False

        # Calculate position size
        risk_amount = state.get("capital", 0) * self.max_risk_per_trade
        max_position = state.get("capital", 0) * self.max_position_size

        logger.info(
            f"Risk check passed: risk=${risk_amount:.2f}, "
            f"max_pos=${max_position:.2f}"
        )
        return True

    def calculate_position_size(self, capital: float, entry: float, stop: float) -> float:
        """Calculate position size based on fixed risk per trade."""
        risk_per_unit = abs(entry - stop)
        if risk_per_unit == 0:
            return 0
        risk_amount = capital * self.max_risk_per_trade
        position_size = risk_amount / risk_per_unit
        return min(position_size, capital * self.max_position_size / entry)

    def _trigger_kill_switch(self, state: dict, reason: str) -> None:
        """Activate the kill switch — stops all trading."""
        state["kill_switch"] = True
        logger.critical(f"🔴 KILL SWITCH ACTIVATED: {reason}")

"""
Monitor Agent — tracks performance vs expectations.
Detects decay, compares live vs backtest, and knows when to shut down.
"""
import logging
from typing import Optional
from datetime import datetime

logger = logging.getLogger("autotrade.monitor")

class MonitorAgent:
    """Tracks live performance, compares to backtests, detects decay."""

    def __init__(self, config: dict = None):
        self.config = config or {}
        self.max_drawdown_multiple = self.config.get("max_drawdown_multiple", 1.5)
        self.trade_log = []
        logger.info("Monitor Agent initialized")

    def log_trade(self, trade: dict) -> None:
        """Log a completed trade for analysis."""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "trade": trade,
        }
        self.trade_log.append(entry)
        self._check_decay()

    def _check_decay(self) -> bool:
        """
        Compare recent performance vs historical expectations.
        Triggers warning if performance degrades beyond threshold.
        """
        if len(self.trade_log) < 10:
            return False

        recent = self.trade_log[-10:]
        win_rate = sum(1 for t in recent if t["trade"].get("pnl", 0) > 0) / len(recent)
        expected = self.config.get("expected_win_rate", 0.55)

        if win_rate < expected * 0.7:  # 30% below expected
            logger.warning(
                f"⚠️ Performance decay detected: {win_rate*100:.0f}% win rate "
                f"(expected {expected*100:.0f}%)"
            )
            return True
        return False

    def check_shutdown(self, worst_drawdown: float, current_drawdown: float) -> bool:
        """
        Check if current drawdown exceeds 1.5x worst historical drawdown.
        Returns True if bot should shut down.
        """
        if worst_drawdown > 0 and current_drawdown > worst_drawdown * self.max_drawdown_multiple:
            logger.critical(
                f"🔴 Shutdown threshold hit! "
                f"Current: ${current_drawdown:.2f}, "
                f"Limit: ${worst_drawdown * self.max_drawdown_multiple:.2f}"
            )
            return True
        return False

    def get_log_summary(self) -> dict:
        """Return trade log summary for dashboard."""
        recent = self.trade_log[-20:] if self.trade_log else []
        wins = sum(1 for t in recent if t["trade"].get("pnl", 0) > 0)
        return {
            "total_logged": len(self.trade_log),
            "recent_trades": recent[-10:],
            "recent_win_rate": f"{wins / max(len(recent), 1) * 100:.1f}%",
        }

"""
Memory Agent — the self-learning brain.
Stores every mistake with full context.
Queried before every trade to avoid repeating errors.
"""
import json
import os
from datetime import datetime
from typing import Optional

MEMORY_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "memory")

class MemoryAgent:
    """Stores, queries, and learns from trading mistakes."""

    def __init__(self):
        os.makedirs(MEMORY_DIR, exist_ok=True)
        self.memory_file = os.path.join(MEMORY_DIR, "mistakes.jsonl")
        self.lessons_file = os.path.join(MEMORY_DIR, "lessons.jsonl")
        self._load()

    def _load(self):
        """Load past mistakes into memory."""
        self.mistakes = []
        self.lessons = []
        if os.path.exists(self.memory_file):
            with open(self.memory_file) as f:
                for line in f:
                    if line.strip():
                        self.mistakes.append(json.loads(line))
        if os.path.exists(self.lessons_file):
            with open(self.lessons_file) as f:
                for line in f:
                    if line.strip():
                        self.lessons.append(json.loads(line))

    def learn(self, trade_result: dict) -> None:
        """
        Learn from a trade result.
        If it was a loss, analyze what went wrong and save the lesson.
        """
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "trade": trade_result,
            "lesson": self._analyze_mistake(trade_result),
        }

        # Save to mistakes log
        with open(self.memory_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
        self.mistakes.append(entry)

        # If it was a loss, extract a reusable lesson
        if trade_result.get("pnl", 0) < 0:
            lesson = self._extract_lesson(trade_result)
            with open(self.lessons_file, "a") as f:
                f.write(json.dumps(lesson) + "\n")
            self.lessons.append(lesson)

    def _analyze_mistake(self, trade: dict) -> str:
        """Analyze why a trade went wrong."""
        reasons = []
        if trade.get("pnl", 0) < 0:
            if trade.get("stop_loss_hit"):
                reasons.append("Stop loss triggered — position moved against us")
            if trade.get("slippage", 0) > 0.01:
                reasons.append(f"Excessive slippage: {trade['slippage']}")
            if trade.get("regime_mismatch"):
                reasons.append("Traded against regime signal")
            if not reasons:
                reasons.append("Direction was wrong — retracement or reversal")
        return "; ".join(reasons) if reasons else "Trade was profitable"

    def _extract_lesson(self, trade: dict) -> dict:
        """Extract a reusable lesson from a losing trade."""
        return {
            "lesson_id": f"L{len(self.lessons) + 1:04d}",
            "learned_at": datetime.utcnow().isoformat(),
            "market_condition": trade.get("market_condition", "unknown"),
            "signal_type": trade.get("signal_type", "unknown"),
            "what_went_wrong": trade.get("mistake", self._analyze_mistake(trade)),
            "how_to_avoid": self._suggest_avoidance(trade),
            "times_applied": 0,
        }

    def _suggest_avoidance(self, trade: dict) -> str:
        """Suggest how to avoid this mistake in the future."""
        if trade.get("stop_loss_hit"):
            return "Widen stop loss by 1.5x ATR or check if entry was against trend"
        if trade.get("slippage", 0) > 0.01:
            return "Use limit orders instead of market orders in low liquidity"
        if trade.get("regime_mismatch"):
            return "Only trade when regime detection confirms trend strength"
        return "Review entry timing — wait for confirmation candle"

    def query_current_setup(self, market_condition: str = None) -> list:
        """
        Before a trade, query memory for similar past mistakes.
        Returns relevant lessons the strategy agent should consider.
        """
        if not self.lessons:
            return []

        relevant = []
        for lesson in self.lessons:
            # Match by market condition if provided
            if market_condition and lesson.get("market_condition") == market_condition:
                relevant.append(lesson)
            # Also return general lessons
            elif lesson.get("signal_type"):
                relevant.append(lesson)

        # Mark queried lessons
        for r in relevant:
            r["times_applied"] = r.get("times_applied", 0) + 1

        return relevant[:5]  # Return top 5 most relevant lessons

    def get_memory_stats(self) -> dict:
        """Return memory statistics for the dashboard."""
        return {
            "total_mistakes": len(self.mistakes),
            "total_lessons": len(self.lessons),
            "last_lesson": self.lessons[-1] if self.lessons else None,
            "recent_mistakes": self.mistakes[-5:] if self.mistakes else [],
        }

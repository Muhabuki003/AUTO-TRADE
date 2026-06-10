"""
AutoTrade Orchestrator — the brain.
Coordinates all agents, manages the trade lifecycle,
and ensures the bot learns from every mistake.
"""
import json
import time
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger("autotrade")

class AutoTradeOrchestrator:
    """Main orchestrator that coordinates all trading agents."""

    def __init__(self, config_path: str = "data/config/config.yaml"):
        self.config = self._load_config(config_path)
        self.state = {
            "mode": "idle",  # idle | backtest | paper | live
            "capital": self.config.get("initial_capital", 30.0),
            "target": self.config.get("target", 100.0),
            "total_trades": 0,
            "wins": 0,
            "losses": 0,
            "current_drawdown": 0.0,
            "max_drawdown": 0.0,
            "kill_switch": False,
            "started_at": None,
        }
        self.agents = {}
        self.vision = None
        logger.info(f"AutoTrade v0.1 initialized — ${self.state['capital']} → ${self.state['target']}")

    def _load_config(self, path: str) -> dict:
        """Load configuration from YAML file."""
        import yaml
        try:
            with open(path) as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return {"initial_capital": 30.0, "target": 100.0}

    def register_agent(self, name: str, agent) -> None:
        """Register an agent with the orchestrator."""
        self.agents[name] = agent
        logger.info(f"Agent registered: {name}")

    def register_vision(self, api_key: str = None) -> None:
        """Register GLM-OCR vision module for chart/doc reading."""
        from agents.vision import ChartReader
        self.vision = ChartReader(api_key=api_key)
        logger.info("GLM-OCR Vision module registered")

    def run(self, mode: str = "backtest") -> None:
        """Run the bot in the specified mode."""
        self.state["mode"] = mode
        self.state["started_at"] = datetime.utcnow().isoformat()
        logger.info(f"Starting AutoTrade in {mode} mode")

        if mode == "backtest":
            self._run_backtest()
        elif mode in ("paper", "live"):
            self._run_trading_loop()

    def _run_trading_loop(self):
        """Main trading loop — runs until kill switch or target hit."""
        while not self.state["kill_switch"]:
            # 1. Check memory for past mistakes
            similar_mistakes = self._query_memory()

            # 2. Check regime — should we even trade?
            regime_ok = self._check_regime()

            # 3. Generate trade signal
            signal = self._generate_signal(similar_mistakes)

            # 4. Check risk limits
            if not self._check_risk(signal):
                continue

            # 5. Execute trade
            result = self._execute_trade(signal)

            # 6. Learn from result
            self._learn(result)

            # 7. Check if target hit
            if self.state["capital"] >= self.state["target"]:
                logger.info(f"🎯 Target hit! ${self.state['capital']:.2f}")
                self._notify("Target reached!", f"Capital: ${self.state['capital']:.2f}")
                break

            time.sleep(self.config.get("poll_interval", 60))

    def _query_memory(self) -> list:
        """Query memory agent for similar past mistakes."""
        mem = self.agents.get("memory")
        if mem:
            return mem.query_current_setup()
        return []

    def _check_regime(self) -> bool:
        """Check if current market regime is tradeable."""
        reg = self.agents.get("regime")
        if reg:
            return reg.is_tradeable()
        return True

    def _generate_signal(self, mistakes: list) -> Optional[dict]:
        """Generate a trade signal considering past mistakes."""
        strat = self.agents.get("strategy")
        if strat:
            return strat.generate_signal(mistakes)
        return None

    def _check_risk(self, signal: Optional[dict]) -> bool:
        """Check if trade falls within risk parameters."""
        risk = self.agents.get("risk")
        if risk and signal:
            return risk.approve_trade(signal, self.state)
        return True

    def _execute_trade(self, signal: dict) -> dict:
        """Execute the trade via execution agent."""
        exec_agent = self.agents.get("execution")
        if exec_agent:
            result = exec_agent.execute(signal)
            self.state["total_trades"] += 1
            if result.get("pnl", 0) > 0:
                self.state["wins"] += 1
            else:
                self.state["losses"] += 1
                self.state["current_drawdown"] += abs(result.get("pnl", 0))
            self.state["max_drawdown"] = max(
                self.state["max_drawdown"], self.state["current_drawdown"]
            )
            self.state["capital"] += result.get("pnl", 0)
            return result
        return {}

    def _learn(self, result: dict) -> None:
        """Feed trade result to memory agent to learn from mistakes."""
        mem = self.agents.get("memory")
        if mem:
            mem.learn(result)

    def _notify(self, title: str, message: str) -> None:
        """Send notification (Telegram / email / webhook)."""
        logger.info(f"🔔 {title}: {message}")

    def status(self) -> dict:
        """Return current status for the dashboard."""
        return {
            "mode": self.state["mode"],
            "capital": round(self.state["capital"], 2),
            "target": self.state["target"],
            "progress": f"{self.state['capital'] / self.state['target'] * 100:.1f}%",
            "total_trades": self.state["total_trades"],
            "win_rate": f"{self.state['wins'] / max(self.state['total_trades'], 1) * 100:.1f}%",
            "current_drawdown": round(self.state["current_drawdown"], 2),
            "max_drawdown": round(self.state["max_drawdown"], 2),
            "kill_switch": self.state["kill_switch"],
            "started_at": self.state["started_at"],
        }

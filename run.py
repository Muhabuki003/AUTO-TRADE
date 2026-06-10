#!/usr/bin/env python3
"""AutoTrade — entry point for running the trading bot."""
import argparse
import logging
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.orchestrator import AutoTradeOrchestrator
from agents.memory.agent import MemoryAgent
from agents.strategy.agent import StrategyAgent
from agents.risk.agent import RiskAgent
from agents.execution.agent import ExecutionAgent
from agents.regime.agent import RegimeAgent
from agents.monitor.agent import MonitorAgent


def setup_logging(verbose: bool = False):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def main():
    parser = argparse.ArgumentParser(description="AutoTrade — Self-Learning Trading Bot")
    parser.add_argument(
        "--mode", "-m",
        choices=["backtest", "paper", "live"],
        default="paper",
        help="Trading mode (default: paper)",
    )
    parser.add_argument(
        "--capital", "-c",
        type=float,
        default=30.0,
        help="Initial capital (default: $30)",
    )
    parser.add_argument(
        "--target", "-t",
        type=float,
        default=100.0,
        help="Target capital (default: $100)",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    setup_logging(args.verbose)
    logger = logging.getLogger("autotrade")

    print(r"""
    ╔══════════════════════════════════════╗
    ║         AUTO-TRADE v0.1              ║
    ║   Self-Learning Trading Bot          ║
    ║   ${} → ${}                    ║
    ╚══════════════════════════════════════╝
    """.format(args.capital, args.target))

    # Initialize orchestrator
    bot = AutoTradeOrchestrator()
    bot.state["capital"] = args.capital
    bot.state["target"] = args.target

    # Register agents
    bot.register_agent("memory", MemoryAgent())
    bot.register_agent("strategy", StrategyAgent())
    bot.register_agent("risk", RiskAgent())
    bot.register_agent("execution", ExecutionAgent())
    bot.register_agent("regime", RegimeAgent())
    bot.register_agent("monitor", MonitorAgent())

    # Print agent status
    print(f"\n  🤖 Agents: {len(bot.agents)} registered")
    print(f"  🧠 Memory: Learning from every trade")
    print(f"  🛡️  Risk:  2% max per trade")
    print(f"  🎯 Target: ${args.target}")
    print()

    # Run
    bot.run(mode=args.mode)


if __name__ == "__main__":
    main()

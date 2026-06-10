# AUTO-TRADE 🤖

A self-learning trading bot with memory — it understands when it makes a mistake, saves it to memory, and never makes the same mistake twice.

**Give it $30. Tell it to turn into $100. Watch it learn.**

## Architecture

```
┌──────────────────────────────────────────────────┐
│                    SITE                          │
│  Dashboard · Agent Status · Trade Log · Memory   │
└──────────────┬───────────────────────────────────┘
               │
┌──────────────▼───────────────────────────────────┐
│              ORCHESTRATOR AGENT                   │
│  Coordinates all agents, manages workflow flow   │
└──────┬──────┬──────┬──────┬──────┬──────┬───────┘
       │      │      │      │      │      │
  ┌────▼┐ ┌──▼──┐ ┌─▼───┐ ┌▼───┐ ┌▼───┐ ┌▼────┐
  │MEM │ │STRAT│ │RISK │ │EXEC│ │REG │ │MON  │
  │ORY │ │EGY  │ │     │ │    │ │IME │ │ITOR │
  └────┘ └─────┘ └─────┘ └────┘ └────┘ └─────┘
```

### Agents

| Agent | Role |
|-------|------|
| **Orchestrator** | Coordinates all agents, manages the trade workflow |
| **Memory** | Stores mistakes & lessons learned. Queried before every trade |
| **Strategy** | Analyzes market conditions, decides entry/exit signals |
| **Risk** | Position sizing (1-2%), daily drawdown limits, kill switch |
| **Execution** | API connections, order placement, error recovery |
| **Regime** | ATR/ADX analysis, knows when NOT to trade |
| **Monitor** | Tracks live vs backtest, detects decay, logs everything |

### Memory System

Every mistake is saved with context:
- What was the trade setup?
- What went wrong?
- What should the bot learn?
- How to avoid it next time?

On every new trade signal, the bot queries past memory for similar situations before acting.

## Getting Started

```bash
# Install dependencies
pip install -r requirements.txt

# Configure
cp data/config/config.example.yaml data/config/config.yaml

# Run backtest
python run.py --mode backtest

# Paper trade
python run.py --mode paper

# Live trade
python run.py --mode live
```

## The $30 → $100 Goal
- Start capital: $30
- Target: $100 (3.33x)
- Max risk per trade: 1-2% ($0.30-$0.60)
- Auto-kill on defined drawdown
- Bot stops and notifies when target hit

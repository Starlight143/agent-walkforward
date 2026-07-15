# agent-walkforward

**Stop overfitting your agent to its eval set.**

Agent eval tools (agentevals, RAGAS, DeepEval, your own JSONL log) score your
agent against a fixed set of cases. You tweak a prompt, the score goes up, you
ship. Sound familiar? It's the same trap quants fell into for decades: tune a
strategy against one slice of history, the backtest looks great, live trading
falls apart. The score went up because you overfit the *test*, not because the
agent got better.

`agent-walkforward` borrows the fix quants already built — **walk-forward
validation with purge and embargo** — and applies it to eval logs. It splits
your time-ordered eval records into in-sample (IS) and out-of-sample (OOS)
folds, then measures how much the score degrades out-of-sample. A large,
persistent IS→OOS gap means your gains are overfit to the eval set.

- **Zero dependencies.** Pure standard library. `pip install` and go.
- **Bring your own eval tool.** Reads JSONL / JSON / CSV with configurable
  field names — it sits *on top of* whatever you already use, not instead of it.
- **Leakage-aware.** Purge (drop IS records sharing a session/group with OOS)
  and embargo (temporal buffer) prevent the split from lying to you.

## Install

```bash
pip install agent-walkforward
```

Or from source:

```bash
git clone https://github.com/Starlight143/agent-walkforward
cd agent-walkforward
pip install -e ".[dev]"
```

## Quickstart

Your eval log is a list of scored records, ordered in time (by run, by version,
by commit — anything monotonic). One record per line for JSONL:

```json
{"id": "case-001", "timestamp": 1, "score": 0.92, "group": "sessionA"}
{"id": "case-002", "timestamp": 2, "score": 0.88, "group": "sessionA"}
```

Run it:

```bash
agent-walkforward run --traces examples/sample_traces.jsonl --n-splits 4 --oos-size 8
```

```
agent-walkforward 0.1.0  |  records=50
fold  IS_n  OOS_n   IS_mean  OOS_mean      gap   degr  purged  embargo
   1    18      8    0.886    0.787    0.099   0.889       0        0
   2    26      8    0.856    0.729    0.127   0.851       0        0
   3    34      8    0.826    0.670    0.156   0.811       0        0
   4    42      8    0.796    0.608    0.189   0.763       0        0
------------------------------------------------------------------
overall IS_mean= 0.841  OOS_mean= 0.698  mean_gap= 0.143
VERDICT: OVERFIT_RISK
```

The OOS score sits well below IS and the gap *widens* fold over fold — a
textbook sign that improvements are being tuned into the eval set rather than
into the agent.

### As a library

```python
from agent_walkforward import load_records, walk_forward_splits, evaluate

records = load_records("evals.jsonl")
sorted_records, folds = walk_forward_splits(records, n_splits=4, oos_size=8, embargo=2)
report = evaluate(sorted_records, folds)

print(report.verdict, report.mean_gap)
for f in report.folds:
    print(f.index, f.is_mean, f.oos_mean, f.gap)
```

## Concepts

| Term | What it means here |
|------|--------------------|
| **In-sample (IS)** | Records you'd have tuned against — everything before an OOS block. |
| **Out-of-sample (OOS)** | A held-out block of later records the tuning never saw. |
| **Walk-forward** | Consecutive OOS blocks tile the tail of the series; IS expands (or rolls) up to each block. |
| **Purge** | Drop IS records whose `group` (session / conversation / seed) also appears in the OOS block, so a shared context can't leak across the boundary. |
| **Embargo** | Drop the *N* IS records immediately before an OOS block, a buffer against temporal spillover. |
| **Gap** | `IS_mean − OOS_mean`. Positive and growing ⇒ overfitting. |
| **Degradation** | `OOS_mean / IS_mean` (only meaningful for non-negative scores). |

## Interop

The loader maps whatever field names your tool emits:

```bash
agent-walkforward run --traces run.csv \
  --id-field case_id --time-field ts --score-field response_match_score \
  --group-field conversation_id
```

That makes it a drop-in post-processor for agentevals OTel exports, RAGAS
result tables, DeepEval logs, or a hand-rolled JSONL.

## Agent integrations

Built to be called by coding agents (Claude Code, Cursor, Cline, ...), three ways:

**1. One-call Python API** — returns a plain JSON-serializable dict:

```python
from agent_walkforward import analyze

result = analyze("evals.jsonl", n_splits=5, oos_size=10, embargo=2)
# also accepts a list of dicts or EvalRecord objects instead of a path
print(result["verdict"], result["mean_gap"])
```

**2. CLI with `--json`** — for agents that shell out and parse stdout:

```bash
agent-walkforward run --traces evals.jsonl --json
```

**3. MCP server** — expose it as a native tool to any MCP client:

```bash
pip install "agent-walkforward[mcp]"
agent-walkforward-mcp          # stdio transport
```

Example Claude Desktop / Cursor config:

```json
{
  "mcpServers": {
    "agent-walkforward": { "command": "agent-walkforward-mcp" }
  }
}
```

The server exposes one tool, `walkforward_analyze`, taking either a `traces_path`
or inline `records`.

**Claude Code skill** — a ready-made skill lives in
[`integrations/claude-code-skill/`](integrations/claude-code-skill/SKILL.md).
Copy it to `~/.claude/skills/agent-walkforward/` and Claude Code will reach for
it whenever you ask "are these eval gains real or overfit?".

## When this helps — and when it doesn't

Walk-forward assumes your eval records have **temporal / versioned order** and
that you iterate against them over time. It shines when you have a growing eval
log across many runs or agent versions.

It does **not** help a one-shot eval of a static set with no ordering — there's
no "later" to hold out. And the verdict is a heuristic on the score scale
(default tuned for 0–1 scores), not a statistical significance test. Treat it
as a smoke alarm, not a p-value.

## Development

```bash
pip install -e ".[dev]"
pytest -q
```

## License

MIT — see [LICENSE](LICENSE).

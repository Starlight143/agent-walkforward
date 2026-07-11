---
name: agent-walkforward
description: Detect eval-set overfitting in an agent's evaluation log using walk-forward / out-of-sample validation. Use when the user has an eval log (JSONL/JSON/CSV of scored runs over time or versions) and asks whether score improvements are real or overfit to the eval set, or mentions walk-forward, out-of-sample, overfitting, or eval degradation.
---

# agent-walkforward

Validates whether an agent's rising eval scores generalize or are overfit to
the eval set — the same walk-forward + purge/embargo trick quants use to catch
backtest overfitting.

## When to use

Trigger when the user has a **time-ordered eval log** (many runs / versions /
commits, each with a score) and wants to know if improvements are trustworthy.
Not useful for a single one-shot eval with no ordering.

## How to run

Prefer the CLI with `--json` (parse the JSON, then explain the verdict):

```bash
agent-walkforward run --traces <path> --n-splits 5 --oos-size 10 --json
```

If field names differ from the defaults (`id`, `timestamp`, `score`, `group`),
map them:

```bash
agent-walkforward run --traces run.csv \
  --score-field response_match_score --time-field ts \
  --group-field conversation_id --json
```

If the package is not installed: `pip install agent-walkforward` (zero runtime
dependencies).

Programmatic alternative (one call, returns a dict):

```python
from agent_walkforward import analyze
result = analyze("evals.jsonl", n_splits=5, oos_size=10, embargo=2)
```

## Interpreting the result

The JSON has `verdict`, overall `is_mean` / `oos_mean` / `mean_gap`, and
per-fold detail.

- `verdict: OK` — out-of-sample tracks in-sample; improvements look real.
- `verdict: WATCH` — a moderate IS→OOS gap; keep an eye on it.
- `verdict: OVERFIT_RISK` — large gap, especially one that **widens** fold over
  fold, means the agent is being tuned into the eval set, not genuinely improved.

Report the verdict, the mean gap, and whether the per-fold gap is growing. The
verdict is a heuristic on the score scale (default tuned for 0–1 scores), not a
statistical significance test — frame it as a smoke alarm, not a p-value.

## Install this skill

Copy this folder to `~/.claude/skills/agent-walkforward/` (or a project's
`.claude/skills/`), then restart Claude Code.

"""MCP server exposing walk-forward validation as an agent tool.

Optional: requires the `mcp` extra ->  pip install "agent-walkforward[mcp]"

Run:  agent-walkforward-mcp        (stdio transport)
Wire it into Claude Desktop / Cursor / Cline as a stdio MCP server.
"""

from __future__ import annotations

from typing import Any

from .api import analyze

try:
    from mcp.server.fastmcp import FastMCP
except ModuleNotFoundError as e:  # pragma: no cover - only hit without the extra
    raise SystemExit(
        "The MCP server needs the optional 'mcp' dependency.\n"
        'Install it with:  pip install "agent-walkforward[mcp]"'
    ) from e

mcp = FastMCP("agent-walkforward")


@mcp.tool()
def walkforward_analyze(
    traces_path: str = "",
    records: list[dict[str, Any]] | None = None,
    n_splits: int = 5,
    oos_size: int = 10,
    is_size: int | None = None,
    embargo: int = 0,
    purge: bool = True,
    gap_threshold: float = 0.1,
    id_field: str = "id",
    time_field: str = "timestamp",
    score_field: str = "score",
    group_field: str = "group",
) -> dict:
    """Run walk-forward / out-of-sample validation on an agent-eval log to
    detect eval-set overfitting.

    Provide exactly one source: `traces_path` (a .jsonl/.json/.csv file) or
    `records` (a list of {id, timestamp, score, group} objects). Records are
    ordered by timestamp, split into expanding in-sample / out-of-sample folds
    with purge + embargo leakage controls, and scored.

    Returns a dict with `verdict` (OK / WATCH / OVERFIT_RISK), overall
    `is_mean` / `oos_mean` / `mean_gap`, and per-fold detail. A large,
    widening IS->OOS gap means improvements are overfit to the eval set.
    """
    if bool(traces_path) == bool(records):
        raise ValueError("provide exactly one of `traces_path` or `records`")
    source: Any = traces_path if traces_path else records
    return analyze(
        source,
        n_splits=n_splits,
        oos_size=oos_size,
        is_size=is_size,
        embargo=embargo,
        purge=purge,
        gap_threshold=gap_threshold,
        id_field=id_field,
        time_field=time_field,
        score_field=score_field,
        group_field=group_field,
    )


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()

"""One-call, agent-friendly entry point.

`analyze()` collapses load -> split -> evaluate into a single call that returns
a plain JSON-serializable dict, so an agent (or the CLI, or the MCP server) can
get a verdict without touching the lower-level pieces.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, Mapping

from .evaluate import evaluate
from .loader import load_records
from .models import EvalRecord, Report
from .split import walk_forward_splits


def _coerce_records(
    source: str | Path | Iterable[Mapping[str, Any] | EvalRecord],
    field_map: dict,
) -> list[EvalRecord]:
    """Accept a file path, a list of dicts, or a list of EvalRecord."""
    if isinstance(source, (str, Path)):
        return load_records(source, **field_map)

    id_f = field_map.get("id_field", "id")
    time_f = field_map.get("time_field", "timestamp")
    score_f = field_map.get("score_field", "score")
    group_f = field_map.get("group_field", "group")

    records: list[EvalRecord] = []
    for i, row in enumerate(source):
        if isinstance(row, EvalRecord):
            records.append(row)
            continue
        if score_f not in row or row[score_f] in (None, ""):
            raise ValueError(f"record {i}: missing score field {score_f!r}")
        group = row.get(group_f) if group_f else None
        records.append(
            EvalRecord(
                id=str(row.get(id_f, i)),
                timestamp=float(row[time_f]) if row.get(time_f) not in (None, "") else float(i),
                score=float(row[score_f]),
                group=str(group) if group not in (None, "") else None,
            )
        )
    if not records:
        raise ValueError("no records provided")
    return records


def report_to_dict(report: Report, n_records: int) -> dict:
    return {
        "verdict": report.verdict,
        "n_records": n_records,
        "is_mean": report.is_mean,
        "oos_mean": report.oos_mean,
        "mean_gap": report.mean_gap,
        "degradation": report.degradation,
        "params": report.params,
        "folds": [vars(f) for f in report.folds],
    }


def analyze(
    source: str | Path | Iterable[Mapping[str, Any] | EvalRecord],
    *,
    n_splits: int = 5,
    oos_size: int = 10,
    is_size: int | None = None,
    embargo: int = 0,
    purge: bool = True,
    gap_threshold: float = 0.1,
    id_field: str = "id",
    time_field: str = "timestamp",
    score_field: str = "score",
    group_field: str | None = "group",
) -> dict:
    """Run walk-forward validation end-to-end and return a result dict.

    `source` may be a path to a .jsonl/.json/.csv log, a list of dicts, or a
    list of EvalRecord. Returns the same shape the CLI emits with --json.
    """
    field_map = {
        "id_field": id_field,
        "time_field": time_field,
        "score_field": score_field,
        "group_field": group_field,
    }
    records = _coerce_records(source, field_map)
    sorted_records, folds = walk_forward_splits(
        records,
        n_splits=n_splits,
        oos_size=oos_size,
        is_size=is_size,
        embargo=embargo,
        purge=purge,
    )
    report = evaluate(sorted_records, folds, gap_threshold=gap_threshold)
    return report_to_dict(report, len(records))

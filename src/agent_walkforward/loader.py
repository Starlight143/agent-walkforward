"""Load eval records from JSONL / JSON / CSV.

Field names are configurable so this stays compatible with whatever your eval
tool (agentevals, RAGAS, DeepEval, a home-grown JSONL log, ...) already emits.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterable

from .models import EvalRecord


class LoaderError(ValueError):
    pass


def _coerce_time(value, fallback_index: int) -> float:
    """Timestamps may be epoch floats or ISO-8601 strings. Fall back to row
    order when absent, so ordering still works on append-only logs."""
    if value is None or value == "":
        return float(fallback_index)
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip()
    try:
        return float(s)
    except ValueError:
        pass
    from datetime import datetime

    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
    except ValueError as e:
        raise LoaderError(f"cannot parse timestamp {value!r}") from e


def _rows_from_file(path: Path) -> Iterable[dict]:
    suffix = path.suffix.lower()
    text = path.read_text(encoding="utf-8")
    if suffix == ".csv":
        yield from csv.DictReader(text.splitlines())
        return
    if suffix == ".jsonl" or suffix == ".ndjson":
        for line in text.splitlines():
            line = line.strip()
            if line:
                yield json.loads(line)
        return
    # .json — either a list of objects or {"results": [...]}-ish wrapper.
    data = json.loads(text)
    if isinstance(data, dict):
        for key in ("results", "records", "data", "evals"):
            if isinstance(data.get(key), list):
                data = data[key]
                break
    if not isinstance(data, list):
        raise LoaderError(
            "JSON must be a list of records or an object wrapping one under "
            "results/records/data/evals"
        )
    yield from data


def load_records(
    path: str | Path,
    *,
    id_field: str = "id",
    time_field: str = "timestamp",
    score_field: str = "score",
    group_field: str | None = "group",
) -> list[EvalRecord]:
    """Read records from `path`. Score is required; id/timestamp fall back to
    row order; group is optional."""
    path = Path(path)
    if not path.is_file():
        raise LoaderError(f"file not found: {path}")

    records: list[EvalRecord] = []
    for i, row in enumerate(_rows_from_file(path)):
        if score_field not in row or row[score_field] in (None, ""):
            raise LoaderError(f"row {i}: missing score field {score_field!r}")
        try:
            score = float(row[score_field])
        except (TypeError, ValueError) as e:
            raise LoaderError(f"row {i}: score {row[score_field]!r} not numeric") from e

        rec_id = str(row.get(id_field, i)) if id_field else str(i)
        ts = _coerce_time(row.get(time_field), i)
        group = None
        if group_field and row.get(group_field) not in (None, ""):
            group = str(row[group_field])

        records.append(EvalRecord(id=rec_id, timestamp=ts, score=score, group=group))

    if not records:
        raise LoaderError(f"no records loaded from {path}")
    return records

"""Walk-forward splitting with purge + embargo.

Adapts the expanding-window walk-forward scheme (with purge/embargo leakage
controls, cf. Lopez de Prado, *Advances in Financial Machine Learning*) to a
time-ordered series of agent-eval records.

Fold k tiles the tail of the series with consecutive out-of-sample blocks:

    OOS_k   = a contiguous block of `oos_size` records
    IS_k    = records before OOS_k  (expanding, or last `is_size` if rolling)
    embargo = drop the `embargo` IS records immediately before OOS_k
    purge   = drop IS records whose group also appears in OOS_k
"""

from __future__ import annotations

from typing import Iterable

from .models import EvalRecord, Fold


def walk_forward_splits(
    records: Iterable[EvalRecord],
    *,
    n_splits: int,
    oos_size: int,
    is_size: int | None = None,
    embargo: int = 0,
    purge: bool = True,
) -> tuple[list[EvalRecord], list[Fold]]:
    """Build walk-forward folds.

    Returns (sorted_records, folds). Fold indices reference `sorted_records`,
    which is the input sorted ascending by timestamp (stable).

    Raises ValueError on invalid params or insufficient data.
    """
    if n_splits < 1:
        raise ValueError("n_splits must be >= 1")
    if oos_size < 1:
        raise ValueError("oos_size must be >= 1")
    if embargo < 0:
        raise ValueError("embargo must be >= 0")
    if is_size is not None and is_size < 1:
        raise ValueError("is_size must be >= 1 when provided")

    sorted_records = sorted(records, key=lambda r: r.timestamp)
    n = len(sorted_records)

    # Need every OOS block to fit at the tail, plus at least 1 IS record for the
    # earliest fold (before embargo/purge, which may thin it further).
    need = n_splits * oos_size + 1
    if n < need:
        raise ValueError(
            f"not enough records: have {n}, need >= {need} "
            f"(n_splits*oos_size + 1)"
        )

    folds: list[Fold] = []
    for k in range(n_splits):
        oos_start = n - (n_splits - k) * oos_size
        oos_end = oos_start + oos_size
        oos_index = list(range(oos_start, oos_end))

        is_end = oos_start
        is_start = 0 if is_size is None else max(0, is_end - is_size)

        # embargo: drop the buffer immediately before OOS
        embargo_end = max(is_start, is_end - embargo)
        embargoed = is_end - embargo_end
        candidate_is = list(range(is_start, embargo_end))

        purged = 0
        if purge:
            oos_groups = {sorted_records[i].group_key for i in oos_index}
            kept = [i for i in candidate_is if sorted_records[i].group_key not in oos_groups]
            purged = len(candidate_is) - len(kept)
            candidate_is = kept

        folds.append(
            Fold(
                index=k + 1,
                is_index=candidate_is,
                oos_index=oos_index,
                purged=purged,
                embargoed=embargoed,
            )
        )

    return sorted_records, folds

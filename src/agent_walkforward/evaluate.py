"""Turn walk-forward folds into IS/OOS overfitting diagnostics."""

from __future__ import annotations

from statistics import fmean

from .models import EvalRecord, Fold, FoldResult, Report

# Denominator guard: catches IEEE-754 subnormals that <= 0.0 / == 0.0 miss.
_EPS = 1e-14


def _ratio(num: float, denom: float) -> float | None:
    if not (abs(denom) > _EPS):
        return None
    return num / denom


def evaluate(
    sorted_records: list[EvalRecord],
    folds: list[Fold],
    *,
    gap_threshold: float = 0.1,
) -> Report:
    """Aggregate per-fold IS/OOS scores and emit an overfitting verdict.

    `gap_threshold` is on the score scale (default assumes 0..1 scores).
    Verdict is a heuristic, not a statistical test — see README.
    """
    results: list[FoldResult] = []
    for f in folds:
        is_scores = [sorted_records[i].score for i in f.is_index]
        oos_scores = [sorted_records[i].score for i in f.oos_index]
        is_mean = fmean(is_scores) if is_scores else None
        oos_mean = fmean(oos_scores) if oos_scores else None

        gap = None
        degradation = None
        if is_mean is not None and oos_mean is not None:
            gap = is_mean - oos_mean
            degradation = _ratio(oos_mean, is_mean)

        results.append(
            FoldResult(
                index=f.index,
                is_n=len(is_scores),
                oos_n=len(oos_scores),
                is_mean=is_mean,
                oos_mean=oos_mean,
                gap=gap,
                degradation=degradation,
                purged=f.purged,
                embargoed=f.embargoed,
            )
        )

    is_means = [r.is_mean for r in results if r.is_mean is not None]
    oos_means = [r.oos_mean for r in results if r.oos_mean is not None]
    gaps = [r.gap for r in results if r.gap is not None]

    is_mean_all = fmean(is_means) if is_means else None
    oos_mean_all = fmean(oos_means) if oos_means else None
    mean_gap = fmean(gaps) if gaps else None
    degradation_all = (
        _ratio(oos_mean_all, is_mean_all)
        if (is_mean_all is not None and oos_mean_all is not None)
        else None
    )

    if mean_gap is None:
        verdict = "N/A"
    elif mean_gap > gap_threshold:
        verdict = "OVERFIT_RISK"
    elif mean_gap > gap_threshold / 2:
        verdict = "WATCH"
    else:
        verdict = "OK"

    return Report(
        folds=results,
        is_mean=is_mean_all,
        oos_mean=oos_mean_all,
        mean_gap=mean_gap,
        degradation=degradation_all,
        verdict=verdict,
        params={"gap_threshold": gap_threshold, "n_folds": len(folds)},
    )

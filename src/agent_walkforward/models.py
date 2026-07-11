"""Data models. Plain dataclasses, no third-party deps."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class EvalRecord:
    """One agent-eval outcome.

    id:        unique record id.
    timestamp: ordering key (epoch seconds, run index, version number, ...).
               Records are sorted ascending by this before splitting.
    score:     the eval score. Any float; higher = better is assumed for the
               degradation verdict, but the raw gap is sign-agnostic.
    group:     leakage-grouping key (e.g. conversation / session / seed id).
               Records sharing a group must not straddle the IS/OOS boundary,
               so IS records whose group appears in OOS get purged.
               Defaults to the record id (each record its own group).
    """

    id: str
    timestamp: float
    score: float
    group: str | None = None

    @property
    def group_key(self) -> str:
        return self.group if self.group is not None else self.id


@dataclass(frozen=True)
class Fold:
    """Index sets into the time-sorted record list for one walk-forward step."""

    index: int  # 1-based fold number
    is_index: list[int]
    oos_index: list[int]
    purged: int  # IS records dropped by purge
    embargoed: int  # IS records dropped by embargo


@dataclass
class FoldResult:
    index: int
    is_n: int
    oos_n: int
    is_mean: float | None
    oos_mean: float | None
    gap: float | None  # is_mean - oos_mean (positive => degrades OOS)
    degradation: float | None  # oos_mean / is_mean (only meaningful for >=0 scores)
    purged: int
    embargoed: int


@dataclass
class Report:
    folds: list[FoldResult] = field(default_factory=list)
    is_mean: float | None = None
    oos_mean: float | None = None
    mean_gap: float | None = None
    degradation: float | None = None
    verdict: str = "N/A"
    params: dict = field(default_factory=dict)

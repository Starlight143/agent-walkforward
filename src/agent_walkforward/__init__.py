"""agent-walkforward: walk-forward / out-of-sample validation for agent evals.

Detect eval-set overfitting the way quants detect backtest overfitting:
split time-ordered eval records into in-sample / out-of-sample folds with
purge + embargo, then measure how much score degrades out-of-sample.
"""

from .models import EvalRecord, Fold, FoldResult, Report
from .split import walk_forward_splits
from .evaluate import evaluate
from .loader import load_records
from .api import analyze, report_to_dict

__version__ = "0.1.1"

__all__ = [
    "EvalRecord",
    "Fold",
    "FoldResult",
    "Report",
    "walk_forward_splits",
    "evaluate",
    "load_records",
    "analyze",
    "report_to_dict",
    "__version__",
]

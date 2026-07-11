"""Command-line interface: `agent-walkforward run --traces ...`."""

from __future__ import annotations

import argparse
import json
import sys

from . import __version__
from .api import report_to_dict
from .evaluate import evaluate
from .loader import LoaderError, load_records
from .split import walk_forward_splits


def _fmt(x: float | None) -> str:
    return "  --  " if x is None else f"{x:6.3f}"


def _run(args: argparse.Namespace) -> int:
    try:
        records = load_records(
            args.traces,
            id_field=args.id_field,
            time_field=args.time_field,
            score_field=args.score_field,
            group_field=args.group_field,
        )
        sorted_records, folds = walk_forward_splits(
            records,
            n_splits=args.n_splits,
            oos_size=args.oos_size,
            is_size=args.is_size,
            embargo=args.embargo,
            purge=not args.no_purge,
        )
        report = evaluate(sorted_records, folds, gap_threshold=args.gap_threshold)
    except (LoaderError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(report_to_dict(report, len(records)), indent=2))
        return 0

    print(f"agent-walkforward {__version__}  |  records={len(records)}")
    print(
        "fold  IS_n  OOS_n   IS_mean  OOS_mean      gap   degr  purged  embargo"
    )
    for f in report.folds:
        print(
            f"{f.index:>4}  {f.is_n:>4}  {f.oos_n:>5}   "
            f"{_fmt(f.is_mean)}   {_fmt(f.oos_mean)}   {_fmt(f.gap)}  "
            f"{_fmt(f.degradation)}  {f.purged:>6}  {f.embargoed:>7}"
        )
    print("-" * 66)
    print(
        f"overall IS_mean={_fmt(report.is_mean)}  OOS_mean={_fmt(report.oos_mean)}  "
        f"mean_gap={_fmt(report.mean_gap)}"
    )
    print(f"VERDICT: {report.verdict}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="agent-walkforward",
        description="Walk-forward / out-of-sample validation for agent evals. "
        "Detects eval-set overfitting.",
    )
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    r = sub.add_parser("run", help="run walk-forward validation on an eval log")
    r.add_argument("--traces", required=True, help="path to .jsonl/.json/.csv eval log")
    r.add_argument("--n-splits", type=int, default=5, dest="n_splits")
    r.add_argument("--oos-size", type=int, default=10, dest="oos_size",
                   help="records per out-of-sample block")
    r.add_argument("--is-size", type=int, default=None, dest="is_size",
                   help="rolling in-sample window size (default: expanding)")
    r.add_argument("--embargo", type=int, default=0,
                   help="IS records to drop immediately before each OOS block")
    r.add_argument("--no-purge", action="store_true",
                   help="disable group-based purge")
    r.add_argument("--gap-threshold", type=float, default=0.1, dest="gap_threshold")
    r.add_argument("--id-field", default="id", dest="id_field")
    r.add_argument("--time-field", default="timestamp", dest="time_field")
    r.add_argument("--score-field", default="score", dest="score_field")
    r.add_argument("--group-field", default="group", dest="group_field")
    r.add_argument("--json", action="store_true", help="emit JSON instead of a table")
    r.set_defaults(func=_run)
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

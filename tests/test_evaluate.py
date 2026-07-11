from agent_walkforward import EvalRecord, evaluate, walk_forward_splits


def _series(scores):
    return [EvalRecord(id=str(i), timestamp=float(i), score=s) for i, s in enumerate(scores)]


def test_known_means_and_gap():
    # 20 records: IS (first 10) all 1.0, OOS (last 10) all 0.5.
    recs = _series([1.0] * 10 + [0.5] * 10)
    sorted_recs, folds = walk_forward_splits(recs, n_splits=1, oos_size=10)
    report = evaluate(sorted_recs, folds)
    f = report.folds[0]
    assert f.is_mean == 1.0
    assert f.oos_mean == 0.5
    assert f.gap == 0.5
    assert f.degradation == 0.5
    assert report.verdict == "OVERFIT_RISK"


def test_no_gap_is_ok():
    recs = _series([0.7] * 20)
    sorted_recs, folds = walk_forward_splits(recs, n_splits=2, oos_size=5)
    report = evaluate(sorted_recs, folds)
    assert report.mean_gap == 0.0
    assert report.verdict == "OK"


def test_degradation_none_when_is_mean_zero():
    recs = _series([0.0] * 10 + [0.0] * 10)
    sorted_recs, folds = walk_forward_splits(recs, n_splits=1, oos_size=10)
    report = evaluate(sorted_recs, folds)
    assert report.folds[0].degradation is None


def test_empty_is_fold_handled():
    # embargo wipes out the entire IS of the first fold; means become None.
    recs = _series([1.0] * 12)
    sorted_recs, folds = walk_forward_splits(recs, n_splits=2, oos_size=5, embargo=100)
    report = evaluate(sorted_recs, folds)
    assert report.folds[0].is_mean is None
    assert report.folds[0].gap is None

import pytest

from agent_walkforward import EvalRecord, walk_forward_splits


def _recs(n, group_of=None):
    return [
        EvalRecord(id=str(i), timestamp=float(i), score=0.0, group=group_of(i) if group_of else None)
        for i in range(n)
    ]


def test_expanding_tiles_tail_and_is_disjoint():
    recs = _recs(30)
    sorted_recs, folds = walk_forward_splits(recs, n_splits=3, oos_size=5)
    assert len(folds) == 3
    # OOS blocks tile the last 15 records consecutively.
    assert folds[0].oos_index == list(range(15, 20))
    assert folds[1].oos_index == list(range(20, 25))
    assert folds[2].oos_index == list(range(25, 30))
    # expanding IS = everything before the OOS block.
    assert folds[0].is_index == list(range(0, 15))
    assert folds[2].is_index == list(range(0, 25))
    # IS and OOS never overlap.
    for f in folds:
        assert set(f.is_index).isdisjoint(f.oos_index)


def test_rolling_is_size_caps_window():
    recs = _recs(30)
    _, folds = walk_forward_splits(recs, n_splits=3, oos_size=5, is_size=4)
    assert folds[0].is_index == [11, 12, 13, 14]
    assert folds[2].is_index == [21, 22, 23, 24]


def test_embargo_drops_buffer_before_oos():
    recs = _recs(30)
    _, folds = walk_forward_splits(recs, n_splits=3, oos_size=5, embargo=2)
    # first OOS starts at 15; embargo removes indices 13,14 from IS.
    assert folds[0].is_index == list(range(0, 13))
    assert folds[0].embargoed == 2


def test_purge_removes_is_records_sharing_oos_group():
    # group by parity of a fixed key so a group straddles the boundary.
    # Put record 14 (IS) in the same group as record 15 (OOS).
    recs = _recs(30, group_of=lambda i: "shared" if i in (14, 15) else str(i))
    _, folds = walk_forward_splits(recs, n_splits=3, oos_size=5)
    # index 14 is in IS of fold 1 but shares group "shared" with OOS index 15.
    assert 14 not in folds[0].is_index
    assert folds[0].purged == 1


def test_insufficient_data_raises():
    with pytest.raises(ValueError, match="not enough records"):
        walk_forward_splits(_recs(10), n_splits=3, oos_size=5)


def test_bad_params_raise():
    with pytest.raises(ValueError):
        walk_forward_splits(_recs(30), n_splits=0, oos_size=5)
    with pytest.raises(ValueError):
        walk_forward_splits(_recs(30), n_splits=3, oos_size=0)
    with pytest.raises(ValueError):
        walk_forward_splits(_recs(30), n_splits=3, oos_size=5, embargo=-1)


def test_unsorted_input_is_sorted_by_timestamp():
    recs = [EvalRecord(id=str(i), timestamp=float(30 - i), score=0.0) for i in range(30)]
    sorted_recs, _ = walk_forward_splits(recs, n_splits=3, oos_size=5)
    ts = [r.timestamp for r in sorted_recs]
    assert ts == sorted(ts)

import json

import pytest

from agent_walkforward import analyze


def _rows(scores):
    return [{"id": str(i), "timestamp": i, "score": s} for i, s in enumerate(scores)]


def test_analyze_from_list_of_dicts():
    result = analyze(_rows([1.0] * 10 + [0.5] * 10), n_splits=1, oos_size=10)
    assert result["verdict"] == "OVERFIT_RISK"
    assert result["is_mean"] == 1.0
    assert result["oos_mean"] == 0.5
    assert result["n_records"] == 20
    assert len(result["folds"]) == 1


def test_analyze_from_path(tmp_path):
    p = tmp_path / "e.jsonl"
    p.write_text("\n".join(json.dumps(r) for r in _rows([0.7] * 20)), encoding="utf-8")
    result = analyze(p, n_splits=2, oos_size=5)
    assert result["verdict"] == "OK"


def test_analyze_result_is_json_serializable():
    result = analyze(_rows([0.9, 0.8] * 10), n_splits=2, oos_size=5)
    json.dumps(result)  # must not raise


def test_analyze_custom_score_field():
    rows = [{"score_x": s, "timestamp": i} for i, s in enumerate([0.6] * 20)]
    result = analyze(rows, n_splits=2, oos_size=5, score_field="score_x")
    assert result["verdict"] == "OK"


def test_analyze_missing_score_raises():
    with pytest.raises(ValueError, match="missing score"):
        analyze([{"id": "a", "timestamp": 0}], n_splits=1, oos_size=1)


def test_mcp_tool_wraps_analyze():
    pytest.importorskip("mcp")  # skip when the optional [mcp] extra isn't installed
    from agent_walkforward import mcp_server as mcp

    out = mcp.walkforward_analyze(records=_rows([1.0] * 10 + [0.5] * 10),
                                  n_splits=1, oos_size=10)
    assert out["verdict"] == "OVERFIT_RISK"
    with pytest.raises(ValueError, match="exactly one"):
        mcp.walkforward_analyze(traces_path="x.jsonl", records=_rows([0.5] * 20))

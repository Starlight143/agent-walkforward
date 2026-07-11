import json

import pytest

from agent_walkforward.loader import LoaderError, load_records


def test_jsonl_roundtrip(tmp_path):
    p = tmp_path / "e.jsonl"
    p.write_text(
        "\n".join(
            json.dumps({"id": f"r{i}", "timestamp": i, "score": i / 10, "group": "g"})
            for i in range(3)
        ),
        encoding="utf-8",
    )
    recs = load_records(p)
    assert len(recs) == 3
    assert recs[0].id == "r0"
    assert recs[1].score == 0.1
    assert recs[2].group == "g"


def test_json_array_and_wrapper(tmp_path):
    p = tmp_path / "e.json"
    p.write_text(json.dumps({"results": [{"score": 0.5}, {"score": 0.6}]}), encoding="utf-8")
    recs = load_records(p)
    assert [r.score for r in recs] == [0.5, 0.6]
    # id/timestamp fall back to row order.
    assert recs[0].timestamp == 0.0
    assert recs[1].id == "1"


def test_csv_with_custom_fields(tmp_path):
    p = tmp_path / "e.csv"
    p.write_text("run,when,metric\na,1,0.9\nb,2,0.4\n", encoding="utf-8")
    recs = load_records(p, id_field="run", time_field="when", score_field="metric",
                        group_field=None)
    assert [r.score for r in recs] == [0.9, 0.4]
    assert recs[0].id == "a"


def test_iso_timestamp_parsed(tmp_path):
    p = tmp_path / "e.jsonl"
    p.write_text(json.dumps({"score": 0.5, "timestamp": "2026-01-01T00:00:00Z"}), encoding="utf-8")
    recs = load_records(p)
    assert recs[0].timestamp > 0


def test_missing_score_raises(tmp_path):
    p = tmp_path / "e.jsonl"
    p.write_text(json.dumps({"id": "x"}), encoding="utf-8")
    with pytest.raises(LoaderError, match="missing score"):
        load_records(p)


def test_non_numeric_score_raises(tmp_path):
    p = tmp_path / "e.jsonl"
    p.write_text(json.dumps({"score": "abc"}), encoding="utf-8")
    with pytest.raises(LoaderError, match="not numeric"):
        load_records(p)


def test_missing_file_raises(tmp_path):
    with pytest.raises(LoaderError, match="file not found"):
        load_records(tmp_path / "nope.jsonl")

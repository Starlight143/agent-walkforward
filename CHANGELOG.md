# Changelog

All notable changes to this project are documented here. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/); this project uses
[Semantic Versioning](https://semver.org/).

## [0.1.0] - 2026-07-11

Initial release.

### Added
- Walk-forward splitter with expanding or rolling in-sample windows.
- Purge (group-based leakage removal) and embargo (temporal buffer) controls.
- IS/OOS diagnostics: per-fold gap, degradation ratio, and a heuristic
  overfitting verdict (`OK` / `WATCH` / `OVERFIT_RISK`).
- Loader for JSONL / JSON / CSV eval logs with configurable field names,
  compatible with agentevals / RAGAS / DeepEval-style exports.
- `agent-walkforward run` CLI with table and `--json` output.
- Zero runtime dependencies (standard library only).

[0.1.0]: https://github.com/Starlight143/agent-walkforward/releases/tag/v0.1.0

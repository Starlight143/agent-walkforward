# Changelog

All notable changes to this project are documented here. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/); this project uses
[Semantic Versioning](https://semver.org/).

## [0.1.2] - 2026-07-16

No code changes. First release actually published to PyPI — v0.1.0/v0.1.1
were GitHub-only; `pip install agent-walkforward` was documented but 404'd.

### Fixed
- README no longer claims `pip install agent-walkforward` works before the
  package exists on PyPI; leads with source install instead.

### Added
- `.github/workflows/publish.yml` — publishes to PyPI via Trusted Publishing
  (OIDC) on every GitHub Release.
- `PUBLISHING.md` documenting the one-time PyPI/GitHub setup and the release
  cadence going forward.

## [0.1.1] - 2026-07-11

### Added
- `analyze()` one-call API: path / list-of-dicts / list-of-EvalRecord in, result
  dict out — agent-friendly single entry point.
- MCP server (`agent-walkforward-mcp`, optional `[mcp]` extra) exposing a
  `walkforward_analyze` tool for Claude Desktop / Cursor / Cline and other MCP
  clients.
- Claude Code skill under `integrations/claude-code-skill/`.

### Changed
- CLI `--json` output now shares the `analyze()` serializer and includes
  `n_records`.

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

[0.1.2]: https://github.com/Starlight143/agent-walkforward/releases/tag/v0.1.2
[0.1.1]: https://github.com/Starlight143/agent-walkforward/releases/tag/v0.1.1
[0.1.0]: https://github.com/Starlight143/agent-walkforward/releases/tag/v0.1.0

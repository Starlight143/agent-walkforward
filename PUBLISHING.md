# Publishing to PyPI

This repo is not yet published to PyPI (`pip install agent-walkforward`
currently 404s). `.github/workflows/publish.yml` is wired up to publish
automatically on every GitHub Release via [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/)
(OIDC — no long-lived API token stored in the repo). Two manual steps only
you can do (they require your PyPI login), then it's fully automated.

## One-time setup

1. **Create a PyPI account** if you don't have one: https://pypi.org/account/register/
2. **Register the trusted publisher** — this can be done *before* the project
   exists on PyPI ("pending publisher"):
   - Go to https://pypi.org/manage/account/publishing/
   - Add a new pending publisher:
     - PyPI project name: `agent-walkforward`
     - Owner: `Starlight143`
     - Repository name: `agent-walkforward`
     - Workflow filename: `publish.yml`
     - Environment name: `pypi`
3. In the GitHub repo → Settings → Environments → create an environment named
   `pypi` (matches the workflow's `environment: pypi`). No secrets needed —
   trusted publishing uses short-lived OIDC tokens per run.

## Every release after that

1. Bump the version in `src/agent_walkforward/__init__.py` (hatch reads it
   from there) and add a `CHANGELOG.md` entry.
2. Tag and push: `git tag v0.1.2 && git push origin v0.1.2`
3. GitHub → Releases → Draft a new release from that tag → Publish.
4. The `publish.yml` workflow builds the sdist/wheel and uploads to PyPI
   automatically — no local `twine upload` needed.

## Verifying locally before a release (optional)

```bash
python -m pip install build twine
python -m build
python -m twine check dist/agent_walkforward-*
```

Both `dist/agent_walkforward-0.1.1-py3-none-any.whl` and the matching
`.tar.gz` already passed `twine check` locally (2026-07-16) — the package
itself is publish-ready, only the PyPI-side trusted-publisher registration
above is outstanding.

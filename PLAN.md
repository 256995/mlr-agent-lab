# PLAN.md

Keep this short. One checked-off list of what is done, and exactly one **next step**.
Update it at the end of every step (rules: `AGENTS.md`).

Last updated: 2026-10-14

## Done

- [x] Working rules written for agents — `AGENTS.md` (read first, uv only, checks before done).
- [x] `CLAUDE.md` loads the rules via `@AGENTS.md`.
- [x] `README.md` — goal and how to run things.
- [x] `RUNS.md` — run log started with the setup run.
- [x] Verified the example script runs: `PYTHONUTF8=1 uv run --no-project random_greeting.py` → exit 0.
- [x] `git init` + first commit + public repo `github.com/256995/mlr-agent-lab` (branch `main`,
      `.gitignore` added, `uv.lock` deliberately not ignored).
- [x] Real uv project: `pyproject.toml` + `uv.lock` committed, `.venv` from CPython 3.13.2.
      `uv init` never had to run — `uv add` created the metadata. `--no-project` no longer needed.
- [x] **Snake** — `snake/index.html`, classic rules, one self-contained file (canvas, keyboard
      + touch, pause/restart, best score in `localStorage`). Verified: 18 in-page core checks
      and 23 live browser checks over DevTools protocol, plus a 300-game seeded replay for
      false self-collisions. See `RUNS.md`.
- [x] Lint wired up: `ruff` as a dev dep, `uv run --dev ruff check snake/check.py` clean.
- [x] `pytest` as a dev dep (`uv run pytest -q`).
- [x] **Pawn in CadQuery** — `pawn_model.py`: one closed profile in the XZ plane (rim arc,
      concave waist, collar bead, tapered shaft, neck, spherical head) revolved 360° into a
      *single* solid, with a `check_profile()` self-check that refuses a disconnected wire,
      a neck that overshoots the head, or a shaft that swallows the collar. 23.5 mm tall on
      a 11.2 mm base (height/base 2.10), 639 mm³, 7 faces, valid.
- [x] **Mesh export** — `export_pawn_mesh.py` → `docs/pawn.json` (indexed positions +
      normals + index). Crease-aware vertex normals (union-find, 30°) keep the rim and
      collar reading as hard edges while the head shades smooth. 3 779 verts / 6 924 tris,
      closed and consistently wound, mesh volume within 0.6 % of the CAD volume.
- [x] **Viewer** — `docs/index.html`, three.js r186 vendored in `docs/vendor/` (no CDN),
      OrbitControls, shadows, grid + table, auto-rotate / reset / wireframe / smooth-toggle,
      HUD read from the mesh. Needs to be served (`uv run python -m http.server 8000`).
- [x] Checks: `uv run pytest -q` → 14 passed; `ruff check` clean on the three pawn files;
      headless-Chrome render confirmed by pixel silhouette against the CAD profile.

## Not yet decided

- Is this lab about the greeting script, or is the script just a placeholder for a real
  MLR/agent assignment? Shapes whether we add tests/CI or keep it minimal.

## Next step

**Publish `docs/` on GitHub Pages — blocked on the user checking the page first.** Nothing
to do until they have looked at it. Once they say go:

```bash
uv run python -m http.server 8000             # http://localhost:8000/docs/  (their check)
gh api repos/256995/mlr-agent-lab/pages -X POST -f "source[branch]=main" -f "source[path]=/docs"
```

Then the page lives at `https://256995.github.io/mlr-agent-lab/` and `README.md` gets the
link. Do not enable it before that go-ahead.

## Not yet decided (other workstream)

**Shape of the dependencies.** `uv add cadquery` landed in the shared `[project]
dependencies` from the pawn work, so every `uv run` in this repo drags ~150 MB of CAD
libraries; `pypdf` and `sympy` came from a third. Proposed:

```bash
uv remove cadquery pypdf sympy
uv add --optional cadquery cadquery==2.8.0
uv run --dev ruff check .                     # must pass repo-wide
```

Confirm before running — it changes how every workstream installs its deps. (Repo-wide
`ruff check .` currently reports 12 findings in `ML_study/`, none in the pawn files.)

## Later

- [ ] One real test around `random_greeting` (seeded choice, greetings valid UTF-8) in `pytest`.
- [ ] Port `snake/check.py`'s shell checks into pytest so there is one entry point.
- [ ] Snake: the five rule modifications the user is choosing between — implement the winner.
- [ ] Decide and record the lab's actual goal in `README.md`.
- [ ] Pawn: real glTF export (needs `cadquery-ocp` ≥ 8 or a trimesh round-trip) so the
      viewer can ship textures; other pieces off the same profile toolkit.
- [ ] Pawn: fit the silhouette against a real Staunton pawn table instead of hand-picked
      spline control points.

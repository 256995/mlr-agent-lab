# RUNS.md

Log of runs in this lab — newest last. One entry per attempt, including failures.
Fields per entry: **date · model (from `/status`) · asked · checked · result.**

> Note on *model*: the agent cannot read `/status` from inside its own session, so this
> field is filled in by the user after `/status`, or left as `?` when unknown. Claude Code
> CLI at setup time: `2.1.299`; `ANTHROPIC_MODEL=agentic` against a custom base URL
> (`llm.ai.e-infra.cz`), so the API alias is not a public model name.

---

## 2026-10-14 · setup

- **Model:** `?` (Claude Code CLI 2.1.299; `/status` not readable from inside the session — please fill in)
- **Asked:** Write `AGENTS.md` with our working rules (read `README.md` + `PLAN.md` first, use uv
  — `uv run`, `uv add`, no global `pip install`, run checks before saying it is done). Make
  `CLAUDE.md` load it. Create `README.md` (goal, how to run), `PLAN.md` (progress, next step),
  `RUNS.md` (model from `/status`, what was asked, how it was checked).
- **Checked:**
  - surveyed the repo first (`ls`, no git repo, only `random_greeting.py`, no config files);
  - `PYTHONUTF8=1 uv run --no-project random_greeting.py` → exit 0, printed a greeting;
  - plain `python random_greeting.py` **and** `uv run random_greeting.py` without `PYTHONUTF8=1`
    → `UnicodeEncodeError: 'charmap' codec ... (cp1250)` on the Czech strings — this is why the
    UTF-8 note is in `AGENTS.md` §3 and `README.md`;
  - `uv init --bare --python 3.13` tested in a throwaway temp copy, not in the repo: produces
    `pyproject.toml` only (no venv, no README), and `uv run` then picks up the system
    CPython 3.13.2 → works. Recorded as step 1 of `PLAN.md` rather than run here.
- **Result:** 5 files created (`AGENTS.md`, `CLAUDE.md`, `README.md`, `PLAN.md`, `RUNS.md`).
  No Python project files, no deps, no git.
- **Open:** `/status` model value; lab's real goal; whether to proceed with `uv init` step 1.

---

## 2026-10-14 · uv + gh install, then git + public repo

- **Model:** `?` (Claude Code CLI 2.1.299; `/status` still not readable from inside the
  session — please fill in)
- **Asked:** Install GitHub CLI and uv without administrator rights into the user folder and
  check both work; then create a public repo `mlr-agent-lab` from this folder, showing what
  would be uploaded before pushing.
- **Checked:**
  - install: both archives matched their published sha256 before extraction
    (`gh 2.102.0` → `ae64e556…`, `uv 0.13.1` → `3b2661a4…`); `cmd.exe` `where gh/uv/uvx`
    resolved them, so they are on the Windows PATH and not just in Git Bash;
    `uv run --python 3.12 python -c …` downloaded a managed CPython 3.12.15 and ran it →
    exit 0. No admin rights used: official `-windows_msvc` zips unpacked into
    `C:\Users\alena\.local\bin`, which was already on the user PATH, so no PATH edit;
  - pre-push: grep sweep for token/private-key/password patterns over all 6 files → clean;
    no `.env`/`.pem`/`.key`/`credentials` files; staged manifest compared against
    `git status --untracked-files=all` so nothing was silently dropped;
    `git check-ignore` confirmed the new `.gitignore` excluded none of the 7 intended files;
  - post-push: `gh api …/git/trees/main?recursive=1` — remote tree byte-identical to the
    local manifest; `gh repo view` → `visibility: PUBLIC`, default branch `main`.
- **Result:** `gh` 2.102.0 and `uv` 0.13.1 installed user-level. Repo live at
  https://github.com/256995/mlr-agent-lab. Commit 1 = the 6 existing files + `.gitignore`
  (7 files, 228 lines). Commit 2 = this doc sync. Commit author email is
  `256995@vutbr.cz`, chosen knowingly.
- **Not checked:** `gh auth status` was verified but `gh api` was not exercised against the
  repo before the push; `uv init` step 1 of `PLAN.md` was *not* run.
- **Open:** `/status` model value; lab's real goal; whether `RUNS.md` should keep naming the
  internal `llm.ai.e-infra.cz` endpoint now that the repo is public.

---

## 2026-10-14 · snake game + its browser harness

- **Model:** `?` (Claude Code CLI 2.1.299 — `/status` is a CLI command, not readable from
  inside the session; please fill in)
- **Asked:** Make a Snake game that runs in the browser as a single HTML file in `snake/`,
  then suggest five unusual rule modifications and implement the one chosen.
- **Checked:**
  - *core rules*, inside a real page (`?selftest=1`, seeded RNG so it never flakes): 18
    assertions — move, 180° rejection, 2-deep turn buffer, grow-by-one on eating, food never
    spawning on the snake, wall death, self-collision, the legal "tail cell just vacated"
    case, pause is a no-op, last-free-cell spawn, win when the board fills, speed floor.
    → `SELFTEST PASS 18/18`;
  - *shell*, `snake/check.py` driving headless Chrome over the DevTools protocol in real
    time: 23 assertions — canvas actually painted, waits for input, key starts/steers, the
    RAF loop advances ticks, tick length, HUD never drifts from state, eating grows, wall
    death + message, restart, best score persists, pause freezes the clock, resume. → 23/23,
    plus two PNGs (live frame, game-over overlay) that were looked at, not just sized;
  - *rule audit*: 300 seeded straight-ahead replays → `over:wall` 300/300 at tick 12
    (no false self-collision), and a tight box-turn sequence stays `running` (the legal
    tail-chasing case);
  - *lint*: `ruff check` clean after fixing 4 findings, `ruff format` applied.
- **Result:** `snake/index.html` (game, zero build step, `file://`-openable),
  `snake/check.py` (harness). Two bugs the harness caught and fixed: the score HUD only
  re-rendered on death, so it sat frozen during play; and my first eat-check placed the
  food behind the snake, which was the harness being wrong, not the game. Two project
  side effects: `pyproject.toml` + `uv.lock` + `.venv` now exist (`uv add --dev websockets`
  created the metadata, so PLAN step 1's `uv init` is moot and `--no-project` is no longer
  needed), and `ruff` is a dev dep.
- **Not checked:** `pytest` is not installed, so the `random_greeting` test still does not
  exist; `ruff check .` was run on `snake/check.py`, not repo-wide (the other workstream's
  `pawn_model.py` is untracked and not mine to lint); the full 23-check suite has not been
  re-run after `ruff format` — only `py_compile` was re-checked, since format is
  whitespace-only.
- **Note for whoever runs this repo:** another session is working in the same folder
  (`ML_study/`, `pawn_model.py`, `_dbg_tmp.py`, `cadquery` in the shared `[project]
  dependencies`). Those are not mine and were not staged, moved, or committed here.
  `README.md` Read calls returned a cached copy while that session edited underneath —
  re-verify shared files on disk before editing them.
- **Open:** which of the five rule modifications to implement; whether `cadquery` moves to
  its own optional extra; `/status` model value.

---

## 2026-10-14 · CadQuery pawn + rotatable web viewer

- **Model:** `?` (Claude Code CLI 2.1.299 — `/status` is a CLI command, not readable from
  inside the session; please fill in)
- **Asked:** Make a chess figure in CadQuery and a web page where I can rotate it in 3D;
  publish the page on GitHub Pages *once I have checked it*. Piece chosen from a menu:
  **pawn** (pure revolve of one profile).
- **Checked:**
  - *CAD*: `PYTHONUTF8=1 uv run pawn_model.py` → exit 0, `valid solid: True`, 638.76 mm³,
    575.88 mm², 7 faces, bbox 11.24 × 11.24 × 23.50 mm, z from −0.00, height/base 2.10.
    `check_profile()` runs first and raises on a disconnected wire, a neck overshooting the
    head sphere, a neck that never pinches, or a shaft rising above the join.
  - *mesh topology/geometry*, `uv run pytest -q` → **14 passed**: single valid solid; one
    closed wire of exactly 8 edges; dims match the spec; sits on z=0; every non-axis
    silhouette edge below the join; neck pinches below the collar; mesh is a closed
    manifold (every edge used exactly twice, no boundary edges, no degenerate faces),
    indices in range, weld actually merges duplicates (the raw OCCT mesh does **not** —
    faces arrive unsplit only after welding), mesh volume within 0.6 % of the CAD volume
    (one-sided, so it cannot exceed it), unit normals, and the crease split measured as an
    actual angle between normals sharing a position (min split at the rim > 45°).
  - *the crease test itself*: mutation-checked by setting `CREASE_ANGLE` to 179° — it failed
    with its intended message ("no base vertex was split"), so it can actually fail.
    Restored to 30°.
  - *lint*: `ruff check` clean on `pawn_model.py`, `export_pawn_mesh.py`, `test_pawn.py`.
  - *the real render*, headless Chrome + SwiftShader on a served `docs/`: module graph
    loaded, WebGL 2.0 context, canvas present, HUD filled from the downloaded mesh
    (`height 23.5 mm · base ∅ 11.2 mm · head ∅ 6.4 mm · volume 639 mm³ · CAD faces 7 ·
    triangles 6,924 · vertices 3,779`), status div `hidden`, and — the check that matters —
    a `readPixels` silhouette measured at 11 heights and compared to the CAD profile
    (11.2 mm wide at the base, 8.2 at the collar, 6.4 at the head, 23.5 mm tall). Screenshot
    looked at, not just sized: base, waist, collar, head and shadow all present.
- **Result:** `pawn_model.py`, `export_pawn_mesh.py`, `test_pawn.py`, `docs/index.html`,
  `docs/pawn.json`, `docs/vendor/` (three.js r186 + OrbitControls, no CDN). GitHub Pages
  **deliberately not enabled** — gated on the user checking the page.
- **Bugs the checks caught** (all mine, all found by a check rather than by eye):
  `Workplane.spline()` starts at its *first listed point*, not the current pen position, so
  concatenated segments produced a disconnected wire → `StdFail_NotDone`; `Edge` has
  `sample()`, not `discretize()`; `Workplane.sphere()` takes `centered=`, and `torus` /
  `Workplane.normal()` do not exist — the sphere lost to a `threePointArc` head; a
  late-binding comprehension in `weld()` (`KeyError`) mangled the index buffer; two of my
  own *validation* rules were wrong (asking the neck to lie on the head circle, then asking
  everything above the ball's south pole to lie inside it) and the corrected version
  immediately caught the neck spline overshooting the ball; `three.module.js` re-exports
  from `./three.core.js`, which I had not vendored → completely blank page with a
  self-explanatory console; and I double-flipped a `readPixels` row index, which made the
  probe's own silhouette look upside down and nearly sent me chasing a nonexistent bug.
  One test was passing vacuously until a forgotten import raised `NameError` — hand-copied
  constants replaced by `BODY_POINTS[-1][0]`.
- **Not checked:** not opened in a real interactive browser (headless SwiftShader only), so
  touch/trackpad feel and real-GPU shading are unverified; `controls.reset()` is only
  confirmed by `saveState()` placement, not by a click; mobile viewport not tested; the
  12 pre-existing `ruff` findings in `ML_study/` are another session's and were left alone.
- **Note for whoever runs this repo:** a parallel session edited `pyproject.toml`
  (`pypdf`, `sympy`, `websockets`), `snake/`, `ML_study/`, `MA/`, `SPEC.md` and all four
  record files while this work was in progress. `cadquery==2.8.0` (pinned `<8.0` for the
  win/cp313 OCP wheels, so 7.9.3.1.1) is the only dep this work added. Nothing outside
  `pawn_model.py` / `export_pawn_mesh.py` / `test_pawn.py` / `docs/` was staged or deleted.
- **Open:** GitHub Pages enable (needs the user's go-ahead); `cadquery` → its own extra;
  `/status` model value.

# mlr-agent-lab

Small lab for working **with** a coding agent on Python: an agent that reads the repo,
follows the rules, runs the code, and leaves a written record of what it did. The
working example is deliberately tiny (`random_greeting.py`) so the process — not the
code — is what gets practiced.

## Start here

| File | What it is |
| --- | --- |
| [`AGENTS.md`](AGENTS.md) | The working rules agents must follow (uv only, run checks before "done"). `CLAUDE.md` imports it. |
| [`PLAN.md`](PLAN.md) | Where we are and the **one** next step. |
| [`RUNS.md`](RUNS.md) | Log of attempts: model, ask, how it was checked, result. |

## Run it

The lab uses [uv](https://docs.astral.sh/uv/) for everything — never a global `pip install`.
`pyproject.toml` + `uv.lock` are committed, so clone and go:

```bash
uv sync --dev                     # once, to create .venv
PYTHONUTF8=1 uv run random_greeting.py
uv add <package>                  # add a runtime dependency
uv add --dev <package>            # add a dev-only tool
uv run --dev ruff check .         # lint
```

`PYTHONUTF8=1` is required on this machine: the sources are UTF-8 (Czech text) and the
console code page is `cp1250`, which raises `UnicodeEncodeError` without it.

### Snake

[`snake/index.html`](snake/index.html) is a complete game in one file — open it
double-clicked, from `file://`, no server or build step needed. Arrow keys / WASD to
steer, <kbd>Space</kbd> pause, <kbd>R</kbd> restart, swipe on touch. Walls and your own
tail are fatal.

It ships with its own checks, because "it loads" is not a test:

```bash
# state-transition rules, run inside the page (works headless or in a normal tab)
start "" "snake/index.html?selftest=1"          # verdict in the tab title

# the real thing driven through Chrome's DevTools protocol: 23 checks on the live
# game (RAF loop, key input, eating, wall death, restart, pause) + PNG screenshots
uv run --dev snake/check.py "file:///$PWD/snake/index.html?selftest=1"
```

`snake/check.py` needs a Chrome/Edge on the usual paths, or `SNAKE_BROWSER=/path/to/browser`.

### Chess pawn in CadQuery + 3D viewer

Two stages — CAD to mesh, then mesh to page. The page never needs CadQuery or a build step.

```bash
PYTHONUTF8=1 uv run pawn_model.py         # build the solid, print volume/bbox
PYTHONUTF8=1 uv run export_pawn_mesh.py   # tessellate -> docs/pawn.json
uv run pytest -q                          # 14 checks on the solid and the mesh
uv run --dev ruff check pawn_model.py export_pawn_mesh.py test_pawn.py
```

Then serve and look at it (a server is required — the page fetches `pawn.json`, and
`file://` blocks that; the page says so on screen if you get it wrong):

```bash
uv run python -m http.server 8000         # then open http://localhost:8000/docs/
```

Drag to orbit, right-drag to pan, wheel to zoom; buttons for auto-rotate, reset, wireframe
and smooth/faceted. `docs/vendor/` holds three.js r186 (incl. `three.core.js`, which
`three.module.js` re-exports from) so there is no CDN dependency. Not published to GitHub
Pages yet — waiting on a look from the user.

## Layout

```
AGENTS.md            working rules (single source of truth)
CLAUDE.md            one-line import of AGENTS.md
README.md            this file
PLAN.md              progress + next step
RUNS.md              run log
random_greeting.py   example script: prints one random greeting
snake/index.html     the browser game (self-contained, no build)
snake/check.py       headless browser checks for the game
pawn_model.py        the pawn as one revolved CadQuery solid (+ construction self-check)
export_pawn_mesh.py  tessellates it and writes docs/pawn.json
test_pawn.py         pytest checks on the solid and on the exported mesh
docs/index.html      three.js viewer for the mesh (needs to be served, not file://)
docs/pawn.json       generated mesh — do not hand-edit, regenerate
docs/vendor/         vendored three.js r186 + OrbitControls
pyproject.toml       deps + Python version (uv)
.gitignore           venv/caches ignored, uv.lock kept
```

## Not set up yet

The greeting script still has no test file (the pawn does: `test_pawn.py`). GitHub Pages
is not enabled. Git is set up: branch `main`, remote `origin`, `.gitignore` in place
(`uv.lock` stays tracked on purpose). See `PLAN.md` for the order.

> Note: `pyproject.toml` currently also carries `cadquery`, `pypdf` and `sympy` as runtime
> dependencies — `cadquery` belongs to the pawn work above, the other two to a separate
> study folder. All three are candidates to move to their own extras. See `PLAN.md`.

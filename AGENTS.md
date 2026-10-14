# AGENTS.md — working rules

Working rules for AI agents (and humans) in this repo. `CLAUDE.md` loads this file;
edit **this** file, not `CLAUDE.md`.

## 1. Read before doing anything

1. `README.md` — what this repo is for and how to run it.
2. `PLAN.md` — what is already done and what the current next step is.
3. `RUNS.md` — recent attempts and how they were verified.

Skim the file you are about to change before editing it. Do not rewrite `README.md`,
`PLAN.md` or `RUNS.md` wholesale — append/update sections.

## 2. Python: uv only

- **Always** `uv run <script.py>` / `uv run pytest` to execute project code.
- Add deps with `uv add <pkg>` (dev-only tools: `uv add --dev <pkg>`).
- **Never** `pip install` into a global / system interpreter, and never `pip install -U`
  outside the project venv. No bare `python script.py` for project code — it bypasses
  the pinned environment.
- One `pyproject.toml` at the repo root is the single source of truth for deps and the
  Python version; `uv.lock` stays committed. (Not created yet — see `PLAN.md`.)

## 3. Windows / UTF-8 (this machine is cp1250)

Source files are UTF-8 and contain non-ASCII text (Czech greetings). The console code
page here is `cp1250`, so printing them raises `UnicodeEncodeError`. Prefix runs with
UTF-8 mode:

```bash
PYTHONUTF8=1 uv run random_greeting.py
```

Keep `# -*- coding: utf-8 -*-`-free plain UTF-8 sources, and do not "fix" this by
escaping the strings.

## 4. Run checks before saying "done"

Nothing counts as done until it has been run in this repo and passed. Required, in order:

| Check | Command |
| --- | --- |
| Code runs | `PYTHONUTF8=1 uv run <entrypoint>` (exit code 0, output looks right) |
| Lint | `uv run --dev ruff check .` (and `ruff format --check .`) |
| Tests | `uv run --dev pytest -q` — once pytest is added (see `PLAN.md`) |
| Browser code | `uv run --dev snake/check.py "<url?selftest=1>"` — real Chrome, exit 0 |
| Docs in sync | `README.md` / `PLAN.md` reflect the change you just made |

Two limits worth knowing, both learned the hard way here:

- The in-page core checks (`?selftest=1`) are cheap and deterministic — but they only
  prove the *pure* logic. The RAF loop, input handling and rendering need the DevTools
  harness: Chrome's `--virtual-time-budget` fires `requestAnimationFrame` once per page,
  so a game loop cannot be exercised without real time over CDP.
- A green check is only as good as its assertion. Two of the snake failures were the
  harness being wrong (food placed behind the snake; score assumed to be exactly 1) and
  one was a real bug (the HUD never re-rendered while playing). When a check fails, work
  out which of the two it is before touching either.

If you did not run it, say so explicitly instead of implying it passed. If a check
fails, report the failing output verbatim. "It should work" is not a check.

## 5. Keep the record straight

- Finish of a step → tick it in `PLAN.md` and add the next step.
- A notable attempt (yours or the user's) → one entry in `RUNS.md`: date, model from
  `/status`, what was asked, how it was checked, result.
- Do not backfill an entry as successful after a later retry — log both runs.

## 6. House rules

- Git is set up (branch `main`, remote `origin` on GitHub). Commit and push **only when
  asked** — the rule against unprompted pushes still stands.
- Ask before deleting or overwriting anything you did not create.
- Match the style of existing code: module docstring, `main() -> None`, type hints,
  English identifiers, natural-language greeting strings as-is.
- Small, verifiable steps over big rewrites.

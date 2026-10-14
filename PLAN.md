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

## Not yet decided

- Is this lab about the greeting script, or is the script just a placeholder for a real
  MLR/agent assignment? Shapes whether we add tests/CI or keep it minimal.

## Next step

**Step 1 — make it a real uv project.** In the repo root:

```bash
uv init --bare --python 3.13
uv add --dev pytest ruff
PYTHONUTF8=1 uv run random_greeting.py   # must still work
uv run ruff check .                      # must pass
uv run pytest -q                         # passes with zero tests collected
```

Commit `pyproject.toml` **and** `uv.lock` (when asked). Then replace the `--no-project`
flag in `README.md` with the normal `uv run` form.

## Later

- [x] ~~`git init` + first commit~~ — done 2026-10-14, repo is public (see `RUNS.md`).
- [ ] One real test around `random_greeting` (e.g. seeded choice, all greetings valid UTF-8).
- [ ] Task runner so checks are one command (`uv run task check` or a `Makefile`).
- [ ] Decide and record the lab's actual goal in `README.md`.

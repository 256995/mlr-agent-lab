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

Right now there is no `pyproject.toml` yet, so run the script without letting uv look for one:

```bash
PYTHONUTF8=1 uv run --no-project random_greeting.py
```

`PYTHONUTF8=1` is required on this machine: the sources are UTF-8 (Czech text) and the
console code page is `cp1250`, which raises `UnicodeEncodeError` without it.

Once `pyproject.toml` exists (step 1 of `PLAN.md`), the workflow is:

```bash
uv init --bare --python 3.13   # first time only
uv add <package>               # add a dependency
PYTHONUTF8=1 uv run random_greeting.py
uv run pytest -q               # once pytest is added
```

## Layout

```
AGENTS.md            working rules (single source of truth)
CLAUDE.md            one-line import of AGENTS.md
README.md            this file
PLAN.md              progress + next step
RUNS.md              run log
random_greeting.py   example script: prints one random greeting
.gitignore           venv/caches ignored, uv.lock kept
```

## Not set up yet

Python project metadata (`pyproject.toml` / `uv.lock` / `.venv`), tests, and linting.
Git is set up: branch `main`, remote `origin`, `.gitignore` in place (`uv.lock` stays
tracked on purpose). See `PLAN.md` for the order.

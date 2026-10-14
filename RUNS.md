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

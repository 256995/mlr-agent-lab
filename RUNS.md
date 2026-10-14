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

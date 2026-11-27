# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

"Spendly" — a Flask expense tracker built incrementally as a teaching project. Most functionality is
intentionally unimplemented: `app.py` carries placeholder routes labelled with the step that will build
them ("coming in Step 3", etc.), and `database/db.py` is a stub containing only a comment describing the
three functions it must eventually export. Treat those markers as the roadmap — when asked to implement a
step, fill in the designated stub rather than restructuring the app.

## Commands

```bash
venv/Scripts/activate          # Windows (bash: source venv/Scripts/activate)
pip install -r requirements.txt
python app.py                  # dev server, debug on, http://127.0.0.1:5001
```

Port 5001 is deliberate (5000 collides with AirPlay on macOS); keep it when adding run instructions.

Tests: `pytest` and `pytest-flask` are pinned in `requirements.txt` but no test suite exists yet. When
adding one, place it in `tests/` and run `pytest tests/test_x.py::test_name` for a single test.

## Architecture

Single-module Flask app — all routing lives in `app.py` with no blueprints, no app factory, and no
extensions (no SQLAlchemy, no Flask-Login). There is no `secret_key` or session wiring yet; authentication
work must add it.

- `app.py` — every route. Template-rendering routes at the top, placeholder stubs below the comment banner.
  `init_db()` and `seed_db()` run at import time inside `app.app_context()`, so the database exists
  before the first request under `python app.py`, `flask run`, or any WSGI server.
- `database/db.py` — the data layer: raw `sqlite3`, no ORM. `get_db()` returns a connection with
  `sqlite3.Row` and `PRAGMA foreign_keys = ON` (per-connection in SQLite, so it must be set on every
  connection, not once at schema creation); `init_db()` creates the `users` and `expenses` tables with
  `CREATE TABLE IF NOT EXISTS`; `seed_db()` inserts a demo user (`demo@spendly.com` / `demo123`,
  scrypt-hashed via `werkzeug.security`) plus 8 sample expenses, returning early if any user exists so
  repeat startups never duplicate. `CATEGORIES` is the canonical seven-category list — import it rather
  than re-typing the values in forms, filters, or validation. `DB_PATH` resolves from `__file__`, so
  `spendly.db` lands in the repo root (gitignored) regardless of the process CWD.

All SQL uses `?` placeholders. Never build a statement with f-strings or `%` formatting.
- `templates/` — Jinja2. `base.html` owns the nav, footer, Google Fonts link, `style.css`, and `main.js`,
  and exposes `title`, `head`, `content`, and `scripts` blocks. Every page extends it; `landing.html` is
  the only one that uses `{% block head %}` to pull in a page-specific stylesheet (`static/css/landing.css`).
- `static/css/style.css` — shared design system used by all pages. `landing.css` is landing-only.
- `static/js/main.js` — empty placeholder loaded globally by `base.html`.

Auth templates (`register.html`, `login.html`) already POST to `/register` and `/login` and render an
`error` variable, but those routes are currently GET-only — implementing auth means adding
`methods=["GET", "POST"]` and passing `error` back into the template, not rewriting the forms.

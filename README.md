# Portfolio — Setup (Step 1)

Run these on your own machine, inside the `portfolio/` folder.

## 1. Create a virtual environment

A venv keeps this project's Python packages separate from your system Python
(and from other projects) — avoids version conflicts.

```bash
python3 -m venv venv
source venv/bin/activate      # you'll see (venv) appear in your prompt
```

## 2. Install dependencies

```bash
pip install -r requirements.txt
```

## 3. Set up your .env file

```bash
cp .env.example .env
```

Then open `.env` and set a real SECRET_KEY (instructions are in the file).

## 4. Run the server

```bash
uvicorn app.main:app --reload
```

- `app.main` = the file `app/main.py`
- `:app` = the FastAPI instance inside it, `app = FastAPI(...)`
- `--reload` = auto-restarts the server whenever you save a file (dev only, never use in production)

## 5. Check it worked

Open these in your browser:

- **http://127.0.0.1:8000** → should show `{"message": "Portfolio backend is alive"}`
- **http://127.0.0.1:8000/api/projects** → should show `[]` (empty list — no projects yet)
- **http://127.0.0.1:8000/docs** → FastAPI's auto-generated interactive API documentation.
  This is one of the best things about FastAPI — every route you write
  automatically shows up here, testable from the browser.

A file `portfolio.db` will appear in your folder — that's your actual SQLite
database, created automatically from the models in `app/models.py`.

## What each file does, in one line

| File | Purpose |
|---|---|
| `app/database.py` | Connects SQLAlchemy to the database (SQLite now, Postgres later) |
| `app/models.py` | Defines your SQL tables as Python classes |
| `app/main.py` | The actual running app — routes live here (will be split into `routers/` soon) |
| `requirements.txt` | List of Python packages this project needs |
| `.env` | Secrets and config — never commit this to git |

## Step 2: Migrations + real data

Now that you've confirmed Step 1 works, pull the updated files and do this:

```bash
source venv/bin/activate
pip install -r requirements.txt      # picks up python-dotenv if missing
cp .env.example .env                 # if you don't already have one

# Apply the migration — creates all 4 tables properly, tracked by Alembic
alembic upgrade head

# Insert real project/skill data
python -m app.seed
```

Then run the server as before:

```bash
uvicorn app.main:app --reload
```

Visit **http://127.0.0.1:8000/api/projects** — you should now see your real
projects (Magic Laundry LMS, the customer app, your trading toolkit) as JSON,
pulled live from the database.

### What Alembic actually did

- `alembic revision --autogenerate -m "..."` compared `app/models.py`
  against the (empty) database and wrote a migration file in
  `alembic/versions/` describing exactly what to create.
- `alembic upgrade head` executed that file, actually building the tables.
- From now on, **any time you change `models.py`** (add a column, add a
  table), the workflow is always: edit the model → `alembic revision
  --autogenerate -m "describe the change"` → `alembic upgrade head`.
  This is what makes it different from Step 1's `create_all()` — it's
  a trackable history, not a one-shot.

### About `app/seed.py`

I drafted entries for Magic Laundry LMS, the customer app, your trading
toolkit, and this portfolio itself, based on what you've actually built.
**Edit the `projects` list directly** — fix descriptions, add your real
GitHub links (I left them as `None` since I don't have those URLs), swap
in different projects, or add more. Re-running `python -m app.seed` is
safe — it skips anything with a slug that already exists instead of
duplicating rows.

## Step 3: Templates + CSS (the actual website)

```bash
uvicorn app.main:app --reload
```

Now visit **http://127.0.0.1:8000/** — you'll see an actual designed
homepage instead of JSON. Click into a project to see the detail page,
and try submitting the contact form at the bottom (it really saves to
your `messages` table — check with `sqlite3 portfolio.db "select * from
messages;"` after submitting).

### What was added

| File | Purpose |
|---|---|
| `app/templates/base.html` | Shared layout — header, footer, font links. Every page extends this. |
| `app/templates/index.html` | Homepage — hero, project list, skills, contact form |
| `app/templates/project_detail.html` | Individual project page at `/projects/{slug}` |
| `app/static/css/style.css` | All hand-written CSS — no framework |
| `app/routers/public.py` | Routes that render the templates (separate from `main.py` now, keeps things organized) |

### The design direction

I deliberately avoided the generic "AI portfolio" look (centered hero,
gradient blob, purple-to-blue everything). Instead it's built around a
**ledger/receipt aesthetic** — projects are listed as line items, not
cards, with dashed rules like a printed receipt, monospace type (IBM
Plex Mono + IBM Plex Sans), and a rotated "Verified Build" stamp badge
on featured projects. It's grounded in your actual work: you build
billing systems and PAN receipts, so the site looks like one.

All the colors/fonts/spacing live in CSS variables at the top of
`style.css` (`:root { ... }`) — change those and the whole site
re-themes. Nothing here is Bootstrap or Tailwind defaults; every rule
was written for this specific design.

### How routing changed

Notice `main.py` no longer defines `/` directly — it now does
`app.include_router(public.router)`, which pulls in every route defined
in `routers/public.py`. This is the pattern you'll keep using: public
pages go in `routers/public.py`, and in Step 4 the admin panel gets its
own `routers/admin.py`, kept separate and password-protected.

## Next step

Once you've clicked through the homepage, a project detail page, and
submitted the contact form successfully, tell me and we'll move to
**Step 4: the admin panel** — JWT login + forms to add/edit projects
without touching code or redeploying.

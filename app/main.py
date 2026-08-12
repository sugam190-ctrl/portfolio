"""
Entrypoint. Running `uvicorn app.main:app --reload` starts this.

For now this file just:
1. Creates the DB tables if they don't exist (normally Alembic handles this,
   but at the very start it's useful to see it happen automatically)
2. Exposes a couple of test routes so we can confirm FastAPI <-> DB works

We'll replace the "create_all" approach with proper Alembic migrations
in the next step — create_all is fine for a first sanity check, but it
doesn't track schema *changes* over time the way migrations do.
"""

from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app import models
from app.database import engine, get_db, SessionLocal
from app.routers import public, admin
from app.theme import FONT_PRESETS, get_or_create_settings

# Creates all tables defined in models.py, if they don't already exist.
# (Alembic is the real source of truth now — this is just a safety net.)
app = FastAPI(title="Sugam's Portfolio")


@app.middleware("http")
async def inject_site_theme(request: Request, call_next):
    """
    Loads the site's color/font settings once per request and stores
    them on request.state, so base.html can read them on EVERY page
    (homepage, project detail, admin) without every single route
    having to fetch and pass them individually.
    """
    db = SessionLocal()
    try:
        settings = get_or_create_settings(db, models)
        request.state.settings = settings
        request.state.font_preset = FONT_PRESETS[settings.font_pair]
    finally:
        db.close()
    return await call_next(request)


# Serves everything in app/static/ at the URL path /static/...
# e.g. app/static/css/style.css -> http://.../static/css/style.css
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Registers all routes defined in routers/public.py (/, /projects/{slug}, /contact)
app.include_router(public.router)
# Registers all /admin/... routes (login, dashboard, project CRUD, messages)
app.include_router(admin.router)


@app.get("/api/projects")
def list_projects(db: Session = Depends(get_db)):
    """
    Proves the DB round-trip works: fetches all rows from the
    'projects' table. It'll be an empty list right now since we
    haven't inserted anything yet.
    """
    projects = db.query(models.Project).order_by(models.Project.display_order).all()
    return projects


@app.get("/health")
def health():
    return {"status": "ok"}

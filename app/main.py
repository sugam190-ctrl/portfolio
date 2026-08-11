"""
Entrypoint. Running `uvicorn app.main:app --reload` starts this.

Table creation is handled entirely by Alembic migrations
(`alembic upgrade head`) — not by this file. Earlier versions of this
file also called `models.Base.metadata.create_all()` here as a
"safety net," but that caused repeated conflicts with Alembic: it
would silently create tables from whatever `models.py` looked like at
that moment, and Alembic had no way of knowing that had happened,
leading to "table already exists" errors the next time a migration
ran. Alembic alone is now the single source of truth for the schema.
"""

from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app import models
from app.database import engine, get_db, SessionLocal
from app.routers import public, admin
from app.theme import FONT_PRESETS, get_or_create_settings

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

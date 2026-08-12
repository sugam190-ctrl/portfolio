
def _image_url(image):
    if not image:
        return None

    path = getattr(image, "file_path", None)

    if not path:
        path = getattr(image, "image_path", None)

    if not path:
        return None

    # New B2 object key
    if not path.startswith("/static/"):
        try:
            return signed_url(path)
        except B2StorageError:
            return None

    # Legacy local image
    return path

def project_image_url(project):
    return _image_url(project)



from app.storage.b2 import upload_fileobj, delete_object, signed_url, B2StorageError
from datetime import datetime
import random

from fastapi import APIRouter, Depends, Form, Request, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.theme import get_or_create_settings, split_heading

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
templates.env.filters["split_heading"] = split_heading


def pick_random_image(db: Session, slot: str):
    images = (
        db.query(models.SiteImage)
        .filter_by(slot=slot)
        .all()
    )

    if not images:
        return None

    image = random.choice(images)

    return _image_url(image)


@router.get("/")
def homepage(request: Request, sent: bool = False, db: Session = Depends(get_db)):
    projects = db.query(models.Project).order_by(models.Project.display_order).all()
    for project in projects:
        project.image_url = _image_url(project)
    services = db.query(models.Service).order_by(models.Service.display_order).all()
    timeline_items = db.query(models.TimelineItem).order_by(models.TimelineItem.display_order).all()
    settings = get_or_create_settings(db, models)
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "projects": projects,
            "services": services,
            "timeline_items": timeline_items,
            "settings": settings,
            "sent": sent,
            "sent_time": datetime.now().strftime("%H:%M"),
            # Picked independently so the hero photo and the contact
            # photo can show two different photos from the same pool.
            "hero_photo": pick_random_image(db, "profile"),
            "connect_photo": pick_random_image(db, "profile"),
        },
    )


@router.get("/projects/{slug}")
def project_detail(slug: str, request: Request, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.slug == slug).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    project.image_url = _image_url(project)
    return templates.TemplateResponse(
        "project_detail.html", {"request": request, "project": project}
    )


@router.post("/contact")
def submit_contact(
    name: str = Form(...),
    email: str = Form(...),
    message: str = Form(...),
    db: Session = Depends(get_db),
):
    """
    Saves the contact form into the 'messages' table instead of just
    emailing you — this is the real backend behavior a static site
    can't do. You'll read these from the admin panel in Step 4.
    """
    db.add(models.Message(name=name, email=email, message=message))
    db.commit()
    # Redirect back to the homepage with ?sent=1 so the success box shows.
    # This is the Post/Redirect/Get pattern — prevents a page refresh
    # from re-submitting the form.
    return RedirectResponse(url="/?sent=1#contact", status_code=303)

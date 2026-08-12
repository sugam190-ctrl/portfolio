import os

from fastapi import APIRouter, Depends, Form, Request, HTTPException, File, UploadFile
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.auth import verify_password, create_access_token, get_current_admin
from app.theme import FONT_PRESETS, ICONS, get_or_create_settings
from app.storage import save_uploaded_image, delete_uploaded_file

router = APIRouter(prefix="/admin")
templates = Jinja2Templates(directory="app/templates")


# ---------- Login / logout ----------

@router.get("/login")
def login_form(request: Request, error: bool = False):
    return templates.TemplateResponse(
        "admin/login.html", {"request": request, "error": error}
    )


@router.post("/login")
def login_submit(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(models.AdminUser).filter_by(username=username).first()
    if not user or not verify_password(password, user.hashed_password):
        return RedirectResponse(url="/admin/login?error=1", status_code=303)

    token = create_access_token({"sub": user.username})
    response = RedirectResponse(url="/admin", status_code=303)
    response.set_cookie(
        key="admin_token", value=token, httponly=True,
        max_age=60 * 60 * 12, samesite="lax",
    )
    return response


@router.get("/logout")
def logout():
    response = RedirectResponse(url="/admin/login", status_code=303)
    response.delete_cookie("admin_token")
    return response


# ---------- Dashboard ----------

@router.get("")
def dashboard(
    request: Request,
    admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    projects = db.query(models.Project).order_by(models.Project.display_order).all()
    unread_count = db.query(models.Message).filter_by(is_read=False).count()
    return templates.TemplateResponse(
        "admin/dashboard.html",
        {"request": request, "projects": projects, "admin": admin, "unread_count": unread_count},
    )


# ---------- Project create/edit/delete ----------

@router.get("/projects/new")
def new_project_form(request: Request, admin: str = Depends(get_current_admin)):
    return templates.TemplateResponse(
        "admin/project_form.html", {"request": request, "project": None}
    )


@router.post("/projects/new")
async def create_project(
    title: str = Form(...),
    slug: str = Form(...),
    short_description: str = Form(...),
    full_description: str = Form(""),
    tech_stack: str = Form(""),
    github_url: str = Form(""),
    live_url: str = Form(""),
    featured: bool = Form(False),
    display_order: int = Form(0),
    photo: UploadFile = File(None),
    admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    image_path = None
    if photo and photo.filename:
        image_path = await save_uploaded_image(photo)

    db.add(models.Project(
        title=title, slug=slug, short_description=short_description,
        full_description=full_description or None,
        tech_stack=tech_stack or None,
        github_url=github_url or None,
        live_url=live_url or None,
        featured=featured, display_order=display_order,
        image_path=image_path,
    ))
    db.commit()
    return RedirectResponse(url="/admin", status_code=303)


@router.get("/projects/{project_id}/edit")
def edit_project_form(
    project_id: int,
    request: Request,
    admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    project = db.get(models.Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return templates.TemplateResponse(
        "admin/project_form.html", {"request": request, "project": project}
    )


@router.post("/projects/{project_id}/edit")
async def update_project(
    project_id: int,
    title: str = Form(...),
    slug: str = Form(...),
    short_description: str = Form(...),
    full_description: str = Form(""),
    tech_stack: str = Form(""),
    github_url: str = Form(""),
    live_url: str = Form(""),
    featured: bool = Form(False),
    display_order: int = Form(0),
    photo: UploadFile = File(None),
    remove_photo: bool = Form(False),
    admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    project = db.get(models.Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    project.title = title
    project.slug = slug
    project.short_description = short_description
    project.full_description = full_description or None
    project.tech_stack = tech_stack or None
    project.github_url = github_url or None
    project.live_url = live_url or None
    project.featured = featured
    project.display_order = display_order

    if photo and photo.filename:
        if project.image_path:
            delete_uploaded_file(project.image_path)
        project.image_path = await save_uploaded_image(photo)
    elif remove_photo and project.image_path:
        delete_uploaded_file(project.image_path)
        project.image_path = None

    db.commit()
    return RedirectResponse(url="/admin", status_code=303)


@router.post("/projects/{project_id}/delete")
def delete_project(
    project_id: int,
    admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    project = db.get(models.Project, project_id)
    if project:
        db.delete(project)
        db.commit()
    return RedirectResponse(url="/admin", status_code=303)


# ---------- Services (Toolkit) create/edit/delete ----------

@router.get("/services")
def list_services(
    request: Request,
    admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    services = db.query(models.Service).order_by(models.Service.display_order).all()
    return templates.TemplateResponse(
        "admin/services.html", {"request": request, "services": services}
    )


@router.get("/services/new")
def new_service_form(request: Request, admin: str = Depends(get_current_admin)):
    return templates.TemplateResponse(
        "admin/service_form.html", {"request": request, "service": None, "icons": ICONS}
    )


@router.post("/services/new")
def create_service(
    title: str = Form(...),
    description: str = Form(...),
    tags: str = Form(""),
    display_order: int = Form(0),
    admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    db.add(models.Service(title=title, description=description, tags=tags, display_order=display_order))
    db.commit()
    return RedirectResponse(url="/admin/services", status_code=303)


@router.get("/services/{service_id}/edit")
def edit_service_form(
    service_id: int,
    request: Request,
    admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    service = db.get(models.Service, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return templates.TemplateResponse(
        "admin/service_form.html", {"request": request, "service": service, "icons": ICONS}
    )


@router.post("/services/{service_id}/edit")
def update_service(
    service_id: int,
    title: str = Form(...),
    description: str = Form(...),
    tags: str = Form(""),
    display_order: int = Form(0),
    admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    service = db.get(models.Service, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    service.title = title
    service.description = description
    service.tags = tags
    service.display_order = display_order
    db.commit()
    return RedirectResponse(url="/admin/services", status_code=303)


@router.post("/services/{service_id}/delete")
def delete_service(
    service_id: int,
    admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    service = db.get(models.Service, service_id)
    if service:
        db.delete(service)
        db.commit()
    return RedirectResponse(url="/admin/services", status_code=303)


# ---------- Timeline (Journey) create/edit/delete ----------

@router.get("/timeline")
def list_timeline(
    request: Request,
    admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    items = db.query(models.TimelineItem).order_by(models.TimelineItem.display_order).all()
    return templates.TemplateResponse(
        "admin/timeline.html", {"request": request, "items": items}
    )


@router.get("/timeline/new")
def new_timeline_form(request: Request, admin: str = Depends(get_current_admin)):
    return templates.TemplateResponse(
        "admin/timeline_form.html", {"request": request, "item": None}
    )


@router.post("/timeline/new")
def create_timeline_item(
    label: str = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    display_order: int = Form(0),
    admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    db.add(models.TimelineItem(label=label, title=title, description=description, display_order=display_order))
    db.commit()
    return RedirectResponse(url="/admin/timeline", status_code=303)


@router.get("/timeline/{item_id}/edit")
def edit_timeline_form(
    item_id: int,
    request: Request,
    admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    item = db.get(models.TimelineItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Timeline item not found")
    return templates.TemplateResponse(
        "admin/timeline_form.html", {"request": request, "item": item}
    )


@router.post("/timeline/{item_id}/edit")
def update_timeline_item(
    item_id: int,
    label: str = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    display_order: int = Form(0),
    admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    item = db.get(models.TimelineItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Timeline item not found")
    item.label = label
    item.title = title
    item.description = description
    item.display_order = display_order
    db.commit()
    return RedirectResponse(url="/admin/timeline", status_code=303)


@router.post("/timeline/{item_id}/delete")
def delete_timeline_item(
    item_id: int,
    admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    item = db.get(models.TimelineItem, item_id)
    if item:
        db.delete(item)
        db.commit()
    return RedirectResponse(url="/admin/timeline", status_code=303)


# ---------- Messages inbox ----------

@router.get("/messages")
def list_messages(
    request: Request,
    admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    messages = db.query(models.Message).order_by(models.Message.created_at.desc()).all()
    return templates.TemplateResponse(
        "admin/messages.html", {"request": request, "messages": messages}
    )


# ---------- Site settings (everything else) ----------

@router.get("/settings")
def settings_form(
    request: Request,
    admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    settings = get_or_create_settings(db, models)
    return templates.TemplateResponse(
        "admin/settings.html",
        {"request": request, "settings": settings, "font_presets": FONT_PRESETS},
    )


@router.post("/settings")
async def settings_update(
    request: Request,
    admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    Uses the raw form dict instead of individually-typed parameters —
    there are ~35 fields here, nearly all plain strings, and this
    keeps the route from becoming an unreadable wall of arguments.
    Checkboxes are handled explicitly since unchecked boxes send
    nothing at all.
    """
    form = await request.form()
    settings = get_or_create_settings(db, models)

    text_fields = [
        "bg_color", "ink_color", "accent_color", "font_pair", "font_scale",
        "hero_eyebrow", "availability_label", "hero_first_name", "hero_last_name",
        "hero_description", "hero_badges", "photo_stamp_text", "hero_scribble",
        "marquee_skills",
        "about_statement", "about_paragraph", "about_focus", "about_status",
        "skills_heading", "skills_intro",
        "work_heading", "work_intro",
        "journey_heading", "journey_note",
        "ai_heading", "ai_note",
        "contact_eyebrow", "contact_heading",
        "contact_email", "contact_phone", "contact_location",
        "social_github", "social_linkedin", "social_instagram", "social_x",
    ]
    for field in text_fields:
        if field in form:
            setattr(settings, field, form[field])

    # Only accept known preset keys — never let arbitrary text into font_pair
    if settings.font_pair not in FONT_PRESETS:
        settings.font_pair = "grotesk"

    settings.available_for_work = "available_for_work" in form

    db.commit()
    return RedirectResponse(url="/admin/settings?saved=1", status_code=303)


# ---------- Site images (photo slots) ----------

@router.get("/images")
def images_page(
    request: Request,
    admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    profile_images = db.query(models.SiteImage).filter_by(slot="profile").order_by(models.SiteImage.uploaded_at.desc()).all()
    work_images = db.query(models.SiteImage).filter_by(slot="work").order_by(models.SiteImage.uploaded_at.desc()).all()
    return templates.TemplateResponse(
        "admin/images.html",
        {"request": request, "profile_images": profile_images, "work_images": work_images},
    )


@router.post("/images/upload")
async def upload_image(
    slot: str = Form(...),
    file: UploadFile = File(...),
    admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    if slot not in ("profile", "work"):
        raise HTTPException(status_code=400, detail="Invalid slot")

    file_path = await save_uploaded_image(file)
    db.add(models.SiteImage(slot=slot, file_path=file_path))
    db.commit()
    return RedirectResponse(url="/admin/images", status_code=303)


@router.post("/images/{image_id}/delete")
def delete_image(
    image_id: int,
    admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    image = db.get(models.SiteImage, image_id)
    if image:
        delete_uploaded_file(image.file_path)
        db.delete(image)
        db.commit()
    return RedirectResponse(url="/admin/images", status_code=303)

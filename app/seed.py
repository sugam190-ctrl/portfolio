"""
Run this once (or whenever you want to reset sample data) to populate
the database with real content.

Usage:
    python -m app.seed
"""

import os
from app.database import SessionLocal
from app import models
from app.auth import hash_password

projects = [
    {
        "title": "Magic Laundry — Laundry Management System",
        "slug": "magic-laundry-lms",
        "short_description": "Full admin panel for a real laundry business: billing, cash register, expenses, and customer management.",
        "full_description": (
            "Built an end-to-end admin panel for Magic Laundry & Dry Cleaning, "
            "handling Bikram Sambat date conversion, PAN-compliant billing, a "
            "cash register with denomination tracking, expense and purchase "
            "logging with invoice uploads, and full customer management."
        ),
        "tech_stack": "Firebase, Firestore, JavaScript, HTML/CSS, jsPDF",
        "github_url": None,
        "live_url": "https://magiclaundry.com.np",
        "image_path": None,
        "featured": True,
        "display_order": 1,
    },
    {
        "title": "Trading Platform Concept",
        "slug": "trading-platform-concept",
        "short_description": "A product concept inspired by what traders actually need: journaling, analytics, paper trading, and better decision-making.",
        "full_description": (
            "An exploration of the tools active traders rely on — trade "
            "journaling, session analytics, paper trading, and structured "
            "decision-making — approached as a real product design problem, "
            "not just a script."
        ),
        "tech_stack": "Python, Product Design, UX",
        "github_url": None,
        "live_url": None,
        "image_path": None,
        "featured": False,
        "display_order": 2,
    },
    {
        "title": "This Portfolio",
        "slug": "portfolio-site",
        "short_description": "This site — a FastAPI + SQLAlchemy + PostgreSQL backend, fully manageable through a custom admin panel.",
        "full_description": (
            "Server-rendered portfolio built on FastAPI with a proper SQL "
            "backend: SQLAlchemy models, Alembic migrations, and a "
            "JWT-protected admin panel that manages every piece of content "
            "on the site."
        ),
        "tech_stack": "FastAPI, SQLAlchemy, PostgreSQL, Alembic, Jinja2",
        "github_url": None,
        "live_url": None,
        "image_path": None,
        "featured": True,
        "display_order": 3,
    },
]

services = [
    {
        "title": "Frontend",
        "description": "HTML, CSS, JavaScript, responsive interfaces, animations and UI experiments.",
        "tags": "HTML, CSS, JS, UI/UX",
        "display_order": 1,
    },
    {
        "title": "Programming",
        "description": "Python and JavaScript for practical tools, automation and product prototypes.",
        "tags": "PYTHON, JS, LOGIC",
        "display_order": 2,
    },
    {
        "title": "Networking",
        "description": "CCNA-focused networking, TCP/IP, OSI, subnetting, switching and Linux environments.",
        "tags": "CCNA, TCP/IP, LINUX",
        "display_order": 3,
    },
    {
        "title": "AI-assisted building",
        "description": "Using AI as a development partner for research, prototyping, debugging, design and iteration.",
        "tags": "AI, PROMPTING, PROTOTYPING",
        "display_order": 4,
    },
]

timeline_items = [
    {
        "label": "NOW",
        "title": "Building & experimenting",
        "description": "Working on practical web projects, product ideas and improving technical foundations.",
        "display_order": 1,
    },
    {
        "label": "01",
        "title": "Networking / CCNA",
        "description": "Studying networking fundamentals including switching, subnetting, TCP/IP and Linux environments.",
        "display_order": 2,
    },
    {
        "label": "02",
        "title": "Markets & trading",
        "description": "Exploring market structure, trading systems, journaling and technology around active trading.",
        "display_order": 3,
    },
    {
        "label": "03",
        "title": "Startup thinking",
        "description": "Looking for real problems in Nepal and turning useful ideas into testable products.",
        "display_order": 4,
    },
]


def seed():
    db = SessionLocal()
    try:
        for p in projects:
            if not db.query(models.Project).filter_by(slug=p["slug"]).first():
                db.add(models.Project(**p))

        for s in services:
            if not db.query(models.Service).filter_by(title=s["title"]).first():
                db.add(models.Service(**s))

        for t in timeline_items:
            if not db.query(models.TimelineItem).filter_by(title=t["title"]).first():
                db.add(models.TimelineItem(**t))

        admin_username = os.getenv("ADMIN_USERNAME", "admin")
        admin_password = os.getenv("ADMIN_PASSWORD", "changeme")
        if not db.query(models.AdminUser).filter_by(username=admin_username).first():
            db.add(models.AdminUser(
                username=admin_username,
                hashed_password=hash_password(admin_password),
            ))
            print(f"Created admin user '{admin_username}'.")

        db.commit()
        print(f"Seeded {len(projects)} projects, {len(services)} services, {len(timeline_items)} timeline items.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()

"""
Each class here = one SQL table. SQLAlchemy turns these into actual
CREATE TABLE statements when we run Alembic migrations.

This is the same schema we planned out, just written as Python.
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, func
from app.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    slug = Column(String(200), unique=True, nullable=False, index=True)  # used in URL: /projects/magic-laundry
    short_description = Column(String(300), nullable=False)
    full_description = Column(Text, nullable=True)
    tech_stack = Column(String(300), nullable=True)  # "FastAPI, PostgreSQL, Docker"
    github_url = Column(String(300), nullable=True)
    live_url = Column(String(300), nullable=True)
    image_path = Column(String(300), nullable=True)
    featured = Column(Boolean, default=False)       # show on homepage?
    display_order = Column(Integer, default=0)       # controls sort order
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)        # "Python"
    category = Column(String(100), nullable=False)     # "Backend"
    proficiency = Column(Integer, default=3)            # 1-5


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    email = Column(String(150), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_read = Column(Boolean, default=False)


class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)


class SiteImage(Base):
    """
    Images the admin uploads to fill photo slots on the homepage.
    'slot' groups images that get randomly swapped in on each page
    load — e.g. multiple 'profile' photos rotate between the hero
    and contact sections, multiple 'work' photos rotate in the
    work-preview box.
    """
    __tablename__ = "site_images"

    id = Column(Integer, primary_key=True, index=True)
    slot = Column(String(50), nullable=False, index=True)  # 'profile' or 'work'
    file_path = Column(String(300), nullable=False)  # e.g. /static/images/uploads/xxxx.jpg
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())


class Service(Base):
    """
    A "toolkit" card shown on the homepage. Fully admin-managed.
    """
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    description = Column(String(300), nullable=False)
    tags = Column(String(200), default="")  # comma-separated, e.g. "HTML, CSS, JS"
    icon_key = Column(String(30), default="code")  # kept for possible future use
    display_order = Column(Integer, default=0)


class TimelineItem(Base):
    """
    A single entry in the "Journey" timeline.
    """
    __tablename__ = "timeline_items"

    id = Column(Integer, primary_key=True, index=True)
    label = Column(String(20), nullable=False)  # e.g. "NOW", "01", "02"
    title = Column(String(150), nullable=False)
    description = Column(String(400), nullable=False)
    display_order = Column(Integer, default=0)


class SiteSettings(Base):
    """
    A single-row table holding every piece of site-wide, admin-editable
    content: theme (colors/fonts) AND every text block on the homepage.
    Always read/written as the one row with id=1.

    Headings that show a two-tone style (upright + italic) use a "|"
    separator: everything before "|" renders upright, everything after
    renders in the italic serif accent. If there's no "|", the whole
    thing renders upright.
    """
    __tablename__ = "site_settings"

    id = Column(Integer, primary_key=True, index=True)

    # Theme
    bg_color = Column(String(20), default="#F3F0E8")
    ink_color = Column(String(20), default="#171717")
    accent_color = Column(String(20), default="#C8FF00")
    font_pair = Column(String(30), default="grotesk")
    font_scale = Column(String(10), default="100")  # percentage: 87.5, 100, 112.5, 125

    # Hero
    hero_eyebrow = Column(String(100), default="✦ AI-ASSISTED PORTFOLIO / 2026")
    availability_label = Column(String(100), default="AVAILABLE FOR OPPORTUNITIES")
    hero_first_name = Column(String(50), default="Sugam")
    hero_last_name = Column(String(50), default="Sapkota")
    hero_description = Column(
        Text,
        default=(
            "I build digital products, experiment with technology, "
            "study networks, and explore ideas that can become real "
            "businesses."
        ),
    )
    hero_badges = Column(String(200), default="DEVELOPER, BUILDER, TRADER, PROBLEM SOLVER")
    photo_stamp_text = Column(String(60), default="BUILT WITH AI ✦")
    hero_scribble = Column(String(100), default="make something real →")
    available_for_work = Column(Boolean, default=True)

    # Marquee ticker
    marquee_skills = Column(
        String(400),
        default="PYTHON, JAVASCRIPT, HTML / CSS, LINUX, NETWORKING, AI TOOLS, PRODUCT THINKING",
    )

    # About
    about_statement = Column(
        Text,
        default=(
            "I don't want to just use technology. I want to understand "
            "it, build with it, and turn ideas into useful products."
        ),
    )
    about_paragraph = Column(
        Text,
        default=(
            "I'm Sugam, an IT-focused builder who enjoys working across "
            "software, networking, markets and small business technology.\n\n"
            "My projects are driven by curiosity: if something feels "
            "inefficient, confusing or outdated, I want to understand why "
            "— and see whether technology can make it better."
        ),
    )
    about_focus = Column(String(80), default="Software + Products")
    about_status = Column(String(80), default="Learning & Building")

    # Section intros
    skills_heading = Column(String(100), default="Things I|work with.")
    skills_intro = Column(
        String(300),
        default="Not a list of buzzwords. These are tools and areas I actively use, study or experiment with.",
    )
    work_heading = Column(String(100), default="Ideas turned|into things.")
    work_intro = Column(String(300), default="A selection of projects and experiments.")
    journey_heading = Column(String(100), default="Still|becoming.")
    journey_note = Column(String(300), default="The goal isn't to look finished. The goal is to keep getting better.")
    ai_heading = Column(String(100), default="Built by a human.|Accelerated by AI.")
    ai_note = Column(
        Text,
        default=(
            "AI tools were used during the design, coding, brainstorming "
            "and iteration of this website. The direction, content, "
            "decisions and final edits are mine."
        ),
    )
    contact_eyebrow = Column(String(60), default="HAVE AN IDEA?")
    contact_heading = Column(String(100), default="Let's make|something.")

    # Contact
    contact_email = Column(String(150), default="sugamsapkota19@gmail.com")
    contact_phone = Column(String(50), default="")
    contact_location = Column(String(150), default="Kavrepalanchok, Nepal")
    social_github = Column(String(300), default="")
    social_linkedin = Column(String(300), default="")
    social_instagram = Column(String(300), default="")
    social_x = Column(String(300), default="")

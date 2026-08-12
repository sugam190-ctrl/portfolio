"""
Font presets the admin picks FROM, rather than free-text — keeps the
site visually consistent. This design uses FOUR font roles:
- display: big bold headlines (Space Grotesk in the original)
- sans: body text, nav, general UI (Manrope)
- mono: small uppercase labels/tags (DM Mono)
- serif: italic accent flourish used inside headings (Georgia)
"""

FONT_PRESETS = {
    "grotesk": {
        "label": "Space Grotesk / Manrope / DM Mono (default)",
        "display": "'Space Grotesk', sans-serif",
        "sans": "'Manrope', Arial, sans-serif",
        "mono": "'DM Mono', monospace",
        "serif": "Georgia, 'Times New Roman', serif",
        "google_fonts_url": "https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap",
    },
    "classic": {
        "label": "Sora / IBM Plex Sans / JetBrains Mono",
        "display": "'Sora', sans-serif",
        "sans": "'IBM Plex Sans', Arial, sans-serif",
        "mono": "'JetBrains Mono', monospace",
        "serif": "Georgia, 'Times New Roman', serif",
        "google_fonts_url": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600;700&family=Sora:wght@500;600;700&display=swap",
    },
}

DEFAULT_FONT_KEY = "grotesk"

# Kept for the admin Service form (not currently rendered on the
# homepage in this design, which uses numbered labels instead).
ICONS = {
    "code": {"label": "Code (</>)", "svg": '<path d="M11 9L4 16l7 7M21 9l7 7-7 7M18 6l-4 20"/>'},
    "database": {"label": "Database", "svg": '<ellipse cx="16" cy="8" rx="10" ry="3.5"/>'},
    "gear": {"label": "Systems", "svg": '<circle cx="16" cy="16" r="4.5"/>'},
}

DEFAULT_ICON_KEY = "code"


def get_or_create_settings(db, models):
    """
    Settings are always a single row. Create it with defaults the
    first time anything asks for it.
    """
    settings = db.query(models.SiteSettings).first()
    if not settings:
        settings = models.SiteSettings()
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


def split_heading(text):
    """
    Splits a "Normal part|Italic part" heading string into
    (upright, italic). If there's no "|", the whole thing is upright
    and the italic part is empty.
    """
    if not text:
        return "", ""
    if "|" in text:
        upright, italic = text.split("|", 1)
        return upright.strip(), italic.strip()
    return text.strip(), ""

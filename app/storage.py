"""
Handles saving, serving, and deleting uploaded images.

In production, images go to Backblaze B2 — object storage that
persists independently of your web server, unlike Render's local
disk (which gets wiped every time the free-tier service sleeps and
wakes back up). B2's free tier (10GB, forever) requires no credit
card at all, unlike some competitors.

The bucket stays PRIVATE (which avoids B2's card-required step for
public buckets) — instead, this app serves images itself through the
/media/{filename} route in routers/public.py, fetching from B2
server-side using the app's own credentials. Visitors never talk to
B2 directly.

If B2 isn't configured (no credentials in .env), uploads fall back to
local disk under app/static/images/uploads/ — this keeps local
development simple, since you don't need a B2 account just to test
uploads on your own machine. Only production needs B2 configured.
"""

import os
import uuid

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
LOCAL_UPLOAD_DIR = "app/static/images/uploads"

B2_KEY_ID = os.getenv("B2_KEY_ID")
B2_APPLICATION_KEY = os.getenv("B2_APPLICATION_KEY")
B2_BUCKET_NAME = os.getenv("B2_BUCKET_NAME")
B2_ENDPOINT_URL = os.getenv("B2_ENDPOINT_URL")  # e.g. https://s3.us-west-004.backblazeb2.com


def b2_configured() -> bool:
    return all([B2_KEY_ID, B2_APPLICATION_KEY, B2_BUCKET_NAME, B2_ENDPOINT_URL])


def _b2_client():
    import boto3

    return boto3.client(
        "s3",
        endpoint_url=B2_ENDPOINT_URL,
        aws_access_key_id=B2_KEY_ID,
        aws_secret_access_key=B2_APPLICATION_KEY,
    )


async def save_uploaded_image(file) -> str:
    """
    Validates and saves an uploaded image. Returns the URL to store in
    the database — either our own /media/ route (B2-backed) or a local
    /static/ path.
    """
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Unsupported file type")

    new_filename = f"{uuid.uuid4().hex}{ext}"
    contents = await file.read()

    if b2_configured():
        client = _b2_client()
        client.put_object(
            Bucket=B2_BUCKET_NAME,
            Key=new_filename,
            Body=contents,
            ContentType=file.content_type or "application/octet-stream",
        )
        return f"/media/{new_filename}"

    # Local fallback — fine for dev, NOT persistent on Render's free tier
    os.makedirs(LOCAL_UPLOAD_DIR, exist_ok=True)
    dest_path = os.path.join(LOCAL_UPLOAD_DIR, new_filename)
    with open(dest_path, "wb") as f:
        f.write(contents)
    return f"/static/images/uploads/{new_filename}"


def get_b2_object(key: str):
    """
    Fetches an object's bytes + content type from B2, for the
    /media/{filename} route to stream back to the visitor. Raises if
    not found — the route turns that into a 404.
    """
    client = _b2_client()
    obj = client.get_object(Bucket=B2_BUCKET_NAME, Key=key)
    return obj["Body"].read(), obj.get("ContentType", "application/octet-stream")


def delete_uploaded_file(file_path: str) -> None:
    """
    Best-effort delete — works whether file_path is a /media/ (B2) URL
    or a local /static/ path. Never raises; a failed cleanup shouldn't
    block the actual database update.
    """
    if not file_path:
        return
    try:
        if b2_configured() and file_path.startswith("/media/"):
            key = file_path[len("/media/"):]
            _b2_client().delete_object(Bucket=B2_BUCKET_NAME, Key=key)
        elif file_path.startswith("/static/"):
            local_path = "app" + file_path
            if os.path.exists(local_path):
                os.remove(local_path)
    except Exception:
        pass

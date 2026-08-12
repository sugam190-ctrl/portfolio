import mimetypes
import os
from typing import BinaryIO

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError


class B2StorageError(RuntimeError):
    """Raised when a B2 storage operation fails."""


def _settings():
    required = {
        "B2_KEY_ID": os.getenv("B2_KEY_ID"),
        "B2_APPLICATION_KEY": os.getenv("B2_APPLICATION_KEY"),
        "B2_BUCKET_NAME": os.getenv("B2_BUCKET_NAME"),
        "B2_ENDPOINT": os.getenv("B2_ENDPOINT"),
        "B2_REGION": os.getenv("B2_REGION"),
    }
    missing = [k for k, v in required.items() if not v]
    if missing:
        raise B2StorageError(
            "Missing B2 environment variables: " + ", ".join(missing)
        )
    return required


def _client():
    s = _settings()
    return boto3.client(
        "s3",
        endpoint_url=s["B2_ENDPOINT"],
        region_name=s["B2_REGION"],
        aws_access_key_id=s["B2_KEY_ID"],
        aws_secret_access_key=s["B2_APPLICATION_KEY"],
        config=Config(signature_version="s3v4"),
    )


def upload_fileobj(fileobj: BinaryIO, object_key: str, content_type: str | None = None):
    s = _settings()
    content_type = content_type or mimetypes.guess_type(object_key)[0] or "application/octet-stream"
    try:
        _client().upload_fileobj(
            fileobj,
            s["B2_BUCKET_NAME"],
            object_key,
            ExtraArgs={"ContentType": content_type},
        )
    except (BotoCoreError, ClientError) as exc:
        raise B2StorageError(f"B2 upload failed: {exc}") from exc


def delete_object(object_key: str):
    s = _settings()
    try:
        _client().delete_object(Bucket=s["B2_BUCKET_NAME"], Key=object_key)
    except (BotoCoreError, ClientError) as exc:
        raise B2StorageError(f"B2 delete failed: {exc}") from exc


def signed_url(object_key: str, expires: int | None = None) -> str:
    s = _settings()
    expires = expires or int(os.getenv("B2_SIGNED_URL_EXPIRES", "3600"))
    try:
        return _client().generate_presigned_url(
            "get_object",
            Params={"Bucket": s["B2_BUCKET_NAME"], "Key": object_key},
            ExpiresIn=expires,
        )
    except (BotoCoreError, ClientError) as exc:
        raise B2StorageError(f"B2 signed URL generation failed: {exc}") from exc

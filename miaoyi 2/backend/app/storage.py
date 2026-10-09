import uuid

import boto3

from .config import settings


def configured() -> bool:
    return bool(settings.r2_endpoint and settings.r2_access_key_id and settings.r2_secret_access_key)


def upload_image(data: bytes, content_type: str, user_id: str) -> str:
    """Stores an upload in Cloudflare R2 (S3 compatible) and returns its object key."""
    s3 = boto3.client(
        "s3",
        endpoint_url=settings.r2_endpoint,
        aws_access_key_id=settings.r2_access_key_id,
        aws_secret_access_key=settings.r2_secret_access_key,
        region_name="auto",
    )
    key = f"scans/{user_id}/{uuid.uuid4().hex}"
    s3.put_object(Bucket=settings.r2_bucket, Key=key, Body=data, ContentType=content_type)
    return key

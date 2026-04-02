import boto3
from botocore.client import Config
import os
from dotenv import load_dotenv 

load_dotenv()
MINIO_ROOT_USER = os.getenv("MINIO_ROOT_USER")
MINIO_ROOT_PASSWORD = os.getenv("MINIO_ROOT_PASSWORD")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "attachments")
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")

s3_client = boto3.client(
    "s3",
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=MINIO_ROOT_USER,
    aws_secret_access_key=MINIO_ROOT_PASSWORD,
    config=Config(signature_version="s3v4", region_name="us-east-1"),
)


def ensure_bucker_exists():
    try:
        s3_client.head_bucket(Bucket=MINIO_BUCKET)
    except Exception:
        s3_client.create_bucket(Bucket=MINIO_BUCKET)


def upload_file(file_bytes: bytes, object_key: str, content_type: str) -> str:
    s3_client.put_object(
        Bucket=MINIO_BUCKET, Key=object_key, Body=file_bytes, ContentType=content_type
    )
    return object_key


def delete_file(object_key: str):
    s3_client.delete_object(Bucket=MINIO_BUCKET, Key=object_key)


def get_presigned_url(object_key: str, expiry: int = 3600) -> str:
    return s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": MINIO_BUCKET, "Key": object_key},
        ExpiresIn=expiry,
    )

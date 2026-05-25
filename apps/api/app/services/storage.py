from dataclasses import dataclass
from io import BytesIO
from typing import BinaryIO

import boto3
from botocore.client import Config

from app.core.config import settings


@dataclass(frozen=True)
class StoredObject:
    key: str
    bucket: str


class ObjectStorage:
    """S3-compatible storage adapter.

    MinIO is used locally; the same code works with AWS S3 in production.
    """

    def __init__(self) -> None:
        self._client = boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint_url,
            aws_access_key_id=settings.s3_access_key_id,
            aws_secret_access_key=settings.s3_secret_access_key,
            region_name=settings.s3_region,
            config=Config(signature_version="s3v4"),
        )

    def upload_fileobj(self, fileobj: BinaryIO, key: str, content_type: str) -> StoredObject:
        self._client.upload_fileobj(
            fileobj,
            settings.s3_bucket,
            key,
            ExtraArgs={"ContentType": content_type},
        )
        return StoredObject(key=key, bucket=settings.s3_bucket)

    def upload_bytes(self, payload: bytes, key: str, content_type: str) -> StoredObject:
        return self.upload_fileobj(BytesIO(payload), key, content_type)

    def download_bytes(self, key: str) -> bytes:
        response = self._client.get_object(Bucket=settings.s3_bucket, Key=key)
        body = response["Body"]
        with body:
            return body.read()

    def delete_object(self, key: str) -> None:
        self._client.delete_object(Bucket=settings.s3_bucket, Key=key)


def get_object_storage() -> ObjectStorage:
    return ObjectStorage()

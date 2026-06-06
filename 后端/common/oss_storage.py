from io import BytesIO

import oss2
from django.conf import settings
from django.core.files.base import File
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible


@deconstructible
class AliyunOssStorage(Storage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.access_key_id = getattr(settings, "OSS_ACCESS_KEY_ID", "")
        self.access_key_secret = getattr(settings, "OSS_ACCESS_KEY_SECRET", "")
        self.bucket_name = getattr(settings, "OSS_BUCKET_NAME", "")
        self.endpoint = getattr(settings, "OSS_ENDPOINT", "")
        self.cname = getattr(settings, "OSS_CNAME", "")

    @property
    def bucket(self):
        endpoint = self.endpoint or ""
        if endpoint and not endpoint.startswith("http"):
            endpoint = f"https://{endpoint}"
        auth = oss2.Auth(self.access_key_id, self.access_key_secret)
        return oss2.Bucket(auth, endpoint, self.bucket_name)

    def _normalize_name(self, name):
        return str(name or "").replace("\\", "/").lstrip("/")

    def _save(self, name, content):
        name = self.get_available_name(self._normalize_name(name))
        if hasattr(content, "seek"):
            content.seek(0)
        self.bucket.put_object(name, content.read())
        return name

    def _open(self, name, mode="rb"):
        normalized_name = self._normalize_name(name)
        result = self.bucket.get_object(normalized_name)
        return File(BytesIO(result.read()), name=normalized_name)

    def delete(self, name):
        normalized_name = self._normalize_name(name)
        if normalized_name:
            self.bucket.delete_object(normalized_name)

    def exists(self, name):
        normalized_name = self._normalize_name(name)
        if not normalized_name:
            return False
        return self.bucket.object_exists(normalized_name)

    def size(self, name):
        normalized_name = self._normalize_name(name)
        headers = self.bucket.get_object_meta(normalized_name).headers
        return int(headers.get("Content-Length", 0))

    def url(self, name):
        normalized_name = self._normalize_name(name)
        if self.cname:
            return f"https://{self.cname}/{normalized_name}"
        return f"https://{self.bucket_name}.{self.endpoint}/{normalized_name}"

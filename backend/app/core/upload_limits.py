"""Parse bodies only after authorization, with actual streamed byte bounds."""

from collections.abc import AsyncGenerator, AsyncIterator
from contextlib import asynccontextmanager

from fastapi import Request
from starlette.datastructures import UploadFile
from starlette.formparsers import MultiPartException, MultiPartParser

from app.api.voice_schemas import voice_error
from app.core.config import Settings


async def bounded_stream(request: Request, maximum: int) -> AsyncGenerator[bytes, None]:
    count = 0
    async for chunk in request.stream():
        count += len(chunk)
        if count > maximum:
            raise voice_error(413, "request_too_large", "Request exceeds the upload limit")
        for start in range(0, len(chunk), 65536):
            yield chunk[start : start + 65536]


class BoundedParser(MultiPartParser):
    """Also bound multipart headers/file bytes before the parser spools them."""

    header_bytes = 0
    file_bytes = 0
    complete = False
    limit = 0

    def on_header_field(self, data: bytes, start: int, end: int) -> None:
        self.header_bytes += end - start
        if self.header_bytes > 8192:
            raise MultiPartException("Headers too large")
        super().on_header_field(data, start, end)

    def on_header_value(self, data: bytes, start: int, end: int) -> None:
        self.header_bytes += end - start
        if self.header_bytes > 8192:
            raise MultiPartException("Headers too large")
        super().on_header_value(data, start, end)

    def on_part_data(self, data: bytes, start: int, end: int) -> None:
        self.file_bytes += end - start
        if self.file_bytes > self.limit:
            raise voice_error(413, "upload_too_large", "Audio exceeds the upload limit")
        super().on_part_data(data, start, end)

    def on_end(self) -> None:
        self.complete = True
        super().on_end()


@asynccontextmanager
async def audio_upload(request: Request, settings: Settings) -> AsyncIterator[UploadFile]:
    content_type = request.headers.get("content-type", "")
    if not content_type.startswith("multipart/form-data;") or len(content_type) > 512:
        raise voice_error(422, "invalid_upload", "Upload one audio file")
    parser = BoundedParser(
        request.headers,
        bounded_stream(request, settings.audio_max_request_bytes),
        max_files=1,
        max_fields=0,
    )
    parser.limit = settings.audio_max_upload_bytes
    try:
        form = await parser.parse()
        uploaded = form.get("file")
        if not parser.complete or len(form) != 1 or not isinstance(uploaded, UploadFile):
            raise voice_error(422, "invalid_upload", "Upload one complete audio file")
        yield uploaded
    except MultiPartException:
        raise voice_error(422, "invalid_upload", "Upload one complete audio file") from None
    finally:
        # Starlette closes these only on MultiPartException; also close on limits/cancellation.
        for file in parser._files_to_close_on_error:
            file.close()

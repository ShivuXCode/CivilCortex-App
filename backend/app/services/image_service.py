import os
import uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException
from app.services.storage_service import storage_service

MAX_IMAGE_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

# Magic-byte signatures for image validation
# Protects against content-type spoofing (Fix #5)
_MAGIC_BYTES: dict[bytes, str] = {
    b"\xff\xd8\xff": "image/jpeg",
    b"\x89PNG": "image/png",
    b"RIFF": "image/webp",  # WEBP files start with RIFF....WEBP
}


def _validate_magic_bytes(header: bytes, claimed_type: str) -> bool:
    """Return True if the file's magic bytes match the claimed content type."""
    for signature, mime in _MAGIC_BYTES.items():
        if header.startswith(signature):
            # WEBP extra check: bytes 8-11 must be 'WEBP'
            if mime == "image/webp":
                return len(header) >= 12 and header[8:12] == b"WEBP" and claimed_type == "image/webp"
            return mime == claimed_type
    return False


class ImageService:
    @staticmethod
    def save_image(file: UploadFile, inspection_id: str) -> dict:
        if file.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(status_code=400, detail="Invalid image type")

        ext = os.path.splitext(file.filename or "")[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail="Invalid file extension")

        # --- Robust size check: read stream directly, do NOT trust file.size ---
        # file.size is None in many Starlette versions, making a conditional check
        # dangerously bypassable. Seeking to end gives the real byte count.
        file.file.seek(0, os.SEEK_END)
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to start before reading content

        if file_size > MAX_IMAGE_SIZE_BYTES:
            raise HTTPException(status_code=413, detail=f"File too large. Maximum allowed size is 20 MB.")

        # --- Magic-byte validation: reject content-type spoofing (Fix #5) ---
        header = file.file.read(12)
        file.file.seek(0)  # Reset again for upload
        if not _validate_magic_bytes(header, file.content_type):
            raise HTTPException(
                status_code=400,
                detail="File content does not match the declared content type. Possible spoofing attempt."
            )

        unique_name = f"{uuid.uuid4()}{ext}"
        object_key = f"inspections/{inspection_id}/images/{unique_name}"
        
        try:
            storage_service.upload_file(file.file, object_key, file_size, file.content_type)
        except Exception as e:
            raise HTTPException(status_code=500, detail="Failed to upload image to storage")
            
        return {
            "object_key": object_key,
            "original_filename": file.filename,
            "mime_type": file.content_type,
            "file_size": file_size
        }

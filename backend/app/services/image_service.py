import os
import uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException
from app.services.storage_service import storage_service

class ImageService:
    @staticmethod
    def save_image(file: UploadFile, inspection_id: str) -> dict:
        allowed_types = ["image/jpeg", "image/png", "image/webp"]
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Invalid image type")
        
        # Check size (if possible via file.size, depends on Starlette version)
        if file.size and file.size > 20 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large")
            
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
            raise HTTPException(status_code=400, detail="Invalid extension")

        unique_name = f"{uuid.uuid4()}{ext}"
        object_key = f"inspections/{inspection_id}/images/{unique_name}"
        
        # Ensure we are at the beginning of the file
        file.file.seek(0, os.SEEK_END)
        file_size = file.file.tell()
        file.file.seek(0)
        
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

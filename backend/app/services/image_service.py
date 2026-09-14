import os
import shutil
import uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException
from app.core.config import settings

class ImageService:
    @staticmethod
    def save_image(file: UploadFile) -> dict:
        allowed_types = ["image/jpeg", "image/png", "image/webp"]
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Invalid image type")
        
        # Check size (if possible via file.size, depends on Starlette version)
        if file.size and file.size > 20 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large")
            
        ext = os.path.splitext(file.filename)[1]
        unique_name = f"{uuid.uuid4()}{ext}"
        
        # Determine path from ROOT/storage/images
        # Since backend is in backend/ and ROOT is parent, let's resolve relative to backend if needed
        # Or just use the absolute configured path if it's relative to the project root where app is run
        # We assume the FastAPI app is run from `backend` directory, but the user requested:
        # "storage/images/ at the PROJECT ROOT"
        # We'll calculate the project root relative to this file
        project_root = Path(__file__).parent.parent.parent.parent
        storage_dir = project_root / settings.STORAGE_ROOT
        storage_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = storage_dir / unique_name
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        return {
            "file_path": str(file_path.resolve()),
            "original_filename": file.filename,
            "mime_type": file.content_type,
            "file_size": file.size or os.path.getsize(file_path)
        }

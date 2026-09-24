import sys
import os
sys.path.insert(0, os.path.abspath('backend'))
import glob
images = glob.glob("backend/storage/images/*.jpg")
from app.services.ml_service import MLService

if images:
    res = MLService.analyze_image(images[0])
    print(res)

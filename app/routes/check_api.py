from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from app.face_detection.face_detection import detect_face
from app.quality_check.quality_check import detect_blurriness
from app.face_detection.image_processing import save_image
import logging
import os
from dotenv import load_dotenv
# Set up secure logging
logger = logging.getLogger(__name__)

load_dotenv()

router = APIRouter()

@router.post("/check-quality")
async def check_quality_api(image: UploadFile = File(...)):

    try:
        # Save the uploaded image
        image_path = save_image(image)
        logger.info(f"Image saved at: {image_path}")

        # Check if the file path is secure and valid
        if not os.path.exists(image_path):
            logger.error(f"Image not found at: {image_path}")
            raise HTTPException(status_code=404, detail="Image not found")

        # Detect face in the image
        if not detect_face(image_path):
            logger.warning(f"Face not detected in the image: {image_path}")
            return JSONResponse(content={"success": False, "message": "Face not detected"})
        
        # Check image blurriness
        if not detect_blurriness(image_path):
            logger.warning(f"Image quality is poor for: {image_path}")
            return JSONResponse(content={"success": False, "message": "Image quality is poor"})

        logger.info(f"Image passed quality check: {image_path}")
        return JSONResponse(content={"success": True, "image_url": image_path.replace("app", os.getenv('BASE_URL'), 1), "image_path": image_path})

    except HTTPException as e:
        logger.error(f"HTTPException: {str(e.detail)}")
        raise e

    except Exception as e:
        logger.error(f"An error occurred during image quality check: {str(e)}")
        raise HTTPException(status_code=400, detail="An error occurred while processing the image.")

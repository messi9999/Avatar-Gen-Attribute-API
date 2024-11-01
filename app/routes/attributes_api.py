from fastapi import APIRouter, HTTPException, Form, Request
from fastapi.responses import JSONResponse
from app.skin_tone_detection.skin_tone_detection import detect_skin_tone
from app.hair_color_detection.hair_color_detection import detect_hair_color
from app.eye_color_detection.eye_color_detection import detect_eye_color
from app.schemas.schemas import AttributesRequest
import os
import logging
from urllib.parse import urlparse, unquote

# Set up secure logging
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/detect-attributes")
async def detect_attributes(request: AttributesRequest):
    try:            
        if not os.path.exists(request.image_path):
            logger.error(f"Image not found: {request.image_path}")
            raise HTTPException(status_code=404, detail="Image not found")

        # Perform attribute detections securely
        skin_tone = detect_skin_tone(
                image_path=request.image_path,
                color_type=request.color_type,
                group_name=request.group_name
            )
        hair_color = detect_hair_color(request.image_path)
        eye_color = detect_eye_color(request.image_path)

        result = {
            "skin_tone": skin_tone,
            "hair_color": hair_color,
            "eye_color": eye_color
        }
        
        return JSONResponse(content={"success": True, "data": result})

    except HTTPException as e:
        logger.error(f"HTTPException: {str(e.detail)}")
        raise e
    
    except Exception as e:
        logger.error(f"An error occurred while processing the image: {str(e)}")
        raise HTTPException(status_code=500, detail="An internal error occurred while processing the image.")

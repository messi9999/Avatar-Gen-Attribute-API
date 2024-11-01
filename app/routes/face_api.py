from fastapi import APIRouter, HTTPException, Form, Request
from fastapi.responses import JSONResponse
import logging

from app.schemas.schemas import ChangSkinToneRequest
from app.skin_tone_detection.skin_tone_detection import detect_skin_tone
from app.skin_tone_transfer import skin_tone_change
from app.utils import utils
from app.schemas.schemas import AttributesRequest

import os

from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/detect_skin_tone")
async def detect_skin_tone_api(request: AttributesRequest):
    if not os.path.exists(request.image_path):
        logger.error(f"Image not found: {request.image_path}")
        raise HTTPException(status_code=404, detail="Image not found")
    
    try:
        skin_tone = detect_skin_tone(
                    image_path=request.image_path,
                    color_type=request.color_type,
                )
        result = {
            "skin_tone": skin_tone
        }    
        
        return JSONResponse(content={"success": True, "data": result})
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        return JSONResponse(content={"success": False, "error": str(e)}, status_code=500)


@router.post("/change_skin_tone")
async def change_skin_tone(request: ChangSkinToneRequest):
    try:
        result_path = "app/static/results/" + utils.generate_secure_random_image_name(extension='.png')
        output_path = skin_tone_change.execute(which="color", img=request.image_path, col=utils.hex_to_rgb(request.target_color), res=result_path)
        image_url = output_path.replace("app", os.getenv('BASE_URL'), 1)
        return JSONResponse(content={"success": True, "image_url": image_url, "image_path": output_path})
    except Exception as e:
        logger.error(f"An error occurred during skin tone change: {str(e)}")
        return JSONResponse(content={"success": False, "error": str(e)}, status_code=500)

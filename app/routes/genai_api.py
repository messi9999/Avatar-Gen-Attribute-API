from fastapi import APIRouter, HTTPException, Form, Request
from fastapi.responses import JSONResponse
import logging

from app.schemas.schemas import GenImageRequest
from app.image_generation import generate
import os
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/generate-image")
async def generate_image_api(request: GenImageRequest):
    prompt=request.prompt
    output_path = generate.run(image_url=request.image_path, prompt=prompt)
    
    return JSONResponse(content={"success": True, "image_url": output_path.replace("app", os.getenv('BASE_URL'), 1), "image_path": output_path})


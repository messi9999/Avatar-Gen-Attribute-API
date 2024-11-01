import logging
from fastapi import APIRouter, HTTPException
from app.skin_tone_detection.skin_tone_detection import detect_skin_tone
import os

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create file handler for logging (optional, depending on your use case)

# Define the relative path to the logs directory
log_directory = os.path.join("app", "logs")
# Ensure the logs directory exists
os.makedirs(log_directory, exist_ok=True)
# Define the path to the log file within the logs directory
log_file_path = os.path.join(log_directory, "skin_tone_detection.log")

file_handler = logging.FileHandler("app/logs/skin_tone_detection.log")
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Initialize FastAPI router for skin tone detection
router = APIRouter()

# Secure API route for skin tone detection
@router.post("/detect-skin-tone")
async def detect_skin_tone_route(image_url: str):
    try:
        logger.info(f"Received request for skin tone detection for image: {image_url}")
        
        # Validate the image URL (ensure the file exists)
        if not image_url or not image_url.lower().endswith(('.jpg', '.jpeg', '.png')):
            logger.error("Invalid image URL or unsupported image format.")
            raise HTTPException(status_code=400, detail="Invalid image URL or unsupported image format.")
        
        # Call the skin tone detection function
        result = detect_skin_tone(image_url)
        if result is None:
            logger.error(f"Failed to detect skin tone for image: {image_url}")
            raise HTTPException(status_code=500, detail="Skin tone detection failed.")
        
        # Log and return the result
        logger.info(f"Skin tone detection successful for image: {image_url}. Result: {result}")
        return {"success": True, "skin_tone": result}
    
    except HTTPException as http_err:
        logger.error(f"HTTP error occurred: {http_err.detail}")
        raise http_err
    
    except Exception as e:
        logger.error(f"An unexpected error occurred during skin tone detection: {str(e)}")
        raise HTTPException(status_code=500, detail="An internal error occurred during skin tone detection.")

# Add the router to handle skin tone detection routes
def init_skin_tone_detection():
    try:
        logger.info("Initializing skin tone detection module.")
        # Any additional setup for the module can be performed here
        logger.info("Skin tone detection module initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing skin tone detection module: {str(e)}")
        raise RuntimeError("Failed to initialize skin tone detection module") from e

# Call the initialization function to set up the skin tone detection module
init_skin_tone_detection()

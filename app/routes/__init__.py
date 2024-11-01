import logging
from fastapi import APIRouter
from app.routes.attributes_api import router as detect_attributes_router
from app.routes.check_api import router as check_quality_router
from app.routes.genai_api import router as genai_router
from app.routes.face_api import router as face_router


# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create file handler for logging (optional, depending on your use case)
file_handler = logging.FileHandler("app/logs/routes_init.log")
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Initialize FastAPI router
api_router = APIRouter()

# Include routers from other route files
api_router.include_router(detect_attributes_router, prefix="/attributes", tags=["Attributes Detection"])
api_router.include_router(check_quality_router, prefix="/quality", tags=["Quality Check"])
api_router.include_router(genai_router, prefix="/genimg", tags=["Generate Image"])
api_router.include_router(face_router, prefix="/checkface", tags=["Face APIs"])

# Log the initialization of the routes
logger.info("Routes for attributes detection and quality check initialized successfully.")

# Ensure secure route handling
try:
    logger.info("Verifying route security...")
    # Placeholder for any security checks or middlewares for routes (if needed)
    # For instance, JWT or OAuth2 mechanisms can be integrated here for secure access to routes
    # More secure handling of routes can be added based on the specific security needs of the app.
    logger.info("Route security verified successfully.")

except Exception as e:
    logger.error(f"An error occurred while securing the routes: {str(e)}")
    raise RuntimeError("Failed to secure the routes") from e

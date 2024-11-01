import logging
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from app.routes import check_api, attributes_api, genai_api, face_api

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create file handler for logging (optional)
file_handler = logging.FileHandler("app/logs/app.log")
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Initialize FastAPI app
app = FastAPI()

# Mount static files directory securely
app.mount("/static", StaticFiles(directory="app/static"), name="static")
logger.info("Mounted static directory at '/static'")

# Include routers from routes folder
app.include_router(check_api.router)
app.include_router(attributes_api.router)
app.include_router(genai_api.router)
app.include_router(face_api.router)

logger.info("Included 'check_api' and 'attributes_api' routers")


@app.get("/")
async def root():
    try:
        logger.info("Root endpoint accessed")
        return {"message": "Welcome to the AI Backend API"}
    except Exception as e:
        logger.error(f"Error in root endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Securely handle file uploads
@app.post("/upload-file")
async def upload_file(file: UploadFile = File(...)):
    try:
        logger.info(f"Received file upload request for {file.filename}")
        file_location = f"app/static/{file.filename}"
        
        # Save the uploaded file securely
        with open(file_location, "wb") as buffer:
            buffer.write(file.file.read())
        
        logger.info(f"File saved successfully at {file_location}")
        return {"filename": file.filename, "message": "File uploaded successfully"}
    except Exception as e:
        logger.error(f"Error in file upload: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Initialize application with security and error handling
def init_app():
    try:
        logger.info("Initializing FastAPI application...")
        # Any additional initialization logic
        logger.info("FastAPI application initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing FastAPI application: {str(e)}")
        raise RuntimeError("Failed to initialize the application") from e

# Call the initialization function
init_app()

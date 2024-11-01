import os
import uuid
import logging
from fastapi import UploadFile, HTTPException
from typing import List

# Set up logging
logging.basicConfig(level=logging.INFO)

# Allowed image extensions to prevent malicious file uploads
ALLOWED_EXTENSIONS = [".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff"]

# Directory to save uploaded images
IMAGE_DIRECTORY = "app/static/images/"

# Ensure the image directory exists
if not os.path.exists(IMAGE_DIRECTORY):
    os.makedirs(IMAGE_DIRECTORY)

def generate_unique_filename(original_filename: str) -> str:
    """
    Generates a unique filename using UUID to avoid conflicts and includes the original file extension.
    """
    # Extract the file extension from the original filename
    _, extension = os.path.splitext(original_filename.lower())

    # Check if the extension is allowed (to prevent uploading malicious files)
    if extension not in ALLOWED_EXTENSIONS:
        logging.error(f"File type {extension} is not allowed.")
        raise HTTPException(status_code=400, detail="File type not allowed")

    # Generate a unique UUID for the file
    unique_id = uuid.uuid4()

    # Combine the unique ID with the original file extension
    unique_filename = f"{unique_id}{extension}"

    return unique_filename

def save_image(image: UploadFile) -> str:
    """
    Saves the uploaded image file to the server, and returns the file path. 
    Ensures that only valid images are processed.
    """
    try:
        # Validate the file size (example: restrict to max 5MB for security)
        MAX_FILE_SIZE_MB = 5
        if image.file._file.tell() > MAX_FILE_SIZE_MB * 1024 * 1024:
            logging.error("Uploaded file exceeds the maximum allowed size of 5MB.")
            raise HTTPException(status_code=400, detail="File too large")

        # Generate a safe and unique filename
        filename = generate_unique_filename(image.filename)

        # Define the path to save the image
        image_path = os.path.join(IMAGE_DIRECTORY, filename)

        # Save the file to the specified path
        with open(image_path, "wb") as buffer:
            buffer.write(image.file.read())

        logging.info(f"Image successfully saved to {image_path}")

        return image_path

    except Exception as e:
        logging.error(f"Error saving image: {e}")
        raise HTTPException(status_code=500, detail="Error saving image")

import cv2
import os
import logging

# Set up secure logging
logger = logging.getLogger(__name__)

def detect_blurriness(image_path):
    """
    Detects the blurriness of an image by calculating the variance of the Laplacian.
    
    Args:
        image_path (str): The path to the image file.

    Returns:
        bool: True if the image is not blurry, False if it is blurry.

    Raises:
        ValueError: If the image file cannot be read or the path is invalid.
    """
    # Validate that the file exists and is accessible
    if not os.path.isfile(image_path):
        logger.error(f"File not found: {image_path}")
        raise ValueError(f"File not found: {image_path}")

    # Read the image in grayscale mode
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        logger.error(f"Unable to read the image file: {image_path}")
        raise ValueError(f"Unable to read the image file: {image_path}")

    # Calculate the variance of the Laplacian to detect blurriness
    variance_of_laplacian = cv2.Laplacian(image, cv2.CV_64F).var()
    logger.info(f"Variance of Laplacian: {variance_of_laplacian}")

    # Blurriness threshold
    blur_threshold = 100
    if variance_of_laplacian < blur_threshold:
        logger.info(f"Image is blurry: {image_path}")
        return False
    else:
        logger.info(f"Image is not blurry: {image_path}")
        return True

# # Example usage with error handling and logging
# if __name__ == "__main__":
#     path = 'app/static/images/Screenshot_11.png'
#     try:
#         result = detect_blurriness(path)
#         if result:
#             logger.info("Image passed the blurriness test.")
#         else:
#             logger.info("Image failed the blurriness test.")
#     except ValueError as e:
#         logger.error(f"Error during quality check: {e}")

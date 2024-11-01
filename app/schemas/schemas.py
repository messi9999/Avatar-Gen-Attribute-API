from pydantic import BaseModel, HttpUrl, ValidationError
import logging

# Set up secure logging
logger = logging.getLogger(__name__)

class ImageRequest(BaseModel):
    image_url: HttpUrl  # Use HttpUrl for stricter validation of URL formats
    image_path: str

    @classmethod
    def validate_image_url(cls, url: str):
        """
        Validates the provided image URL.
        Args:
            url (str): The URL of the image.
        Returns:
            ImageRequest: Validated ImageRequest instance.
        Raises:
            ValueError: If the URL is not valid or does not point to an image.
        """
        try:
            request = cls(image_url=url)
            if not cls.is_valid_image_url(url):
                raise ValueError(f"URL does not point to a valid image: {url}")
            return request
        except ValidationError as e:
            logger.error(f"Validation error for URL {url}: {e}")
            raise ValueError(f"Invalid URL provided: {url}")

    @staticmethod
    def is_valid_image_url(url: str) -> bool:
        """
        Check if the URL points to an image by verifying the file extension.
        Args:
            url (str): The URL of the image.
        Returns:
            bool: True if URL points to an image, False otherwise.
        """
        valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')
        return url.lower().endswith(valid_extensions)



class GenImageRequest(BaseModel):
    image_url: HttpUrl  # Use HttpUrl for stricter validation of URL formats
    image_path: str
    prompt: str    

class AttributesRequest(BaseModel):
    image_url: HttpUrl
    image_path: str
    color_type: str



class ChangSkinToneRequest(BaseModel):
    image_url: HttpUrl
    image_path: str
    target_color: str
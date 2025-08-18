import logging
from pathlib import Path
import random
from src.config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

def classify_car_image(image_path: str | Path) -> str:
    """
    Dummy function to simulate car body type detection from an image.
    Returns a random car body type from ['Sedan', 'SUV', 'Truck'].
    Args:
        image_path (str | Path): Path to the car image.
    Returns:
        str: Random car body type ('Sedan', 'SUV', or 'Truck').
    """
    try:
        image_path = str(Path(image_path))
        logger.info(f"Simulating car body type detection for image: {image_path}")

        # Randomly select a body type
        body_types = ['Sedan', 'SUV', 'Truck']
        return random.choice(body_types)

    except Exception as e:
        logger.error(f"Error in dummy image classification: {str(e)}")
        return 'Unknown'
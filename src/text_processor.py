from langchain_core.prompts import PromptTemplate
from langchain_core.language_models import BaseLanguageModel

from src.templates import CAR_LISTING_PROMPT
from src.utils import CarListing, sanitize_input
import logging
from dotenv import load_dotenv

from src.logging_config import setup_logging
setup_logging()
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def create_default_car_listing() -> dict:
    """Create a default car listing structure."""
    return {
        "car": {
            "body_type": "unknown",
            "color": "Unknown",
            "brand": "Unknown", 
            "model": "Unknown",
            "manufactured_year": 0,
            "motor_size_cc": 0,
            "tires": {
                "type": "Unknown",
                "manufactured_year": 0
            },
            "windows": "Unknown",
            "notices": [],
            "price": None,
            "estimated_price": {
                "amount": 0.0,
                "currency": "Unknown"
            }
        }
    }

def process_text(description: str,llm:BaseLanguageModel) -> dict:
    """
    Process car description into structured JSON using LangChain and Pydantic.
    Args:
        description (str): User-provided car description.
    Returns:
        dict: JSON with car details or default JSON on error.
    """
    try:
        # Input validation
        if not description or not isinstance(description, str):
            logger.warning("Empty or invalid input provided")
            return create_default_car_listing()

        # Sanitize input
        sanitized_description = sanitize_input(description, max_length=5000, strict_mode=True, log_threats=True)
        if not sanitized_description:
            logger.warning("Input is empty after sanitization")
            return create_default_car_listing()

        logger.info(f"Processing car description with {len(sanitized_description)} characters")

        # Setup parser and chain
        prompt = PromptTemplate(template=CAR_LISTING_PROMPT, input_variables=["description"])
        structured_llm = llm.with_structured_output(CarListing)
        chain = prompt | structured_llm 

        # Process with LangChain
        car_listing = chain.invoke({"description": sanitized_description})
        
        # Convert Pydantic model to dict
        result = car_listing.model_dump()
        logger.info("Successfully processed car listing")
        return result

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return create_default_car_listing()
    
    except Exception as e:
        logger.error(f"Unexpected error processing text: {str(e)}")
        return create_default_car_listing()
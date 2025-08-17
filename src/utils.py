import logging
from datetime import datetime
from pydantic import BaseModel, Field, model_validator
from typing import Optional, List
import re
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Tires(BaseModel):
    type: str = Field(description="Type of tires (e.g., brand-new, used)", default="Unknown")
    manufactured_year: int = Field(description="Year tires were manufactured", default=0, ge=0)  # FIXED: Added ge=0 constraint

class Notice(BaseModel):
    type: str = Field(description="Type of notice (e.g., collision, repair)")
    description: str = Field(description="Details of the notice")

class Price(BaseModel):
    amount: float = Field(description="Price amount", ge=0)
    currency: str = Field(description="Currency code (e.g., L.E, USD, EGP)")

class Car(BaseModel):
    body_type: str = Field(default="unknown", description="Car body type (e.g., sedan, SUV)")
    color: str = Field(description="Car color", default="Unknown")
    brand: str = Field(description="Car manufacturer", default="Unknown")
    model: str = Field(description="Car model", default="Unknown")
    manufactured_year: int = Field(description="Year of manufacture", default=0, ge=1900, le=2030)
    motor_size_cc: int = Field(description="Engine size in cubic centimeters", default=0, ge=0)
    tires: Tires = Field(description="Tire details", default_factory=Tires)
    windows: str = Field(description="Window type (e.g., tinted, electrical)", default="Unknown")
    notices: List[Notice] = Field(description="List of notices (e.g., collisions)", default_factory=list)
    price: Optional[Price] = Field(default=None, description="Explicit price, if provided")
    estimated_price: Optional[Price] = Field(default=None, description="Estimated price, if inferred")

    @model_validator(mode='after')
    def validate_price_fields(self):
        """Ensure exactly one of price or estimated_price is provided."""
        has_price = self.price is not None
        has_estimated_price = self.estimated_price is not None
        
        if not has_price and not has_estimated_price:
            # If no price info available, set estimated_price with default values
            self.estimated_price = Price(amount=0.0, currency="Unknown")
        elif has_price and has_estimated_price:
            # If both are provided, prioritize explicit price
            self.estimated_price = None
            
        return self

class CarListing(BaseModel):
    car: Car = Field(description="Car details")


def sanitize_input(text: str, max_length: int = 2000, strict_mode: bool = False, log_threats: bool = True) -> str:
    """
    Enhanced input sanitization to prevent prompt injection attacks while preserving legitimate content.
    
    Args:
        text (str): Raw user input (car description)
        max_length (int): Maximum allowed input length (default: 2000)
        strict_mode (bool): If True, applies stricter sanitization rules (default: False)
        log_threats (bool): Whether to log detected threats (default: True)
    
    Returns:
        str: Sanitized input text
    """
    
    # High-threat patterns that should always be removed
    HIGH_THREAT_PATTERNS = {
        'instruction_override': [
            r'\bignore\s+(?:all\s+)?(?:previous|above|prior)\s+(?:instructions?|prompts?|rules?)\b',
            r'\bforget\s+(?:everything|all|previous|above)\b',
            r'\bdisregard\s+(?:previous|above|all)\s+(?:instructions?|prompts?)\b',
            r'\boverride\s+(?:system|previous|default)\s+(?:settings?|instructions?|prompts?)\b',
        ],
        'system_manipulation': [
            r'\bsystem\s*:\s*(?:you\s+are|act\s+as|behave\s+like)',
            r'\bassistant\s*:\s*(?:you\s+are|act\s+as)',
            r'\bnow\s+(?:you\s+are|act\s+as|behave\s+like)\s+(?:a\s+)?(?:car\s+dealer|salesperson)',
            r'\bpretend\s+(?:you\s+are|to\s+be)\s+(?:a\s+)?(?:car\s+dealer|salesperson)',
        ],
        'code_injection': [
            r'```\s*(?:python|javascript|sql|bash|sh|cmd)',
            r'<script\b[^>]*>.*?</script>',
            r'<iframe\b[^>]*>.*?</iframe>',
            r'\beval\s*\(',
            r'\bexec\s*\(',
            r'__import__\s*\(',
        ],
        'data_extraction': [
            r'\bprint\s+(?:all\s+)?(?:system\s+)?(?:prompts?|instructions?|data)\b',
            r'\bshow\s+(?:me\s+)?(?:your\s+)?(?:system\s+)?(?:prompts?|instructions?|data)\b',
            r'\breveal\s+(?:your\s+)?(?:system\s+)?(?:prompts?|instructions?)\b',
            r'\bdisplay\s+(?:all\s+)?(?:hidden\s+)?(?:prompts?|instructions?)\b',
        ]
    }
    
    # Medium-threat patterns (only removed in strict mode)
    MEDIUM_THREAT_PATTERNS = {
        'role_confusion': [
            r'\bas\s+(?:a\s+)?(?:car\s+dealer|salesperson|expert),\s*(?:you\s+should|please)',
            r'\byou\s+are\s+now\s+(?:a\s+)?(?:car\s+dealer|salesperson)',
            r'\bchange\s+your\s+role\s+to\b',
        ],
        'context_manipulation': [
            r'\bstart\s+(?:over|new|fresh)\b',
            r'\breset\s+(?:context|conversation|everything)\b',
            r'\bclear\s+(?:previous|all)\s+(?:context|data)\b',
        ],
        #long sequence of unusual formatting characters
        'unusual_formatting': [
            r'={10,}', 
            r'-{10,}',  
            r'\*{10,}', 
            r'#{5,}',   
        ]
    }
    
    # Input validation
    if not isinstance(text, str):
        logger.warning(f"Invalid input type received: {type(text)}")
        return ""
    
    original_length = len(text)
    
    # Cap input length
    if len(text) > max_length:
        text = text[:max_length]
        if log_threats:
            logger.warning(f"Input truncated from {original_length} to {max_length} characters")
    
    threats_detected = []
    cleaned_text = text
    
    # Remove high-threat patterns (always removed)
    for category, patterns in HIGH_THREAT_PATTERNS.items():
        for pattern in patterns:
            matches = list(re.finditer(pattern, cleaned_text, re.IGNORECASE | re.MULTILINE))
            if matches:
                threats_detected.append(f"HIGH: {category}")
                for match in reversed(matches):  # Reverse to maintain indices
                    cleaned_text = cleaned_text[:match.start()] + " " + cleaned_text[match.end():]
    
    # Remove medium-threat patterns (only in strict mode)
    if strict_mode:
        for category, patterns in MEDIUM_THREAT_PATTERNS.items():
            for pattern in patterns:
                matches = list(re.finditer(pattern, cleaned_text, re.IGNORECASE | re.MULTILINE))
                if matches:
                    threats_detected.append(f"MEDIUM: {category}")
                    for match in reversed(matches):
                        cleaned_text = cleaned_text[:match.start()] + " " + cleaned_text[match.end():]
    
    # Log threats if detected
    if log_threats and threats_detected:
        threat_level = "HIGH" if any("HIGH:" in threat for threat in threats_detected) else "MEDIUM"
        logger.warning(f"Threats detected in input - Level: {threat_level}, Count: {len(threats_detected)}")
        for threat in threats_detected:
            logger.debug(f"Threat pattern: {threat}")
        logger.info(f"Input sanitization completed. Original length: {original_length}, Final length: {len(cleaned_text)}")
    
    # Normalize whitespace
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
    
    # Remove leading/trailing whitespace
    cleaned_text = cleaned_text.strip()
    
    return cleaned_text
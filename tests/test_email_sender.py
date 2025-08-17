import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv
from PIL import Image as PILImage
import io

# Adjust the path to import from the src directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.email_sender import send_car_listing_email, format_car_details, create_email_body

# Load environment variables
load_dotenv()

# Configure logging for better output visibility
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_live_email_test():
    """
    Runs a live test to send an actual email with synthetic data.
    """
    logging.info("--- Starting Live Email Test for email_sender.py ---")

    car_data = {
        "car": {
            "brand": "Toyota",
            "model": "Camry",
            "manufactured_year": 2020,
            "body_type": "Sedan",
            "color": "Silver",
            "motor_size_cc": 2500,
            "windows": "Power",
            "tires": {"type": "All-season", "manufactured_year": 2020},
            "price": {"amount": 22000.0, "currency": "USD"},
            "notices": [{"type": "Maintenance", "description": "Needs a new oil change."}]
        }
    }

    # Test 1: format_car_details
    logging.info("\n--- Testing format_car_details ---")
    html_details = format_car_details(car_data)
    print(html_details)
    assert "Toyota" in html_details
    assert "22,000.00 USD" in html_details
    logging.info("format_car_details test passed.")

    # Test 2: create_email_body
    logging.info("\n--- Testing create_email_body ---")
    html_body = create_email_body(car_data, include_photo=True)
    print(html_body)
    assert "<h1>Car Listing</h1>" in html_body
    assert "Photo attached." in html_body
    logging.info("create_email_body test passed.")

    # Test 3: send_car_listing_email
    recipient = "yahiakhalaf6@gmail.com"
    dummy_image_path= "F:/projects/AutoLister360/temp/NewTux.png"

    try:
        logging.info(f"\n--- Attempting to send a live email to {recipient} ---")
        
        success = send_car_listing_email(car_data, recipient, photo_path=dummy_image_path)
        
        # Clean up the file
        if os.path.exists(dummy_image_path):
            os.remove(dummy_image_path)
            logging.info(f"Cleaned up dummy image at {dummy_image_path}")
        
        if success:
            logging.info("Live email test completed successfully. Check your inbox!")
        else:
            logging.error("Live email test failed. Check the logs for details.")

    except Exception as e:
        logging.error(f"An unexpected error occurred during the live test: {e}")

if __name__ == '__main__':
    run_live_email_test()
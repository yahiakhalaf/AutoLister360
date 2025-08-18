import smtplib
import logging
import os
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from pathlib import Path
import mimetypes
from dotenv import load_dotenv
from src.logging_config import setup_logging

# Configure logging
setup_logging()
logger = logging.getLogger(__name__)

load_dotenv()

def get_smtp_config():
    """Get SMTP configuration from environment variables."""
    config = {
        'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
        'smtp_port': int(os.getenv('SMTP_PORT', '587')),
        'username': os.getenv('SMTP_USERNAME'),
        'password': os.getenv('SMTP_PASSWORD')
    }
    if not all(config.values()):
        raise ValueError("Missing SMTP configuration in environment variables.")
    return config


def format_car_details(car_data: dict) -> str:
    """Format car data into a simple HTML string."""
    if not car_data or 'car' not in car_data:
        return "<p>No car information available.</p>"
    
    car = car_data['car']
    html = "<h2>Car Details</h2>\n<ul>\n"
    html += f"<li><b>Brand:</b> {car.get('brand', 'Unknown')}</li>\n"
    html += f"<li><b>Model:</b> {car.get('model', 'Unknown')}</li>\n"
    html += f"<li><b>Manufactured Year:</b> {car.get('manufactured_year', 'Unknown')}</li>\n"
    html += f"<li><b>Body Type:</b> {car.get('body_type', 'Unknown')}</li>\n"
    html += f"<li><b>Color:</b> {car.get('color', 'Unknown')}</li>\n"
    html += f"<li><b>Engine Size:</b> {car.get('motor_size_cc', 0):,} cc</li>\n"
    html += f"<li><b>Windows:</b> {car.get('windows', 'Unknown')}</li>\n"
    
    # Tire information
    tires = car.get('tires', {})
    tire_info = tires.get('type', 'Unknown')
    tire_year = tires.get('manufactured_year', 0)
    if tire_year > 0:
        tire_info += f" (Manufactured Year: {tire_year})"
    html += f"<li><b>Tires:</b> {tire_info}</li>\n"
    
    # Price information
    price = car.get('price')
    estimated_price = car.get('estimated_price', {})
    if price and isinstance(price, dict) and price.get('amount', 0) > 0:
        html += f"<li><b>Price:</b> {price.get('amount', 0):,.2f} {price.get('currency', 'Unknown')}</li>\n"
    elif estimated_price.get('amount', 0) > 0:
        html += f"<li><b>Estimated Price:</b> {estimated_price.get('amount', 0):,.2f} {estimated_price.get('currency', 'Unknown')}</li>\n"
    else:
        html += "<li><b>Price:</b> Contact for details</li>\n"
    
    # Notices
    notices = car.get('notices', [])
    if notices:
        html += "<li><b>Notices:</b><ul>\n"
        for notice in notices:
            if isinstance(notice, dict):
                notice_type = notice.get('type', 'Notice')
                description = notice.get('description', 'No details available')
                html += f"<li>{notice_type}: {description}</li>\n"
            else:
                html += f"<li>{notice}</li>\n"
        html += "</ul></li>\n"
    
    html += "</ul>\n"
    return html


def create_email_body(car_data: dict, include_photo: bool = False) -> str:
    """Create HTML email body."""
    html = f"""
    <html>
    <body style="font-family: Arial; color: #333;">
        <h1>Car Listing</h1>
        <p>Sent on {datetime.now().strftime('%B %d, %Y')}</p>
        {format_car_details(car_data)}
        {"<p>Photo attached.</p>" if include_photo else ""}
        <p>Contact us for more details.</p>
    </body>
    </html>
    """
    return html


def send_car_listing_email(car_data: dict, recipient_email: str, photo_path: str | Path = None) -> bool:
    """Send car listing email with optional photo attachment."""
    try:
        config = get_smtp_config()
        
        if not recipient_email or '@' not in recipient_email:
            logger.error("Invalid recipient email address")
            return False
        
        if not car_data or not isinstance(car_data, dict):
            logger.error("Invalid car data provided")
            return False
        
        # Create email message
        msg = MIMEMultipart()
        msg['From'] = config['username']
        msg['To'] = recipient_email
        # Create subject
        car = car_data.get('car', {})
        brand = car.get('brand', 'Unknown')
        model = car.get('model', 'Unknown')
        subject = f"Car Listing: {brand} {model}"
        msg['Subject'] = subject
        # Add HTML body
        html_body = create_email_body(car_data, include_photo=bool(photo_path))
        msg.attach(MIMEText(html_body, 'html'))

        # Attach image if provided
        if photo_path:
            photo_path = str(Path(photo_path)) 
            if not os.path.exists(photo_path):
                logger.error(f"Image file not found: {photo_path}")
                return False
            
            mime_type, _ = mimetypes.guess_type(photo_path)
            if mime_type is None or not mime_type.startswith('image/'):
                logger.warning(f"Could not guess MIME type for {photo_path}")
                mime_type = 'image/jpeg' 
            
            with open(photo_path, "rb") as f:
                img_data = f.read()
            image = MIMEImage(img_data, name=os.path.basename(photo_path), _subtype=mime_type.split('/')[1])
            msg.attach(image)

        # Send email
        logger.info(f"Connecting to SMTP server: {config['smtp_server']}:{config['smtp_port']}")
        with smtplib.SMTP(config['smtp_server'], config['smtp_port']) as server:
            server.starttls()
            server.login(config['username'], config['password'])
            server.send_message(msg)        
        logger.info(f"Email successfully sent to {recipient_email}")
        return True
    
    except smtplib.SMTPAuthenticationError:
        logger.error("SMTP authentication failed - check username/password")
        return False
    except smtplib.SMTPRecipientsRefused:
        logger.error(f"Recipient email refused: {recipient_email}")
        return False
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending email: {str(e)}")
        return False
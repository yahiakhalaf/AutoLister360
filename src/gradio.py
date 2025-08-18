import gradio as gr
import re
from pathlib import Path
from langchain_google_genai import ChatGoogleGenerativeAI
import uuid
import logging
from src.text_processor import process_text
from src.email_sender import send_car_listing_email
from src.image_classifier import classify_car_image
from src.config import setup_logging, load_config

# Configure logging
setup_logging()
logger = logging.getLogger(__name__)

def initialize_llm():
    """Initialize the LLM with error handling."""
    try:
        config = load_config()
        llm_config = config['llm']
        llm = ChatGoogleGenerativeAI(
            model=llm_config['model'],
            temperature=llm_config['temperature'],
            api_key=llm_config['api_key']
        )
        return llm, "Gemini API configured successfully"
    except Exception as e:
        return None, f"Error initializing LLM: {str(e)}"

def validate_email(email):
    """Enhanced email validation with stricter checks."""
    if not email or not email.strip():
        return False, "Email cannot be empty"

    if len(email) > 254:
        return False, "Email address is too long (max 254 characters)"
    
    pattern = r'^[a-zA-Z0-9][a-zA-Z0-9._%+-]{0,62}[a-zA-Z0-9]@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Invalid email format"
    
    # Check for consecutive dots or leading/trailing dots in local part
    local_part, domain = email.split('@')
    if '..' in local_part or local_part.startswith('.') or local_part.endswith('.'):
        return False, "Invalid local part: consecutive or leading/trailing dots"
    
    # List of common disposable email domains
    disposable_domains = {'mailinator.com', 'tempmail.com', '10minutemail.com'}
    if domain.lower() in disposable_domains:
        return False, "Disposable email addresses are not allowed"
    
    return True, "Valid email"

def process_and_send(car_description, receiver_email, car_image):
    """Main function to process car description and send email."""
    # Initialize LLM
    llm, llm_status = initialize_llm()
    if not llm:
        return llm_status, ""
    
    # Input validation
    if not car_description or not car_description.strip():
        return "Error: Car description is required!", ""
    
    if not receiver_email or not receiver_email.strip():
        return "Error: Receiver email is required!", ""
    
    is_valid_email, email_message = validate_email(receiver_email)
    if not is_valid_email:
        return f"Error: {email_message}", ""
    
    temp_image_path = None
    try:
        car_data = process_text(car_description, llm)
        
        if not car_data or 'car' not in car_data:
            return "Failed to process car description. Please try again.", ""
        
        # Process image if uploaded
        config = load_config()
        temp_dir = Path(config['application']['temp_directory'])
        temp_dir.mkdir(exist_ok=True)
        allowed_formats = config['application']['allowed_image_formats']
        if car_image is not None:
            # Get original image extension (if available) or default to .jpg
            try:
                image_format = car_image.format.lower() if car_image.format else 'jpg'
                extension = f".{image_format}" if image_format in allowed_formats else '.jpg'
            except AttributeError:
                extension = '.jpg'
            
            unique_filename = f"car_image_{uuid.uuid4().hex}{extension}"
            temp_image_path = temp_dir / unique_filename
            car_image.save(temp_image_path)
            
            # Classify image
            detected_body_type = classify_car_image(temp_image_path)
            if detected_body_type and detected_body_type != 'Unknown':
                car_data['car']['body_type'] = detected_body_type
        
        # Send email
        email_sent = send_car_listing_email(car_data=car_data, recipient_email=receiver_email, photo_path=temp_image_path)
        if email_sent:
            car_details = generate_car_details_summary(car_data['car'])
            return "Email sent successfully to: " + receiver_email, car_details
        else:
            return "Failed to send email. Please check your SMTP configuration.", ""
            
    except Exception as e:
        return f"An error occurred: {str(e)}", ""
    finally:
        if temp_image_path and temp_image_path.exists():
                temp_image_path.unlink()

def generate_car_details_summary(car_info):
    """Generate a formatted summary of car details."""
    summary = "## 📋 Processed Car Details\n\n"
    # Basic information
    summary += f"• **Brand:** {car_info.get('brand', 'Unknown')}\n\n"
    summary += f"• **Model:** {car_info.get('model', 'Unknown')}\n\n"
    summary += f"• **Color:** {car_info.get('color', 'Unknown')}\n\n"
    summary += f"• **Engine Size:** {car_info.get('motor_size_cc', 0):,} cc\n\n"
    summary += f"• **Windows:** {car_info.get('windows', 'Unknown')}\n\n"
    # Tire information
    tires = car_info.get('tires', {})
    tire_info = tires.get('type', 'Unknown')
    tire_year = tires.get('manufactured_year', 0)
    if tire_year > 0:
        tire_info += f" (Manufacturing Year: {tire_year})"
    summary += f"• **Tires:** {tire_info}\n\n"
    # Price information
    price = car_info.get('price')
    estimated_price = car_info.get('estimated_price')
    
    if price and price.get('amount', 0) > 0:
        summary += f"• **Price:** {price.get('amount', 0):,.2f} {price.get('currency', 'Unknown')}\n\n"
    elif estimated_price and estimated_price.get('amount', 0) > 0:
        summary += f"• **Estimated Price:** {estimated_price.get('amount', 0):,.2f} {estimated_price.get('currency', 'Unknown')}\n\n"
    else:
        summary += "• **Price:** Contact for details\n\n"
    # Show notices if any
    notices = car_info.get('notices', [])
    if notices:
        summary += "## Important Notices\n\n"
        for i, notice in enumerate(notices, 1):
            if isinstance(notice, dict):
                summary += f"• **{notice.get('type', 'Notice')}:** {notice.get('description', 'No details available')}\n\n"
            else:
                summary += f"• {str(notice)}\n\n"
    return summary

def create_interface():
    """Create and configure the Gradio interface."""
    # Load config for Gradio settings
    config = load_config()
    gradio_config = config['gradio']
    
    # Custom CSS for better styling
    custom_css = """
    .gradio-container {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .gr-button-primary {
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4) !important;
        border: none !important;
        color: white !important;
        font-weight: bold !important;
    }
    .gr-button-primary:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2) !important;
    }
    """
    
    with gr.Blocks(title="AutoLister360", theme=gradio_config['theme'], css=custom_css) as interface:
        
        # Header
        gr.HTML("""
        <div style='text-align: center; padding: 20px; background: linear-gradient(45deg, #FF6B6B, #4ECDC4); border-radius: 10px; margin-bottom: 20px;'>
            <h1 style='color: white; margin: 0; font-size: 2.5em;'>🚗 AutoLister360</h1>
            <p style='color: white; margin: 10px 0 0 0; font-size: 1.2em;'>Automated Car Listing & Email System</p>
        </div>
        """)
        # Main Interface
        with gr.Row():
            with gr.Column(scale=3):
                gr.HTML("<h3>📝 Car Information</h3>")
                
                with gr.Row():
                    with gr.Column():
                        car_description = gr.Textbox(
                            label="Car Description*",
                            placeholder="Enter detailed car description (e.g., 2020 Toyota Camry, red sedan, 50,000 miles, excellent condition, priced at $25,000...)",
                            lines=6
                        )
                        
                        receiver_email = gr.Textbox(
                            label="Receiver Email*",
                            placeholder="recipient@example.com"
                        )
                    
                    with gr.Column():
                        car_image = gr.Image(
                            label="Car Image (Optional) - Upload to detect body type",
                            type="pil"
                        )
                
                process_btn = gr.Button(
                    "🚀 Process and Send",
                    variant="primary",
                    size="lg"
                )
        
        # Output Section
        gr.HTML("<h3>📊 Results</h3>")
        
        with gr.Row():
            email_status = gr.Textbox(
                label="Email Status",
                lines=2,
                interactive=False
            )
        
        car_details_output = gr.Markdown(
            label="Car Details",
            value="",
            visible=True
        )
        
        # Event handler
        process_btn.click(
            fn=process_and_send,
            inputs=[car_description, receiver_email, car_image],
            outputs=[email_status, car_details_output],
            show_progress=True
        )
        
        # Footer
        gr.HTML("""
        <div style='text-align: center; margin-top: 30px; padding: 20px; color: #666; border-top: 1px solid #eee;'>
            <small>AutoLister360 - Automated Car Listing System </small>
        </div>
        """)
    
    return interface

def main():
    """Launch the Gradio application."""
    config = load_config()
    gradio_config = config['gradio']
    interface = create_interface()
    interface.launch(
        share=gradio_config['share'],
        server_name=gradio_config['server_name'],
        server_port=gradio_config['server_port'],
        show_error=True
    )

if __name__ == "__main__":
    main()

Generate a Python project for a car listing application with AI-powered text processing,image classification and email functionality, The project should be modular, secure,and functional.

### Project Overview
The application allows users to input a car description and recipient email via a Gradio interface and optional car image, processes the description into structured JSON using an LLM (Azure OpenAI) and classify the car body type based on the image and sends an email with formatted car details, optionally including the image. 

### Requirements
1. **Project Structure**:
   - Create a modular structure with separate modules for:
     - Gradio-based user interface.
     - Text processing with Azure OpenAI (via LangChain).
     - Email sending with SMTP.
     - Configuration management using a YAML file.
     - Utility functions for data validation and input sanitization.
     - logging the logs for each requrest in one file .
   - manage the dependencies using uv dependency manager.
   

2. **Gradio Interface**:
   - Build a user-friendly interface with:
     - A text area for car description (required).
     - A text box for recipient email (required).
     - An optional image upload for car body type detection.
     - A "Process and Send" button to trigger processing and email sending.
   - Display outputs: email status (text) and formatted car details (markdown).
   - the (description and reciepant email) and image upload is two boxes in one row,the email status is in a row and then following by the details part.
   - uploaded image will be saved in 'temp/' with unique identifier and it will be deleted after sending email.
   

3. **Text Processing**:
   - Process car descriptions into structured JSON using Azure OpenAI (gpt-4o-mini via LangChain).
   - Extract fields: {
  "car": {
    "body_type": "string",
    "color": "string",
    "brand": "string",
    "model": "string",
    "manufactured_year": "integer",
    "motor_size_cc": "integer",
    "tires": {
      "type": "string",
      "manufactured_year": "integer"
    },
    "windows": "string",
    "notices": [
      {
        "type": "string",
        "description": "string"
      }
    ],
    "price": {
      "amount": "number",
      "currency": "string"
    }
  }
}
.
   - Use Pydantic for data validation, ensuring exactly one of `price` or `estimated_price` is provided.
   - Implement input sanitization to block prompt injection (e.g., remove "ignore instructions" patterns).
   - Return default JSON ({
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
    }) on processing failure.

4. **Email Sending**:
   - Send emails via SMTP  with car details in an HTML table.
   - Support optional image attachments .
   - Include error handling for SMTP issues (e.g., authentication).
   - Log email sending status to a file in a `logs/` directory.

5. **Image Classificaiton**:
   - Create a dummy function for image classification to simulate car type detection, enabling future integration with the real CV model.


6. **Utilities**:
   - Define Pydantic model for car data.
   - Implement a sanitization function to remove high-threat patterns (e.g., code injection, system manipulation).

8. **Additional Files**:
   - Create a `README.md` with explanation of the project and  setup instructions (e.g., setting environment variables, running the app).
   - Ensure sensitive data (e.g., API keys, SMTP credentials) uses environment variables.

### Technology Stack
 use the following languages and frameworks
- follow python 3.12.
- langchain.
- uv depencency manager to manage depencencies and run the project.
-  smtplib and any necessary libraries to handle sending emails.
-  gradio for user interface. 
-  pytorch 
### Output
- Generate all files in a `AutoLister360` directory.
- Ensure the project is executable with `uv run python main.py` after setting environment variables.
- Provide clear, concise code with comments explaining key functionality.


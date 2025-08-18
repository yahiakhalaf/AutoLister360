# AutoLister360

### Intelligent Automated Car Listing & Email System

**AutoLister360** is a sophisticated web application that leverages the power of Large Language Models (LLM) to automatically extract structured data from free-text car descriptions. The system intelligently processes unstructured input, generates professional HTML email listings, and includes optional image classification capabilities—all through an intuitive web interface.

## Table of Contents

- [Key Features](#key-features)
- [Project Architecture](#project-architecture)
- [Quick Start](#quick-start)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage Guide](#usage-guide)
  - [Basic Workflow](#basic-workflow)
  - [Input Requirements](#input-requirements)
- [Data Extraction Capabilities](#data-extraction-capabilities)
  - [Basic Information](#basic-information)
  - [Technical Specifications](#technical-specifications)
  - [Financial Information](#financial-information)
  - [Additional Details](#additional-details)
- [Security Features](#security-features)
  - [Input Sanitization](#input-sanitization)
  - [Email Security](#email-security)
- [Logging & Monitoring](#logging--monitoring)
- [Development](#development)
  - [Project Structure](#project-structure)
  - [Key Dependencies](#key-dependencies)
- [Troubleshooting](#troubleshooting)
  - [Common Issues](#common-issues)
  - [Debug Mode](#debug-mode)
- [License](#license)

## Key Features

- **AI-Powered Extraction:** Uses Azure OpenAI GPT-4o-mini to parse unstructured car descriptions and extract structured data (brand, model, year, price, specifications)
- **Modern Web Interface:** Gradio-based responsive interface with real-time processing and beautiful styling
- **Professional Email Generation**: Automatically creates formatted HTML emails with extracted details and image attachments
- **Image Processing:** Upload car photos for automatic body type detection and enhanced listings
- **Security & Reliability:** Advanced input sanitization, email validation, and comprehensive error handling

## Project Architecture

```
autolister360/
├── src/
│   ├── config.py           # Configuration management
│   ├── text_processor.py   # LLM-powered text processing
│   ├── email_sender.py     # Email functionality
│   ├── image_classifier.py # Image classification
│   ├── utils.py           # Data models and utilities
│   ├── templates.py       # LLM prompt templates
│   └── gradio.py          # Web interface
├── config.yaml            # Application configuration
├── pyproject.toml         # Dependencies and project metadata
└── README.md
```

## Quick Start

### Prerequisites

- Python 3.12 or newer
- uv package manager ([installation guide](https://github.com/astral-sh/uv))
- Azure OpenAI account with GPT-4o-mini deployment
- SMTP credentials (Gmail recommended)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yahiakhalaf/AutoLister360.git
   cd autolister360
   ```

2. **Set up virtual environment and install dependencies:**
   ```bash
   # Create virtual environment
   uv venv
   
   # Activate virtual environment
   # On Linux/macOS:
   source .venv/bin/activate
   
   # On Windows (Command Prompt):
   .venv\Scripts\activate
   
   # On Windows (PowerShell):
   .venv\Scripts\Activate.ps1
   
   # Install dependencies
   uv sync
   ```

3. **Configure environment variables:**
   
   Create a `.env` file in the root directory:
   ```ini
   # SMTP Configuration (Gmail example)
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   
   # Azure OpenAI Configuration
   AZURE_DEPLOYMENT_ENDPOINT=https://your-resource-name.openai.azure.com/
   AZURE_DEPLOYMENT_NAME=your-deployment-name
   AZURE_OPENAI_API_KEY=your-azure-openai-api-key
   ```

4. **Load environment variables and run:**
   ```bash
   # Load environment variables (Linux/macOS)
   export $(cat .env | xargs)
   
   # Load environment variables (Windows PowerShell)
   Get-Content .env | ForEach-Object {
       if ($_ -match '^([^=]+)=(.*)$') {
           [Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
       }
   }
   
   # Launch the application
   uv run python -m src.gradio
   ```

5. **Access the application:**
   
   Open your browser and navigate to `http://127.0.0.1:7860`

## Usage Guide

### Basic Workflow

1. **Enter Car Description:** Provide detailed information about the vehicle
   ```
   Example: "2020 Toyota Camry, red sedan with black leather seats, 
   45,000 miles, excellent condition, new Michelin tires installed 
   in 2023, tinted windows, minor scratch on rear bumper, 
   asking $24,500"
   ```

2. **Add Recipient Email:** Enter the email address where the listing should be sent

3. **Upload Image (Optional):** Upload a car photo to enhance the listing and enable automatic body type detection

4. **Process & Send:** Click the "Process and Send" button to generate and send the email

### Input Requirements

- Car Description: Detailed text description (max 5,000 characters)
- Recipient Email: Valid email address (disposable emails blocked)
- Car Image: Optional image in JPG, JPEG, PNG, or GIF format

## Data Extraction Capabilities

AutoLister360 can extract and structure the following information:

### Basic Information
- Brand & Model: Vehicle manufacturer and model name
- Year: Manufacturing year (1900-2030)
- Color: Vehicle color
- Body Type: Sedan, SUV, Truck, etc.

### Technical Specifications
- Engine Size: Motor displacement in cubic centimeters (cc)
- Windows: Type and features (tinted, electrical, etc.)
- Tires: Brand, type, and manufacturing year

### Financial Information
- Explicit Pricing: Direct price statements
- Estimated Pricing: Inferred or approximate values
- Currency Support: USD, EGP, L.E, and others

### Additional Details
- Notices: Collision history, repairs, maintenance records
- Condition Notes: Wear, damage, or special features

## Security Features

### Input Sanitization
- Prompt Injection Protection: Detects and removes malicious instruction override attempts
- Code Injection Prevention: Blocks script and code execution attempts
- Data Extraction Protection: Prevents attempts to extract system prompts or sensitive data

### Email Security
- Email Validation: RFC-compliant email format checking
- Disposable Email Detection: Blocks known temporary email services
- SMTP Authentication: Secure email transmission with TLS encryption

## Logging & Monitoring

The application provides comprehensive logging capabilities:

- Structured Logging: Detailed logs with timestamps and log levels
- Security Monitoring: Automatic detection and logging of security threats
- Performance Tracking: Processing times and success rates
- Error Reporting: Detailed error messages for troubleshooting

Log files are stored in the `logs/` directory with timestamp-based filenames.

## Development

### Project Structure

```
autolister360/
├── src/
│   ├── config.py           # Configuration management
│   ├── text_processor.py   # LLM-powered text processing
│   ├── email_sender.py     # Email functionality
│   ├── image_classifier.py # Image classification
│   ├── utils.py           # Data models and utilities
│   ├── templates.py       # LLM prompt templates
│   └── gradio.py          # Web interface
├── config.yaml            # Application configuration
├── pyproject.toml         # Dependencies and project metadata
├── logs/                  # Application logs (auto-created)
├── temp/                  # Temporary files (auto-created)
└── .env                   # Environment variables (create manually)
```

### Key Dependencies

- **Gradio 5.42.0+:** Web interface framework
- **LangChain:** LLM integration and structured output
- **Pydantic 2.11.7+:** Data validation and serialization
- **Pillow 11.3.0+:** Image processing
- **PyYAML:** Configuration file parsing

## Troubleshooting

### Common Issues

#### SMTP Authentication Errors
```
Error: SMTP authentication failed - check username/password
```
**Solution:** Verify your email credentials and ensure app passwords are used for Gmail.

#### LLM Connection Issues
```
Error initializing LLM: ...
```
**Solution:** Check your Azure OpenAI credentials and ensure the deployment is active.

#### Image Upload Problems
```
Image file not found: ...
```
**Solution:** Ensure the uploaded image is in a supported format and not corrupted.

### Debug Mode

Enable detailed logging by updating `config.yaml`:
```yaml
logging:
  level: "DEBUG"
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Built with love using Python, AI, and modern web technologies

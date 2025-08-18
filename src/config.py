import logging
from datetime import datetime
from pathlib import Path
import yaml
import os

def load_config():
    """Load configuration from config.yaml with environment variable expansion."""
    config_path = Path("config.yaml")
    try:
        with open(config_path, 'r') as file:
            content = file.read()
            content = os.path.expandvars(content)
            return yaml.safe_load(content)
    except FileNotFoundError:
        logging.getLogger(__name__).error("config.yaml file not found")
        raise
    except yaml.YAMLError as e:
        logging.getLogger(__name__).error(f"Error parsing config.yaml: {str(e)}")
        raise

def setup_logging():
    """Configure logging to write to a single file in the logs directory."""
    # Check if logger is already configured 
    if logging.getLogger().hasHandlers():
        return

    # Load logging configuration
    config = load_config()
    log_config = config['logging']

    logs_dir = Path(log_config['directory'])
    logs_dir.mkdir(exist_ok=True)

    # Configure logging to write to a single file
    log_file = logs_dir / datetime.now().strftime(log_config['filename'])
    logging.basicConfig(
        level=getattr(logging, log_config['level']),
        format=log_config['format'],
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

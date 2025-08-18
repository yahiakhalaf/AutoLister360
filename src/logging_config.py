import logging
from datetime import datetime
from pathlib import Path

def setup_logging():
    """Configure logging to write to a single file in the logs directory."""
    # Check if logger is already configured to avoid duplicate handlers
    if logging.getLogger().hasHandlers():
        return

    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Configure logging to write to a single file
    log_file = logs_dir / f"autolister360_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

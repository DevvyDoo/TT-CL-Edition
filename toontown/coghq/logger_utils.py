# logger_utils.py
import logging
import os

# Directory for logs
log_directory = "crane-logs"
os.makedirs(log_directory, exist_ok=True)

# Log file for object states
log_file = os.path.join(log_directory, "DistributedCashbotBossObjectStates.log")

_state_logger = None  # Singleton instance

def get_state_logger():
    """Creates and returns the singleton state logger."""
    global _state_logger
    if _state_logger is None:
        # Create the logger
        _state_logger = logging.getLogger("DistributedCashbotBossObjectStatesLogger")

        # Clear any pre-existing handlers to avoid duplicates
        _state_logger.handlers.clear()

        # Use the default timestamp format for logs
        log_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

        # File handler
        file_handler = logging.FileHandler(log_file, mode='a')
        file_handler.setFormatter(log_formatter)

        # Stream handler
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(log_formatter)

        # Configure logger
        _state_logger.setLevel(logging.INFO)
        _state_logger.addHandler(file_handler)
        _state_logger.addHandler(stream_handler)

    return _state_logger

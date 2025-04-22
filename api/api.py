from application import app  # noqa: F401
import logging
from logging.handlers import RotatingFileHandler
import os

log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(log_dir, exist_ok=True)
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
file_handler = RotatingFileHandler(
    os.path.join(log_dir, "app.log"),
    maxBytes=10 * 1024 * 1024,  # 10 MB
    backupCount=5,
    encoding="utf-8",
)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
root_logger.addHandler(file_handler)
warning_file_handler = RotatingFileHandler(
    os.path.join(log_dir, "warnings.log"),
    maxBytes=5 * 1024 * 1024,  # 5 MB
    backupCount=3,
    encoding="utf-8",
)
warning_file_handler.setLevel(logging.WARNING)
warning_file_handler.setFormatter(formatter)
root_logger.addHandler(warning_file_handler)
logging.info("API Server is starting up with configured logging (file only)")

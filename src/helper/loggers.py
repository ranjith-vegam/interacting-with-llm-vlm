from log_manager import get_logger
from src.config import get_config

conf = get_config()

startup_sequence_logger = get_logger(
    logger_name="startup_sequence_logger",
    log_level=conf.server.log_level,
    environment=conf.environment     
)

text_model_logger = get_logger(
    logger_name="text_model_logger",
    log_level=conf.server.log_level,
    environment=conf.environment     
)

image_model_logger = get_logger(
    logger_name="image_model_logger",
    log_level=conf.server.log_level,
    environment=conf.environment     
)
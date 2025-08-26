from loguru import logger
import sys

def setup_logging():
    """Configure Loguru logging for the tax calculator application"""

    # Remove default handler
    logger.remove()


    # Console handler with nice formatting
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO",
        colorize=True
    )

    logger.info("Logging system initialized")

# Initialize logging when module is imported
setup_logging()
